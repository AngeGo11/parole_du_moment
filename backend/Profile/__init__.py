"""Routes FastAPI pour la gestion des profils utilisateur."""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from .schemas import (
    BibleVersionsResponse,
    LanguageItem,
    LanguagesResponse,
    ProfileResponse,
    ProfileStats,
    ProfileUpdateRequest,
)
from .service import ProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Initialisation lazy du service
_service: ProfileService | None = None


def get_service() -> ProfileService:
    """Retourne l'instance de ProfileService (initialisation lazy)."""
    global _service
    if _service is None:
        try:
            _service = ProfileService()
            logger.info("✅ ProfileService initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de ProfileService: {e}")
            raise
    return _service


@router.get("/languages", response_model=LanguagesResponse)
async def get_languages() -> LanguagesResponse:
    """
    Récupère toutes les langues disponibles depuis la collection traductions.

    Returns:
        Liste des langues avec code et nom
    """
    try:
        service = get_service()
        languages_data = await service.get_languages()

        languages = [
            LanguageItem(code=lang["code"], name=lang["name"])
            for lang in languages_data
        ]

        return LanguagesResponse(languages=languages)
    except Exception as e:
        logger.exception("❌ Erreur lors de la récupération des langues")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la récupération des langues: {str(e)}"
        ) from e


@router.get("/bible-versions", response_model=BibleVersionsResponse)
async def get_bible_versions(
    language: str | None = Query(
        default=None, description="Code langue pour filtrer les versions (ex: fr, en)"
    )
) -> BibleVersionsResponse:
    """
    Récupère les versions bibliques disponibles, optionnellement filtrées par langue.

    Args:
        language: Code langue pour filtrer

    Returns:
        Liste des versions bibliques
    """
    try:
        service = get_service()
        versions_data = await service.get_bible_versions(language)

        from .schemas import BibleVersionItem

        versions = [
            BibleVersionItem(
                id=version["id"],
                name=version["name"],
                abreviation=version["abreviation"],
            )
            for version in versions_data
        ]

        return BibleVersionsResponse(versions=versions)
    except Exception as e:
        logger.exception("❌ Erreur lors de la récupération des versions")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des versions: {str(e)}",
        ) from e


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: str) -> ProfileResponse:
    """
    Récupère le profil complet d'un utilisateur (préférences + statistiques).

    Args:
        user_id: Identifiant Firebase de l'utilisateur

    Returns:
        Profil complet avec préférences et statistiques
    """
    try:
        service = get_service()

        # Récupérer ou créer le profil
        profile_doc = await service.get_or_create_profile(user_id)

        if not profile_doc:
            raise HTTPException(
                status_code=404, detail=f"Profil non trouvé pour user_id: {user_id}"
            )

        # Calculer les statistiques
        stats = await service.calculate_stats(user_id)

        # Construire la réponse
        from .schemas import ProfilePreferences

        preferences = ProfilePreferences(**profile_doc["preferences"])

        return ProfileResponse(
            user_id=profile_doc["user_id"],
            preferences=preferences,
            stats=stats,
            created_at=profile_doc["created_at"],
            updated_at=profile_doc["updated_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Erreur lors de la récupération du profil pour {user_id}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la récupération du profil: {str(e)}"
        ) from e


@router.get("/{user_id}/stats", response_model=ProfileStats)
async def get_profile_stats(user_id: str) -> ProfileStats:
    """
    Récupère uniquement les statistiques d'un utilisateur.

    Args:
        user_id: Identifiant Firebase de l'utilisateur

    Returns:
        Statistiques utilisateur
    """
    try:
        service = get_service()
        stats = await service.calculate_stats(user_id)
        return stats
    except Exception as e:
        logger.exception(f"❌ Erreur lors du calcul des stats pour {user_id}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}"
        ) from e


@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: str, request: ProfileUpdateRequest
) -> ProfileResponse:
    """
    Met à jour les préférences d'un utilisateur.

    Args:
        user_id: Identifiant Firebase de l'utilisateur
        request: Données de mise à jour

    Returns:
        Profil mis à jour
    """
    try:
        service = get_service()

        # Vérifier que le profil existe (ou le créer)
        await service.get_or_create_profile(user_id)

        # Construire le dictionnaire de mise à jour MongoDB
        update_data = {}
        request_dict = request.dict(exclude_unset=True)

        for key, value in request_dict.items():
            update_data[f"preferences.{key}"] = value

        # Mettre à jour le profil
        updated_profile = await service.update_profile(user_id, update_data)

        if not updated_profile:
            raise HTTPException(
                status_code=404, detail=f"Profil non trouvé pour user_id: {user_id}"
            )

        # Recalculer les statistiques
        stats = await service.calculate_stats(user_id)

        # Construire la réponse
        from .schemas import ProfilePreferences

        preferences = ProfilePreferences(**updated_profile["preferences"])

        return ProfileResponse(
            user_id=updated_profile["user_id"],
            preferences=preferences,
            stats=stats,
            created_at=updated_profile["created_at"],
            updated_at=updated_profile["updated_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Erreur lors de la mise à jour du profil pour {user_id}")
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la mise à jour du profil: {str(e)}"
        ) from e

