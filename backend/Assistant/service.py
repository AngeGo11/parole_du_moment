"""Service MongoDB pour gérer les conversations de l'assistant spirituel."""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from .schemas import Message

logger = logging.getLogger(__name__)

load_dotenv()


class ConversationService:
    """Service pour gérer les conversations dans MongoDB."""

    def __init__(self) -> None:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGODB_DATABASE", "parole_du_moment_db")

        logger.info(f"🔌 Connexion ConversationService à MongoDB: {mongo_url}")
        logger.info(f"📚 Base de données: {mongo_db}")

        try:
            self._client = AsyncIOMotorClient(
                mongo_url,
                serverSelectionTimeoutMS=5000,
            )
            self._db = self._client[mongo_db]
            logger.info("✅ Client MongoDB créé pour ConversationService")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion MongoDB: {e}")
            raise

    @property
    def conversations(self) -> AsyncIOMotorCollection:
        """Collection des conversations."""
        return self._db["assistant_conversations"]

    async def get_or_create_conversation(
        self, user_id: str, conversation_id: Optional[str] = None
    ) -> str:
        """
        Récupère une conversation existante ou en crée une nouvelle.

        Args:
            user_id: Identifiant Firebase de l'utilisateur
            conversation_id: ID de conversation existante (optionnel)

        Returns:
            ID de la conversation
        """
        if conversation_id:
            # Vérifier que la conversation existe et appartient à l'utilisateur
            conversation = await self.conversations.find_one(
                {"conversation_id": conversation_id, "user_id": user_id}
            )
            if conversation:
                logger.info(f"✅ Conversation trouvée: {conversation_id}")
                return conversation_id
            else:
                logger.warning(
                    f"⚠️ Conversation {conversation_id} non trouvée, création d'une nouvelle"
                )

        # Créer une nouvelle conversation
        new_conversation_id = str(uuid.uuid4())
        now = datetime.utcnow()

        conversation_doc = {
            "conversation_id": new_conversation_id,
            "user_id": user_id,
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }

        await self.conversations.insert_one(conversation_doc)
        logger.info(f"✅ Nouvelle conversation créée: {new_conversation_id}")

        return new_conversation_id

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        verse: Optional[dict] = None,
    ) -> None:
        """
        Ajoute un message à une conversation.

        Args:
            conversation_id: ID de la conversation
            role: Rôle ('user' ou 'assistant')
            content: Contenu du message
            verse: Verset biblique associé (optionnel)
        """
        message_doc = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
        }

        if verse:
            message_doc["verse"] = verse

        await self.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": message_doc},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        logger.info(f"✅ Message ajouté à la conversation {conversation_id}")

    async def get_conversation_history(
        self, conversation_id: str, limit: int = 20
    ) -> List[dict]:
        """
        Récupère l'historique d'une conversation.

        Args:
            conversation_id: ID de la conversation
            limit: Nombre maximum de messages à récupérer

        Returns:
            Liste des messages (format dict pour LangChain)
        """
        conversation = await self.conversations.find_one(
            {"conversation_id": conversation_id}
        )

        if not conversation:
            return []

        messages = conversation.get("messages", [])
        # Retourner les derniers messages au format dict
        history = []
        for msg in messages[-limit:]:
            history.append(
                {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                }
            )

        return history

    async def get_all_conversations(self, user_id: str) -> List[dict]:
        """
        Récupère toutes les conversations d'un utilisateur.

        Args:
            user_id: Identifiant Firebase de l'utilisateur

        Returns:
            Liste des conversations avec métadonnées
        """
        cursor = self.conversations.find({"user_id": user_id}).sort("updated_at", -1)
        conversations = []

        async for doc in cursor:
            conversations.append(
                {
                    "conversation_id": doc.get("conversation_id"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at"),
                    "message_count": len(doc.get("messages", [])),
                }
            )

        return conversations

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Supprime une conversation.

        Args:
            conversation_id: ID de la conversation
            user_id: Identifiant Firebase de l'utilisateur

        Returns:
            True si supprimée, False sinon
        """
        result = await self.conversations.delete_one(
            {"conversation_id": conversation_id, "user_id": user_id}
        )

        if result.deleted_count > 0:
            logger.info(f"✅ Conversation {conversation_id} supprimée")
            return True
        else:
            logger.warning(f"⚠️ Conversation {conversation_id} non trouvée")
            return False

