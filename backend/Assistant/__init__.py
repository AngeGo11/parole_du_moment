"""Routes FastAPI pour l'Assistant Spirituel."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .chains import AssistantChains
from .schemas import AssistantRequest, AssistantResponse, Message, VerseReference
from .service import ConversationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

# Initialisation lazy des services
_chains: AssistantChains | None = None
_conversation_service: ConversationService | None = None


def get_chains() -> AssistantChains:
    """Retourne l'instance de AssistantChains (initialisation lazy)."""
    global _chains
    if _chains is None:
        try:
            _chains = AssistantChains()
            logger.info("✅ AssistantChains initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de AssistantChains: {e}")
            raise
    return _chains


def get_conversation_service() -> ConversationService:
    """Retourne l'instance de ConversationService (initialisation lazy)."""
    global _conversation_service
    if _conversation_service is None:
        try:
            _conversation_service = ConversationService()
            logger.info("✅ ConversationService initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de ConversationService: {e}")
            raise
    return _conversation_service


@router.post("/chat", response_model=AssistantResponse)
async def chat(request: AssistantRequest) -> AssistantResponse:
    """
    Envoie un message à l'assistant spirituel et reçoit une réponse.

    Args:
        request: Requête avec le message de l'utilisateur

    Returns:
        Réponse de l'assistant avec verset biblique
    """
    try:
        logger.info(f"📥 Message reçu de {request.user_id}: {request.message[:50]}...")

        # Initialiser les services
        chains = get_chains()
        conversation_service = get_conversation_service()

        # Récupérer ou créer la conversation
        conversation_id = await conversation_service.get_or_create_conversation(
            request.user_id, request.conversation_id
        )

        # Ajouter le message utilisateur à l'historique
        await conversation_service.add_message(
            conversation_id, "user", request.message
        )

        # Récupérer l'historique pour le contexte
        history = await conversation_service.get_conversation_history(conversation_id)

        # Générer la réponse avec l'assistant
        try:
            response_text = await chains.generate_response(
                request.message, history, request.language
            )
        except Exception as e:
            logger.exception(f"❌ Erreur lors de la génération de réponse: {e}")
            # Réponse de fallback si Ollama n'est pas disponible
            response_text = (
                "Je comprends votre préoccupation. 🙏 "
                "Pourriez-vous vérifier que Ollama est démarré avec le modèle Mistral 7B ? "
                "Je suis là pour vous accompagner spirituellement avec la Parole de Dieu."
            )

        # Extraire le verset de la réponse
        verse = chains.extract_verse_from_response(response_text)

        # Extraire les mots-clés
        keywords = chains.extract_keywords(request.message)

        # Ajouter la réponse de l'assistant à l'historique
        verse_dict = None
        if verse:
            verse_dict = {"text": verse.text, "reference": verse.reference}

        await conversation_service.add_message(
            conversation_id, "assistant", response_text, verse_dict
        )

        # Construire la réponse
        response = AssistantResponse(
            response=response_text,
            verse=verse,
            conversation_id=conversation_id,
            keywords=keywords,
        )

        logger.info(f"✅ Réponse envoyée pour la conversation {conversation_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Erreur lors du traitement du message")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message: {str(e)}",
        ) from e


@router.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str) -> dict:
    """
    Récupère toutes les conversations d'un utilisateur.

    Args:
        user_id: Identifiant Firebase de l'utilisateur

    Returns:
        Liste des conversations
    """
    try:
        conversation_service = get_conversation_service()
        conversations = await conversation_service.get_all_conversations(user_id)

        return {"conversations": conversations}
    except Exception as e:
        logger.exception(f"❌ Erreur lors de la récupération des conversations")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des conversations: {str(e)}",
        ) from e


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: str) -> dict:
    """
    Récupère une conversation spécifique avec son historique complet.

    Args:
        conversation_id: ID de la conversation
        user_id: Identifiant Firebase de l'utilisateur

    Returns:
        Conversation avec historique des messages
    """
    try:
        conversation_service = get_conversation_service()

        # Vérifier que la conversation appartient à l'utilisateur
        conversation_doc = await conversation_service.conversations.find_one(
            {"conversation_id": conversation_id, "user_id": user_id}
        )

        if not conversation_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} non trouvée",
            )

        # Convertir les messages en format Message
        messages = []
        for msg_doc in conversation_doc.get("messages", []):
            verse = None
            if "verse" in msg_doc:
                verse = VerseReference(
                    text=msg_doc["verse"].get("text", ""),
                    reference=msg_doc["verse"].get("reference", ""),
                )

            messages.append(
                Message(
                    role=msg_doc.get("role", "user"),
                    content=msg_doc.get("content", ""),
                    verse=verse,
                    timestamp=msg_doc.get("timestamp"),
                )
            )

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": messages,
            "created_at": conversation_doc.get("created_at"),
            "updated_at": conversation_doc.get("updated_at"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Erreur lors de la récupération de la conversation")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de la conversation: {str(e)}",
        ) from e


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str) -> dict:
    """
    Supprime une conversation.

    Args:
        conversation_id: ID de la conversation
        user_id: Identifiant Firebase de l'utilisateur

    Returns:
        Confirmation de suppression
    """
    try:
        conversation_service = get_conversation_service()
        deleted = await conversation_service.delete_conversation(
            conversation_id, user_id
        )

        if deleted:
            return {"message": "Conversation supprimée avec succès", "deleted": True}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} non trouvée",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Erreur lors de la suppression de la conversation")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}",
        ) from e

