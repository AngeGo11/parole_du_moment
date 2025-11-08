"""Schémas Pydantic pour l'API Assistant."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class VerseReference(BaseModel):
    """Référence à un verset biblique."""

    text: str = Field(description="Texte du verset")
    reference: str = Field(description="Référence biblique (ex: Psaume 34:18)")


class Message(BaseModel):
    """Message dans une conversation."""

    role: str = Field(description="Rôle: 'user' ou 'assistant'")
    content: str = Field(description="Contenu du message")
    verse: Optional[VerseReference] = Field(
        default=None, description="Verset biblique associé (optionnel)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AssistantRequest(BaseModel):
    """Requête pour l'assistant spirituel."""

    user_id: str = Field(description="Identifiant Firebase de l'utilisateur")
    message: str = Field(description="Message de l'utilisateur")
    conversation_id: Optional[str] = Field(
        default=None, description="ID de conversation pour maintenir le contexte"
    )
    language: str = Field(default="fr", description="Langue de la réponse")


class AssistantResponse(BaseModel):
    """Réponse de l'assistant spirituel."""

    response: str = Field(description="Réponse de l'assistant")
    verse: Optional[VerseReference] = Field(
        default=None, description="Verset biblique suggéré"
    )
    conversation_id: str = Field(description="ID de conversation pour le contexte")
    keywords: List[str] = Field(
        default_factory=list, description="Mots-clés extraits du message"
    )


class ConversationHistory(BaseModel):
    """Historique d'une conversation."""

    conversation_id: str
    user_id: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime

