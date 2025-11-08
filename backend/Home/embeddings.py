"""Module pour la gestion des embeddings vectoriels des versets."""

from __future__ import annotations

import logging
import os
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Modèle multilingue recommandé pour le français
# paraphrase-multilingual-MiniLM-L12-v2 : bon équilibre qualité/vitesse, multilingue
# all-MiniLM-L6-v2 : plus rapide mais moins bon pour le français
DEFAULT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    """Service pour générer et comparer les embeddings de texte."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        """
        Initialise le service d'embeddings.
        
        Args:
            model_name: Nom du modèle sentence-transformers à utiliser.
                       Par défaut: paraphrase-multilingual-MiniLM-L12-v2
        """
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
        self._model: Optional[SentenceTransformer] = None
        logger.info(f"🔧 Initialisation du service d'embeddings avec le modèle: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """Charge le modèle de manière paresseuse (lazy loading)."""
        if self._model is None:
            try:
                logger.info(f"📥 Chargement du modèle d'embeddings: {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"✅ Modèle d'embeddings chargé avec succès")
                logger.info(f"   Dimension des embeddings: {self._model.get_sentence_embedding_dimension()}")
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement du modèle d'embeddings: {e}")
                raise
        return self._model

    def encode(self, texts: str | List[str], normalize: bool = True) -> np.ndarray:
        """
        Génère les embeddings pour un ou plusieurs textes.
        
        Args:
            texts: Texte unique ou liste de textes à encoder
            normalize: Si True, normalise les vecteurs (utile pour la similarité cosinus)
            
        Returns:
            Array numpy de shape (1, dim) pour un texte ou (n, dim) pour plusieurs textes
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embeddings
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'encodage: {e}")
            raise

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings.
        
        Args:
            embedding1: Premier vecteur d'embedding
            embedding2: Deuxième vecteur d'embedding
            
        Returns:
            Score de similarité entre 0 et 1 (1 = identique, 0 = différent)
        """
        # Similarité cosinus (produit scalaire si les vecteurs sont normalisés)
        similarity = np.dot(embedding1, embedding2)
        return float(similarity)

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        verse_embeddings: List[np.ndarray],
        top_k: int = 10,
    ) -> List[tuple[int, float]]:
        """
        Trouve les versets les plus similaires à la requête.
        
        Args:
            query_embedding: Embedding de la requête utilisateur
            verse_embeddings: Liste des embeddings des versets
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de tuples (index, score_similarité) triés par score décroissant
        """
        if not verse_embeddings:
            return []

        # Convertir en array numpy pour calcul vectoriel efficace
        verse_array = np.array(verse_embeddings)
        
        # Calculer les similarités (produit scalaire car vecteurs normalisés)
        similarities = np.dot(verse_array, query_embedding)
        
        # Obtenir les indices des top_k meilleurs résultats
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Retourner les résultats avec leurs scores
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]
        return results

    def get_embedding_dimension(self) -> int:
        """Retourne la dimension des embeddings générés par le modèle."""
        return self.model.get_sentence_embedding_dimension()


# Instance globale (singleton) pour éviter de recharger le modèle
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Retourne l'instance globale du service d'embeddings (singleton)."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

