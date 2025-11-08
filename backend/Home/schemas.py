"""Schémas Pydantic pour l'API Home."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """Résultat de l'analyse IA du texte utilisateur."""

    emotions: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    summary: Optional[str] = Field(
        default=None, description="Résumé pastoral synthétique"
    )


class SpiritualContent(BaseModel):
    """Contenu spirituel généré à partir du verset."""

    explanation: str
    meditation: Optional[str] = None
    prayer: Optional[str] = None


class VerseMetadata(BaseModel):
    """Métadonnées optionnelles liées au verset."""

    translation: Optional[str] = Field(
        default=None, description="Abréviation de la traduction biblique"
    )
    book: Optional[str] = Field(default=None, description="Nom du livre biblique")
    chapter: Optional[int] = Field(default=None, description="Numéro du chapitre")
    verse: Optional[int] = Field(default=None, description="Numéro du verset")


class VerseRequest(BaseModel):
    """Requête envoyée depuis le frontend Home."""

    text: str = Field(..., description="Message exprimant le ressenti de l'utilisateur")
    user_id: Optional[str] = Field(default=None, description="Identifiant utilisateur")
    language: str = Field(default="fr", description="Langue souhaitée pour la réponse")
    translation_id: Optional[str] = Field(
        default=None, 
        description="ID de traduction biblique (ex: 'lsg', 'kjv'). Si non fourni, utilise bible_version ou la traduction par défaut selon la langue."
    )
    bible_version: Optional[str] = Field(
        default=None,
        description="Nom de la version biblique du profil (ex: 'Louis Segond 1910'). Utilisé si translation_id n'est pas fourni."
    )
    include_analysis: bool = Field(
        default=True,
        description="Inclure ou non les détails d'analyse dans la réponse",
    )


class VerseResponse(BaseModel):
    """Réponse renvoyée au frontend Home."""

    text: str
    reference: str
    explanation: str
    meditation: Optional[str] = None
    prayer: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    metadata: Optional[VerseMetadata] = None
    analysis: Optional[AnalysisResult] = None


