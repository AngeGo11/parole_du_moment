"""Service MongoDB pour la gestion des profils utilisateur."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from .schemas import ProfilePreferences, ProfileStats

logger = logging.getLogger(__name__)

load_dotenv()

# Mapping des codes langue vers les noms affichés
LANGUAGE_NAMES = {
    "fr": "Français",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
    "zh": "中文",
    "ar": "العربية",
    "ko": "한국어",
    "vi": "Tiếng Việt",
    "fi": "Suomi",
    "ro": "Română",
    "el": "Ελληνικά",
    "eo": "Esperanto",
}


class ProfileService:
    """Service pour gérer les profils utilisateur dans MongoDB."""

    def __init__(self) -> None:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGODB_DATABASE", "parole_du_moment_db")

        logger.info(f"🔌 Connexion ProfileService à MongoDB: {mongo_url}")
        logger.info(f"📚 Base de données: {mongo_db}")

        try:
            self._client = AsyncIOMotorClient(
                mongo_url,
                serverSelectionTimeoutMS=5000,
            )
            self._db = self._client[mongo_db]
            logger.info("✅ Client MongoDB créé pour ProfileService")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion MongoDB: {e}")
            raise

    @property
    def profiles(self) -> AsyncIOMotorCollection:
        """Collection des profils utilisateur."""
        return self._db["profiles"]

    @property
    def traductions(self) -> AsyncIOMotorCollection:
        """Collection des traductions bibliques."""
        return self._db["traductions"]

    @property
    def verse_history(self) -> AsyncIOMotorCollection:
        """Collection de l'historique des versets lus."""
        return self._db["verse_history"]

    @property
    def favorite_verses(self) -> AsyncIOMotorCollection:
        """Collection des versets favoris."""
        return self._db["favorite_verses"]

    async def get_or_create_profile(self, user_id: str) -> dict:
        """
        Récupère le profil utilisateur ou le crée avec des valeurs par défaut.

        Args:
            user_id: Identifiant Firebase de l'utilisateur

        Returns:
            Document du profil MongoDB
        """
        profile = await self.profiles.find_one({"user_id": user_id})

        if profile is None:
            # Créer un profil par défaut
            default_preferences = ProfilePreferences().dict()
            now = datetime.utcnow()

            profile_doc = {
                "user_id": user_id,
                "preferences": default_preferences,
                "created_at": now,
                "updated_at": now,
            }

            result = await self.profiles.insert_one(profile_doc)
            logger.info(f"✅ Profil créé pour user_id: {user_id}")

            # Récupérer le profil créé
            profile = await self.profiles.find_one({"_id": result.inserted_id})

        return profile

    async def update_profile(
        self, user_id: str, update_data: dict
    ) -> Optional[dict]:
        """
        Met à jour le profil utilisateur.

        Args:
            user_id: Identifiant Firebase de l'utilisateur
            update_data: Données à mettre à jour (format MongoDB $set)

        Returns:
            Profil mis à jour ou None si non trouvé
        """
        # Vérifier que la traduction existe si translation_id est fourni
        if "preferences.translation_id" in update_data:
            translation_id = update_data["preferences.translation_id"]
            translation = await self.traductions.find_one(
                {"abreviation": translation_id.lower()}
            )
            if translation is None:
                logger.warning(
                    f"⚠️ Traduction '{translation_id}' non trouvée, utilisation de la valeur par défaut"
                )
                # Utiliser la traduction par défaut selon la langue
                language = update_data.get("preferences.language", "fr")
                default_translation = await self._get_default_translation_id(language)
                update_data["preferences.translation_id"] = default_translation

        update_data["updated_at"] = datetime.utcnow()

        result = await self.profiles.find_one_and_update(
            {"user_id": user_id},
            {"$set": update_data},
            return_document=True,
        )

        if result:
            logger.info(f"✅ Profil mis à jour pour user_id: {user_id}")
        else:
            logger.warning(f"⚠️ Profil non trouvé pour user_id: {user_id}")

        return result

    async def calculate_stats(self, user_id: str) -> ProfileStats:
        """
        Calcule les statistiques de l'utilisateur.

        Args:
            user_id: Identifiant Firebase de l'utilisateur

        Returns:
            Statistiques utilisateur
        """
        try:
            # Compter les versets lus
            verses_read = await self.verse_history.count_documents({"user_id": user_id})

            # Compter les favoris
            favorites = await self.favorite_verses.count_documents({"user_id": user_id})

            # Calculer les jours consécutifs
            consecutive_days = await self._calculate_consecutive_days(user_id)

            return ProfileStats(
                verses_read=verses_read,
                favorites=favorites,
                consecutive_days=consecutive_days,
            )
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors du calcul des stats: {e}")
            # Retourner des stats à zéro si les collections n'existent pas encore
            return ProfileStats()

    async def _calculate_consecutive_days(self, user_id: str) -> int:
        """
        Calcule le nombre de jours consécutifs de lecture.

        Args:
            user_id: Identifiant Firebase de l'utilisateur

        Returns:
            Nombre de jours consécutifs
        """
        try:
            # Récupérer toutes les dates de lecture uniques
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$date",
                            }
                        }
                    }
                },
                {"$sort": {"_id": -1}},
            ]

            dates = []
            async for doc in self.verse_history.aggregate(pipeline):
                date_str = doc["_id"]
                dates.append(datetime.strptime(date_str, "%Y-%m-%d").date())

            if not dates:
                return 0

            # Trier les dates (plus récente en premier)
            dates.sort(reverse=True)

            # Calculer les jours consécutifs depuis aujourd'hui
            today = datetime.utcnow().date()
            consecutive = 0

            # Si la date la plus récente n'est pas aujourd'hui ou hier, pas de streak
            if dates[0] < today - timedelta(days=1):
                return 0

            # Compter les jours consécutifs
            expected_date = today
            for date in dates:
                if date == expected_date or date == expected_date - timedelta(days=1):
                    consecutive += 1
                    expected_date = date - timedelta(days=1)
                else:
                    break

            return consecutive
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul jours consécutifs: {e}")
            return 0

    async def get_languages(self) -> list[dict]:
        """
        Récupère toutes les langues disponibles depuis la collection traductions.

        Returns:
            Liste des langues avec code et nom
        """
        try:
            # Récupérer les langues distinctes
            languages = await self.traductions.distinct("langue")

            # Créer la liste avec codes et noms
            result = []
            for lang_code in sorted(set(languages)):
                if lang_code:
                    name = LANGUAGE_NAMES.get(lang_code, lang_code.capitalize())
                    result.append({"code": lang_code, "name": name})

            logger.info(f"✅ {len(result)} langues récupérées")
            return result
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des langues: {e}")
            # Retourner les langues par défaut si erreur
            return [
                {"code": "fr", "name": "Français"},
                {"code": "en", "name": "English"},
            ]

    async def get_bible_versions(self, language: Optional[str] = None) -> list[dict]:
        """
        Récupère les versions bibliques disponibles, optionnellement filtrées par langue.

        Args:
            language: Code langue pour filtrer (ex: "fr")

        Returns:
            Liste des versions bibliques
        """
        try:
            query = {}
            if language:
                query["langue"] = language.lower()

            cursor = self.traductions.find(query).sort("nom", 1)
            versions = []

            async for doc in cursor:
                versions.append(
                    {
                        "id": doc.get("abreviation", "").lower(),
                        "name": doc.get("nom", ""),
                        "abreviation": doc.get("abreviation", ""),
                    }
                )

            logger.info(
                f"✅ {len(versions)} versions bibliques récupérées"
                + (f" pour langue '{language}'" if language else "")
            )
            return versions
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des versions: {e}")
            return []

    async def _get_default_translation_id(self, language: str) -> str:
        """
        Retourne la traduction par défaut selon la langue.

        Args:
            language: Code langue

        Returns:
            ID de traduction par défaut
        """
        language_lower = language.lower()
        default_translations = {
            "fr": "lsg",
            "en": "kjv",
            "es": "rvr",
            "de": "sch",
            "pt": "nvi",
            "ru": "syn",
            "zh": "cuv",
            "ar": "svd",
            "ko": "ko",
            "vi": "vi",
            "fi": "fi",
            "ro": "ro",
            "el": "gr",
            "eo": "eo",
        }
        return default_translations.get(language_lower, "lsg")

