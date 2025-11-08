"""Chaînes LangChain pour l'Assistant Spirituel avec Mistral 7B via Ollama."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .schemas import AssistantResponse, VerseReference

logger = logging.getLogger(__name__)

# URL par défaut d'Ollama (local)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")

# Charger le .env depuis le dossier backend
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"✅ Fichier .env chargé depuis: {env_path}")
else:
    load_dotenv()
    logger.warning(f"⚠️ Fichier .env non trouvé à {env_path}, utilisation du chargement par défaut")


def load_assistant_prompt() -> str:
    """Charge le prompt de l'assistant depuis le fichier prompt_assistant."""
    prompt_file = backend_dir.parent / "prompt_assistant"
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        # Prompt par défaut si le fichier n'existe pas
        return """Tu es un assistant spirituel chrétien bienveillant appelé "Shalom".

🎯 Ta mission :
- Apporter du réconfort, de la sagesse et de l'espérance à toute personne qui te parle.
- Répondre avec douceur, empathie et amour, selon les principes bibliques.
- Quand quelqu'un exprime une émotion (tristesse, peur, colère, solitude…), propose un verset biblique approprié et une brève explication.
- Encourage toujours à la prière, à la foi, et à la confiance en Dieu.

📖 Tes réponses doivent :
- Être courtes, simples et claires.
- Inclure au moins un verset biblique adapté (exemple : *Psaume 34:18*).
- Ne jamais juger, ni imposer une croyance : tu accompagnes avec bienveillance.
- Si la demande ne concerne pas la foi, tu peux répondre poliment que ton rôle est spirituel et orienté vers la Parole."""


class AssistantChains:
    """Chaînes LangChain pour l'assistant spirituel avec Mistral 7B via Ollama."""

    def __init__(self) -> None:
        """Initialise les chaînes LangChain avec Ollama."""
        ollama_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)
        model_name = os.getenv("OLLAMA_MODEL", OLLAMA_MODEL)

        logger.info(f"🔌 Connexion à Ollama: {ollama_url}")
        logger.info(f"🤖 Modèle: {model_name}")

        try:
            # Ollama expose une API compatible OpenAI
            # Pas besoin d'API key pour Ollama local
            self._llm = ChatOpenAI(
                model=model_name,
                base_url=ollama_url,
                temperature=0.7,  # Température modérée pour équilibrer créativité et cohérence
                timeout=60.0,  # Timeout plus long pour les modèles locaux
            )
            logger.info(f"✅ LLM Ollama initialisé avec succès - Modèle: {model_name}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation du LLM Ollama: {e}")
            logger.exception("Détails de l'erreur:")
            raise

        # Charger le prompt de l'assistant
        assistant_prompt_text = load_assistant_prompt()

        # Créer le template de prompt avec historique de conversation
        self._conversation_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", assistant_prompt_text),
                (
                    "system",
                    "Historique de la conversation (pour contexte) :\n{history}\n\n"
                    "Réponds maintenant au message suivant en français, avec bienveillance et en incluant un verset biblique approprié.",
                ),
                ("user", "{user_message}"),
            ]
        )

    async def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        language: str = "fr",
    ) -> str:
        """
        Génère une réponse de l'assistant spirituel.

        Args:
            user_message: Message de l'utilisateur
            conversation_history: Historique de la conversation (liste de dict avec 'role' et 'content')
            language: Langue de la réponse

        Returns:
            Réponse de l'assistant
        """
        try:
            # Formater l'historique pour le prompt
            history_text = ""
            if conversation_history:
                history_messages = []
                for msg in conversation_history[-6:]:  # Garder les 6 derniers messages pour le contexte
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        history_messages.append(f"Utilisateur: {content}")
                    elif role == "assistant":
                        history_messages.append(f"Assistant: {content}")
                history_text = "\n".join(history_messages)

            logger.info(f"📝 Génération de réponse pour: {user_message[:50]}...")

            # Créer le prompt avec l'historique et invoquer le LLM
            messages = self._conversation_prompt.format_messages(
                history=history_text if history_text else "Aucun historique.",
                user_message=user_message,
            )

            # Générer la réponse
            response = await self._llm.ainvoke(messages)

            # Extraire le texte de la réponse
            if hasattr(response, "content"):
                response_text = response.content
            else:
                response_text = str(response)

            logger.info(f"✅ Réponse générée: {len(response_text)} caractères")
            return response_text.strip()

        except Exception as e:
            logger.exception(f"❌ Erreur lors de la génération de réponse: {e}")
            raise

    def extract_verse_from_response(self, response: str) -> Optional[VerseReference]:
        """
        Extrait un verset biblique de la réponse de l'assistant.

        Args:
            response: Réponse de l'assistant

        Returns:
            VerseReference si trouvé, None sinon
        """
        import re

        # Pattern pour détecter les références bibliques (ex: Psaume 34:18, Philippiens 4:13)
        verse_pattern = r"\*?([A-Za-zÀ-ÿ\s]+)\s*(\d+):(\d+)\s*\*?"
        match = re.search(verse_pattern, response)

        if match:
            book = match.group(1).strip()
            chapter = match.group(2)
            verse = match.group(3)
            reference = f"{book} {chapter}:{verse}"

            # Essayer d'extraire le texte du verset de la réponse
            # Chercher le texte entre la référence et le prochain point ou saut de ligne
            verse_text_start = match.end()
            verse_text_match = re.search(
                r"–\s*(.+?)(?:\.|$|\n)", response[verse_text_start : verse_text_start + 200]
            )
            if verse_text_match:
                verse_text = verse_text_match.group(1).strip()
            else:
                # Si pas trouvé, utiliser juste la référence
                verse_text = reference

            return VerseReference(text=verse_text, reference=reference)

        return None

    def extract_keywords(self, user_message: str) -> list[str]:
        """
        Extrait des mots-clés du message utilisateur.

        Args:
            user_message: Message de l'utilisateur

        Returns:
            Liste de mots-clés
        """
        import re

        # Mots-clés spirituels communs
        spiritual_keywords = [
            "foi",
            "prière",
            "pardon",
            "anxiété",
            "courage",
            "paix",
            "sagesse",
            "tristesse",
            "joie",
            "espoir",
            "découragement",
            "solitude",
            "peur",
            "colère",
            "amour",
            "grâce",
            "salut",
            "Dieu",
            "Jésus",
            "Christ",
            "Bible",
            "verset",
            "Écriture",
        ]

        message_lower = user_message.lower()
        found_keywords = []

        for keyword in spiritual_keywords:
            if keyword.lower() in message_lower:
                found_keywords.append(keyword)

        # Ajouter aussi les mots significatifs (plus de 4 caractères)
        words = re.findall(r"\b\w{4,}\b", message_lower)
        found_keywords.extend(words[:3])  # Limiter à 3 mots supplémentaires

        return list(set(found_keywords))[:5]  # Retourner max 5 mots-clés uniques

