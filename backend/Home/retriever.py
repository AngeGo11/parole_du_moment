"""Service de récupération des versets depuis MongoDB."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
import numpy as np

from .schemas import AnalysisResult
from .version_mapping import get_translation_id_from_version_name
from .embeddings import get_embedding_service


logger = logging.getLogger(__name__)

load_dotenv()


@dataclass
class VerseDocument:
    """Représentation typée d'un verset extrait de MongoDB."""

    id: ObjectId
    text: str
    reference: str
    keywords: List[str]
    translation: Optional[str]
    book: Optional[str]
    chapter: Optional[int]
    verse: Optional[int]


class MongoVerseRetriever:
    """Accès MongoDB pour récupérer les versets pertinents."""

    def __init__(self) -> None:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGODB_DATABASE", "parole_du_moment_db")

        logger.info(f"🔌 Connexion à MongoDB: {mongo_url}")
        logger.info(f"📚 Base de données: {mongo_db}")
        
        try:
            # Créer le client avec un timeout de connexion
            self._client = AsyncIOMotorClient(
                mongo_url,
                serverSelectionTimeoutMS=5000  # Timeout de 5 secondes
            )
            self._db = self._client[mongo_db]
            logger.info("✅ Client MongoDB créé")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion à MongoDB: {e}")
            raise
        
        # Cache pour les noms d'émotions/thèmes (chargé dynamiquement)
        self._emotions_cache: Optional[List[dict]] = None
        self._themes_cache: Optional[List[dict]] = None
        
        # Service d'embeddings (chargé de manière paresseuse)
        self._embedding_service = None

    @property
    def verses(self) -> AsyncIOMotorCollection:
        return self._db["versets"]

    @property
    def emotions(self) -> AsyncIOMotorCollection:
        return self._db["emotions"]

    @property
    def themes(self) -> AsyncIOMotorCollection:
        return self._db["themes"]

    @property
    def verses_emotions(self) -> AsyncIOMotorCollection:
        return self._db["versets_emotions"]

    @property
    def verses_themes(self) -> AsyncIOMotorCollection:
        return self._db["versets_themes"]

    @staticmethod
    def _get_default_translation_id(language: str) -> str:
        """Retourne la traduction par défaut selon la langue."""
        language_lower = language.lower()
        default_translations = {
            "fr": "lsg",  # Louis Segond (fr_apee.json -> LSG -> lsg)
            "en": "kjv",  # King James Version
            "es": "rvr",  # Reina Valera
            "de": "schlachter",
            "pt": "nvi",
            "ru": "synodal",
            "zh": "cuv",
            "ar": "svd",
            "ko": "ko",
            "vi": "vietnamese",
            "fi": "finnish",
            "ro": "cornilescu",
            "el": "greek",
            "eo": "esperanto",
        }
        return default_translations.get(language_lower, "lsg")  # Par défaut français

    @staticmethod
    def _normalize_translation_id(translation_id: Optional[str], language: str, version_name: Optional[str] = None) -> str:
        """Normalise le translation_id (convertit en lowercase, gère les valeurs par défaut)."""
        if translation_id:
            return translation_id.lower().strip()
        
        # Si version_name est fourni, essayer de le convertir
        if version_name:
            mapped_id = get_translation_id_from_version_name(version_name)
            if mapped_id:
                return mapped_id.lower().strip()
        
        # Si pas fourni, utiliser la traduction par défaut selon la langue
        return MongoVerseRetriever._get_default_translation_id(language)

    async def get_best_verse(self, analysis: AnalysisResult, translation_id: Optional[str] = None, language: str = "fr", version_name: Optional[str] = None, user_text: Optional[str] = None) -> Optional[VerseDocument]:
        """
        Retourne le verset le plus pertinent selon l'analyse fournie.
        Utilise la recherche vectorielle (embeddings) en priorité, puis combine avec les autres méthodes.
        
        Args:
            analysis: Résultat de l'analyse du texte utilisateur
            translation_id: ID de traduction biblique
            language: Langue de l'utilisateur
            version_name: Nom de la version biblique
            user_text: Texte original de l'utilisateur (pour recherche vectorielle)
        """
        
        # Normaliser le translation_id
        normalized_translation_id = self._normalize_translation_id(translation_id, language, version_name)
        logger.info(f"🔍 Recherche de verset avec analysis: emotions={analysis.emotions}, themes={analysis.themes}, keywords={analysis.keywords}")
        logger.info(f"📖 Filtre traduction: {normalized_translation_id}")

        # Construire le texte de requête pour la recherche vectorielle
        query_text = user_text or analysis.summary or " ".join(analysis.keywords)
        
        # STRATÉGIE 0: Recherche vectorielle (prioritaire)
        vector_results = await self._vector_search(query_text, normalized_translation_id, top_k=20)
        
        # Calculer les IDs des versets liés aux émotions/thèmes pour score hybride
        verse_ids: List[ObjectId] = []

        try:
            emotion_ids = await self._find_ids_by_name(self.emotions, analysis.emotions, "emotions")
            logger.info(f"📊 Emotions trouvées: {len(emotion_ids)} IDs (recherche: {analysis.emotions})")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la recherche d'émotions: {e}")
            emotion_ids = []

        try:
            theme_ids = await self._find_ids_by_name(self.themes, analysis.themes, "themes")
            logger.info(f"📊 Thèmes trouvés: {len(theme_ids)} IDs (recherche: {analysis.themes})")
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la recherche de thèmes: {e}")
            theme_ids = []

        if emotion_ids:
            linked_verse_ids = await self._find_verse_ids_by_link(
                self.verses_emotions, "emotion_id", emotion_ids
            )
            logger.info(f"📖 Versets liés aux émotions: {len(linked_verse_ids)}")
            verse_ids.extend(linked_verse_ids)

        if theme_ids:
            linked_verse_ids = await self._find_verse_ids_by_link(
                self.verses_themes, "theme_id", theme_ids
            )
            logger.info(f"📖 Versets liés aux thèmes: {len(linked_verse_ids)}")
            verse_ids.extend(linked_verse_ids)

        verse_ids = list(dict.fromkeys(verse_ids))
        logger.info(f"📚 Total de versets uniques par émotions/thèmes: {len(verse_ids)}")

        # Si on a des résultats vectoriels, les combiner avec les scores d'émotions/thèmes
        if vector_results:
            logger.info(f"✅ Recherche vectorielle: {len(vector_results)} versets trouvés")
            # Combiner les scores vectoriels avec les correspondances émotions/thèmes
            scored_results = self._combine_scores(vector_results, verse_ids, analysis)
            if scored_results:
                best_result = scored_results[0]
                logger.info(f"✅ Verset sélectionné (recherche vectorielle): {best_result.get('ref_unique', 'N/A')}")
                return VerseDocument(
                    id=best_result.get("_id"),
                    text=best_result.get("contenu", ""),
                    reference=best_result.get("ref_unique", "Référence inconnue"),
                    keywords=list(best_result.get("mots_cles", [])),
                    translation=best_result.get("traduction_id"),
                    book=best_result.get("livre_id"),
                    chapter=best_result.get("chapitre"),
                    verse=best_result.get("numero"),
                )

        # Fallback: utiliser les stratégies existantes si la recherche vectorielle échoue
        search_terms = self._build_search_terms(analysis)
        logger.info(f"🔎 Termes de recherche (fallback): {search_terms}")
        
        projection = {
            "contenu": 1,
            "ref_unique": 1,
            "mots_cles": 1,
            "traduction_id": 1,
            "livre_id": 1,
            "chapitre": 1,
            "numero": 1,
        }

        results: List[dict] = []
        
        # Filtre de traduction à ajouter à toutes les requêtes
        translation_filter = {"traduction_id": normalized_translation_id}

        # Stratégie 1: Recherche par verse_ids ET recherche textuelle (si disponible)
        if verse_ids and search_terms:
            try:
                query = {
                    "_id": {"$in": verse_ids}, 
                    "$text": {"$search": " ".join(search_terms)},
                    **translation_filter
                }
                projection_with_score = projection.copy()
                projection_with_score["score"] = {"$meta": "textScore"}
                cursor = self.verses.find(query, projection_with_score)
                cursor = cursor.sort([("score", {"$meta": "textScore"})])
                results = await cursor.to_list(length=10)
                logger.info(f"✅ Trouvé {len(results)} versets avec recherche textuelle + verse_ids (traduction: {normalized_translation_id})")
            except Exception as exc:
                logger.warning("Recherche textuelle indisponible, utilisation de regex: %s", exc)

        # Stratégie 2: Recherche par verse_ids uniquement (sans texte)
        if not results and verse_ids:
            query = {"_id": {"$in": verse_ids}, **translation_filter}
            cursor = self.verses.find(query, projection)
            cursor = cursor.limit(10)
            results = await cursor.to_list(length=10)
            logger.info(f"✅ Trouvé {len(results)} versets par verse_ids uniquement (traduction: {normalized_translation_id})")

        # Stratégie 3: Recherche regex dans contenu ET mots_cles pour les termes de recherche
        if not results and search_terms:
            logger.info("🔍 Tentative de recherche regex dans contenu et mots-clés...")
            # Créer une regex flexible qui cherche dans le contenu ET les mots-clés
            regex_pattern = "|".join(map(re.escape, search_terms))
            regex = re.compile(regex_pattern, re.IGNORECASE)
            
            # Recherche dans le contenu
            query_content = {"contenu": regex, **translation_filter}
            if verse_ids:
                query_content["_id"] = {"$in": verse_ids}
            
            cursor = self.verses.find(query_content, projection).limit(10)
            results = await cursor.to_list(length=10)
            logger.info(f"✅ Trouvé {len(results)} versets avec recherche regex dans contenu (traduction: {normalized_translation_id})")
            
            # Si pas assez de résultats, chercher aussi dans les mots-clés
            if len(results) < 5:
                query_keywords = {
                    "mots_cles": {"$in": [term.lower() for term in search_terms]},
                    **translation_filter
                }
                if verse_ids:
                    query_keywords["_id"] = {"$in": verse_ids}
                
                cursor_keywords = self.verses.find(query_keywords, projection).limit(10)
                results_keywords = await cursor_keywords.to_list(length=10)
                
                # Combiner les résultats sans doublons
                existing_ids = {r["_id"] for r in results}
                for r in results_keywords:
                    if r["_id"] not in existing_ids:
                        results.append(r)
                        existing_ids.add(r["_id"])
                        if len(results) >= 10:
                            break
                
                logger.info(f"✅ Trouvé {len(results)} versets au total (contenu + mots-clés, traduction: {normalized_translation_id})")

        # Stratégie 4: Recherche flexible avec au moins un terme
        if not results and search_terms:
            logger.info("🔍 Recherche flexible avec au moins un terme...")
            # Chercher au moins un des termes dans le contenu
            or_conditions = [{"contenu": re.compile(re.escape(term), re.IGNORECASE)} for term in search_terms[:3]]
            query_flexible = {"$or": or_conditions, **translation_filter}
            
            cursor = self.verses.find(query_flexible, projection).limit(10)
            results = await cursor.to_list(length=10)
            logger.info(f"✅ Trouvé {len(results)} versets avec recherche flexible (traduction: {normalized_translation_id})")

        # Stratégie 5: Dernier recours - verset aléatoire de la traduction choisie (à éviter si possible)
        if not results:
            logger.warning(f"⚠️ Aucun verset trouvé avec les critères, utilisation d'un verset aléatoire (traduction: {normalized_translation_id})...")
            sample_projection = projection.copy()
            sample_projection.pop("score", None)
            sample = self.verses.aggregate([
                {"$match": translation_filter},
                {"$sample": {"size": 1}},
                {"$project": sample_projection},
            ])
            results = await sample.to_list(length=1)

        if not results:
            return None

        # Sélectionner le meilleur verset parmi les résultats
        best = self._select_best_verse(results, search_terms)
        logger.info(f"✅ Verset sélectionné: {best.get('ref_unique', 'N/A')}")
        
        return VerseDocument(
            id=best.get("_id"),
            text=best.get("contenu", ""),
            reference=best.get("ref_unique", "Référence inconnue"),
            keywords=list(best.get("mots_cles", [])),
            translation=best.get("traduction_id"),
            book=best.get("livre_id"),
            chapter=best.get("chapitre"),
            verse=best.get("numero"),
        )

    async def _vector_search(self, query_text: str, translation_id: str, top_k: int = 20) -> List[dict]:
        """
        Recherche vectorielle des versets les plus pertinents.
        
        Args:
            query_text: Texte de la requête utilisateur
            translation_id: ID de traduction pour filtrer
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de dictionnaires contenant les versets avec leur score de similarité
        """
        try:
            # Charger le service d'embeddings de manière paresseuse
            if self._embedding_service is None:
                self._embedding_service = get_embedding_service()
            
            # Générer l'embedding de la requête
            query_embedding = self._embedding_service.encode(query_text)
            
            # Récupérer tous les versets de la traduction avec leurs embeddings
            # Note: Les embeddings doivent être pré-calculés et stockés dans MongoDB
            cursor = self.verses.find(
                {"traduction_id": translation_id, "embedding": {"$exists": True}},
                {
                    "contenu": 1,
                    "ref_unique": 1,
                    "mots_cles": 1,
                    "traduction_id": 1,
                    "livre_id": 1,
                    "chapitre": 1,
                    "numero": 1,
                    "embedding": 1,
                }
            )
            
            all_verses = await cursor.to_list(length=None)
            
            if not all_verses:
                logger.warning("⚠️ Aucun verset avec embedding trouvé. Exécutez le script de pré-calcul des embeddings.")
                return []
            
            # Extraire les embeddings et calculer les similarités
            verse_embeddings = []
            verse_data = []
            
            for verse in all_verses:
                embedding = verse.get("embedding")
                if embedding is not None:
                    # Convertir la liste MongoDB en numpy array
                    embedding_array = np.array(embedding)
                    verse_embeddings.append(embedding_array)
                    # Retirer l'embedding du dict pour économiser la mémoire
                    verse_without_embedding = {k: v for k, v in verse.items() if k != "embedding"}
                    verse_data.append(verse_without_embedding)
            
            if not verse_embeddings:
                logger.warning("⚠️ Aucun embedding valide trouvé dans les versets.")
                return []
            
            # Trouver les versets les plus similaires
            similar_indices = self._embedding_service.find_most_similar(
                query_embedding[0],  # Prendre le premier (et seul) embedding de la requête
                verse_embeddings,
                top_k=top_k
            )
            
            # Construire les résultats avec les scores
            results = []
            for idx, score in similar_indices:
                verse_result = verse_data[idx].copy()
                verse_result["vector_score"] = score
                results.append(verse_result)
            
            logger.info(f"✅ Recherche vectorielle: {len(results)} versets trouvés (score max: {results[0]['vector_score']:.3f})")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche vectorielle: {e}")
            logger.exception("Détails de l'erreur:")
            return []

    def _combine_scores(self, vector_results: List[dict], verse_ids: List[ObjectId], analysis: AnalysisResult) -> List[dict]:
        """
        Combine les scores vectoriels avec les correspondances émotions/thèmes.
        
        Score final = score_vectoriel * 0.7 + score_emotions_themes * 0.3
        
        Args:
            vector_results: Résultats de la recherche vectorielle avec scores
            verse_ids: IDs des versets liés aux émotions/thèmes
            analysis: Analyse du texte utilisateur
            
        Returns:
            Liste de résultats triés par score combiné décroissant
        """
        verse_ids_set = set(verse_ids)
        search_terms_lower = [term.lower() for term in analysis.keywords]
        
        scored_results = []
        
        for verse in vector_results:
            verse_id = verse.get("_id")
            vector_score = verse.get("vector_score", 0.0)
            
            # Score pour correspondance émotions/thèmes (0.0 à 1.0)
            emotion_theme_score = 1.0 if verse_id in verse_ids_set else 0.0
            
            # Score pour correspondance avec mots-clés dans le contenu
            contenu = verse.get("contenu", "").lower()
            keyword_matches = sum(1 for term in search_terms_lower if term in contenu)
            keyword_score = min(keyword_matches / max(len(search_terms_lower), 1), 1.0)
            
            # Score combiné émotions/thèmes + mots-clés
            semantic_score = (emotion_theme_score * 0.6 + keyword_score * 0.4)
            
            # Score final: 70% vectoriel + 30% sémantique
            final_score = vector_score * 0.7 + semantic_score * 0.3
            
            verse["combined_score"] = final_score
            verse["vector_score"] = vector_score
            verse["semantic_score"] = semantic_score
            scored_results.append(verse)
        
        # Trier par score combiné décroissant
        scored_results.sort(key=lambda x: x.get("combined_score", 0.0), reverse=True)
        
        logger.info(f"📊 Scores combinés calculés pour {len(scored_results)} versets")
        if scored_results:
            logger.info(f"   Meilleur score: {scored_results[0].get('combined_score', 0.0):.3f} "
                       f"(vectoriel: {scored_results[0].get('vector_score', 0.0):.3f}, "
                       f"sémantique: {scored_results[0].get('semantic_score', 0.0):.3f})")
        
        return scored_results

    @staticmethod
    def _select_best_verse(results: List[dict], search_terms: List[str]) -> dict:
        """Sélectionne le meilleur verset basé sur la pertinence avec les termes de recherche."""
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        # Si plusieurs résultats, choisir celui qui correspond le mieux
        best_score = -1
        best_verse = results[0]
        
        search_terms_lower = [term.lower() for term in search_terms]
        
        for verse in results:
            score = 0
            contenu = verse.get("contenu", "").lower()
            mots_cles = [kw.lower() if isinstance(kw, str) else str(kw).lower() for kw in verse.get("mots_cles", [])]
            
            # Bonus pour chaque terme trouvé dans le contenu (score plus élevé pour les mots complets)
            for term in search_terms_lower:
                # Recherche du mot complet (avec limites de mot)
                word_pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                matches = word_pattern.findall(contenu)
                score += len(matches) * 2  # Bonus pour correspondance exacte de mot
            
                # Recherche partielle (moins de points)
                if term in contenu:
                    score += 1
            
            # Bonus supplémentaire pour les mots-clés correspondants (plus pertinents)
            for term in search_terms_lower:
                for mot_cle in mots_cles:
                    if term in mot_cle or mot_cle in term:
                        score += 3  # Les mots-clés sont très pertinents
            
            # Bonus pour les versets courts (plus impactants)
            longueur = len(contenu)
            if longueur < 100:
                score += 1
            elif longueur > 300:
                score -= 1  # Pénalité pour les versets très longs
            
            if score > best_score:
                best_score = score
                best_verse = verse
        
        logger.info(f"🎯 Verset sélectionné avec score: {best_score}")
        return best_verse

    async def _load_collection_cache(self, collection_name: Optional[str]) -> List[dict]:
        """Charge et cache les données d'une collection pour matching intelligent."""
        if collection_name == "emotions":
            if self._emotions_cache is None:
                cursor = self.emotions.find({}, {"_id": 1, "nom": 1, "description": 1})
                self._emotions_cache = await cursor.to_list(length=200)
                logger.info(f"📚 Cache émotions chargé: {len(self._emotions_cache)} éléments")
            return self._emotions_cache or []
        elif collection_name == "themes":
            if self._themes_cache is None:
                cursor = self.themes.find({}, {"_id": 1, "nom": 1, "description": 1})
                self._themes_cache = await cursor.to_list(length=200)
                logger.info(f"📚 Cache thèmes chargé: {len(self._themes_cache)} éléments")
            return self._themes_cache or []
        return []

    @staticmethod
    def _calculate_similarity(term: str, target: str) -> float:
        """Calcule une similarité simple entre deux termes."""
        term_lower = term.lower().strip()
        target_lower = target.lower().strip()
        
        # Correspondance exacte
        if term_lower == target_lower:
            return 1.0
        
        # Correspondance partielle (le terme est dans la cible)
        if term_lower in target_lower:
            return 0.8
        
        # Correspondance inverse (la cible est dans le terme)
        if target_lower in term_lower:
            return 0.7
        
        # Correspondance de mots significatifs
        term_words = set(w for w in term_lower.split() if len(w) > 2)
        target_words = set(w for w in target_lower.split() if len(w) > 2)
        
        if term_words and target_words:
            common_words = term_words & target_words
            if common_words:
                # Score basé sur le ratio de mots communs
                similarity = len(common_words) / max(len(term_words), len(target_words))
                return min(similarity, 0.6)
        
        return 0.0

    async def _find_ids_by_name(
        self, collection: AsyncIOMotorCollection, names: Iterable[str], collection_name: str
    ) -> List[ObjectId]:
        """Recherche dynamique d'IDs par matching intelligent sans mapping codé en dur."""
        if not names:
            return []
        
        found_ids: List[ObjectId] = []
        
        # Charger le cache des éléments disponibles
        cached_items = await self._load_collection_cache(collection_name)
        
        for name in names:
            if not name:
                continue
            
            name_lower = name.lower().strip()
            ids_for_this_name: List[ObjectId] = []
            
            # Stratégie 1: Matching intelligent avec le cache
            if cached_items:
                matches = []
                for item in cached_items:
                    nom = item.get("nom", "")
                    description = item.get("description", "")
                    
                    # Calculer la similarité avec le nom
                    nom_similarity = self._calculate_similarity(name_lower, nom.lower())
                    
                    # Calculer la similarité avec la description
                    desc_similarity = 0.0
                    if description:
                        desc_similarity = self._calculate_similarity(name_lower, description.lower())
                    
                    # Score combiné (le nom a plus de poids)
                    total_score = max(nom_similarity, desc_similarity * 0.7)
                    
                    if total_score > 0.4:  # Seuil de similarité
                        matches.append((item["_id"], total_score, nom))
                
                # Trier par score décroissant et prendre les meilleurs matches
                matches.sort(key=lambda x: x[1], reverse=True)
                ids_for_this_name.extend([match[0] for match in matches[:5]])  # Top 5 matches
                
                if ids_for_this_name:
                    matched_names = [m[2] for m in matches[:len(ids_for_this_name)]]
                    logger.info(f"✅ Matching intelligent pour '{name}': {matched_names}")
            
            # Stratégie 2: Recherche MongoDB traditionnelle (fallback)
            if not ids_for_this_name:
                # Extraire les mots significatifs
                words_in_name = name_lower.split()
                stop_words = {"de", "du", "des", "la", "le", "les", "et", "ou", "dieu", "christ"}
                significant_words = [w for w in words_in_name if w not in stop_words and len(w) > 2]
                
                # Recherche exacte
                try:
                    exact_filter = {"nom": {"$regex": f"^{re.escape(name_lower)}$", "$options": "i"}}
                    cursor = collection.find(exact_filter, {"_id": 1})
                    docs = await cursor.to_list(length=5)
                    ids_for_this_name.extend([doc["_id"] for doc in docs if doc.get("_id")])
                except Exception:
                    pass
                
                # Recherche partielle dans le nom
                if not ids_for_this_name:
                    try:
                        filters = []
                        filters.append({"nom": {"$regex": re.escape(name_lower), "$options": "i"}})
                        # Ajouter aussi les mots significatifs
                        for word in significant_words:
                            filters.append({"nom": {"$regex": re.escape(word), "$options": "i"}})
                        
                        cursor = collection.find({"$or": filters}, {"_id": 1})
                        docs = await cursor.to_list(length=5)
                        ids_for_this_name.extend([doc["_id"] for doc in docs if doc.get("_id")])
                    except Exception:
                        pass
                
                # Recherche dans la description
                if not ids_for_this_name:
                    try:
                        filters = [{"description": {"$regex": re.escape(name_lower), "$options": "i"}}]
                        for word in significant_words:
                            filters.append({"description": {"$regex": re.escape(word), "$options": "i"}})
                        
                        cursor = collection.find({"$or": filters}, {"_id": 1})
                        docs = await cursor.to_list(length=5)
                        ids_for_this_name.extend([doc["_id"] for doc in docs if doc.get("_id")])
                    except Exception:
                        pass
            
            found_ids.extend(ids_for_this_name)
        
        # Retirer les doublons
        return list(dict.fromkeys(found_ids))

    async def _find_verse_ids_by_link(
        self,
        collection: AsyncIOMotorCollection,
        field_name: str,
        ids: Iterable[ObjectId],
    ) -> List[ObjectId]:
        pipeline = [
            {"$match": {field_name: {"$in": list(ids)}}},
            {
                "$group": {
                    "_id": "$verset_id",
                    "score": {"$sum": "$poids_ia"},
                }
            },
            {"$sort": {"score": -1}},
            {"$limit": 20},
        ]

        docs = await collection.aggregate(pipeline).to_list(length=20)
        return [doc["_id"] for doc in docs if doc.get("_id")]

    @staticmethod
    def _build_search_terms(analysis: AnalysisResult) -> List[str]:
        terms = list(dict.fromkeys(analysis.keywords + analysis.emotions + analysis.themes))
        return [term for term in terms if term]


