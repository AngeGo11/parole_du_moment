"""Schémas Pydantic pour l'API Profile."""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ProfilePreferences(BaseModel):
    """Préférences utilisateur."""

    notifications_enabled: bool = Field(default=True, description="Notifications activées")
    notification_time: str = Field(
        default="08:00",
        description="Heure de notification au format HH:MM",
    )
    dark_mode: bool = Field(default=False, description="Thème sombre activé")
    language: str = Field(default="fr", description="Code langue (ex: fr, en)")
    translation_id: str = Field(
        default="lsg",
        description="ID de traduction biblique (abréviation depuis traductions.abreviation)",
    )
    auto_play: bool = Field(default=False, description="Lecture automatique activée")

    @field_validator("notification_time")
    @classmethod
    def validate_notification_time(cls, v: str) -> str:
        """Valide le format HH:MM."""
        if not re.match(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("L'heure doit être au format HH:MM (ex: 08:00)")
        return v


class ProfileUpdateRequest(BaseModel):
    """Requête de mise à jour du profil."""

    notifications_enabled: Optional[bool] = None
    notification_time: Optional[str] = Field(
        default=None,
        description="Heure au format HH:MM",
    )
    dark_mode: Optional[bool] = None
    language: Optional[str] = None
    translation_id: Optional[str] = None
    auto_play: Optional[bool] = None

    @field_validator("notification_time")
    @classmethod
    def validate_notification_time(cls, v: Optional[str]) -> Optional[str]:
        """Valide le format HH:MM."""
        if v is not None and not re.match(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("L'heure doit être au format HH:MM (ex: 08:00)")
        return v


class ProfileStats(BaseModel):
    """Statistiques utilisateur."""

    verses_read: int = Field(default=0, description="Nombre de versets lus")
    favorites: int = Field(default=0, description="Nombre de favoris")
    consecutive_days: int = Field(default=0, description="Jours consécutifs de lecture")


class ProfileResponse(BaseModel):
    """Réponse complète du profil utilisateur."""

    user_id: str
    preferences: ProfilePreferences
    stats: ProfileStats
    created_at: datetime
    updated_at: datetime


class LanguageItem(BaseModel):
    """Item de langue disponible."""

    code: str = Field(description="Code langue (ex: fr, en)")
    name: str = Field(description="Nom de la langue (ex: Français, English)")


class LanguagesResponse(BaseModel):
    """Réponse avec la liste des langues disponibles."""

    languages: List[LanguageItem]


class BibleVersionItem(BaseModel):
    """Item de version biblique disponible."""

    id: str = Field(description="ID de traduction (abréviation)")
    name: str = Field(description="Nom complet de la version")
    abreviation: str = Field(description="Abréviation officielle")


class BibleVersionsResponse(BaseModel):
    """Réponse avec la liste des versions bibliques."""

    versions: List[BibleVersionItem]

