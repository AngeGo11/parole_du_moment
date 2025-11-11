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
- Si la demande ne concerne pas la foi, tu peux répondre poliment que ton rôle est spirituel et orienté vers la Parole.

🧘 MÉDITATION SUR UN VERSET :
Quand l'utilisateur te demande de méditer ensemble sur un verset spécifique (par exemple : "Méditons ensemble sur ce verset: [verset]"), tu dois :
1. Reconnaître le verset mentionné et sa référence biblique
2. Fournir une méditation spirituelle approfondie sur ce verset
3. Expliquer le contexte et le sens du verset
4. Relier ce verset à la vie quotidienne et aux défis spirituels
5. Offrir des pistes de réflexion et d'application pratique
6. Inclure une prière ou une pensée de méditation si approprié
NE demande PAS plus de précisions, mais engage-toi directement dans la méditation sur le verset fourni."""


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
            # On passe une clé factice pour contourner la validation de LangChain
            self._llm = ChatOpenAI(
                model=model_name,
                base_url=ollama_url,
                api_key="ollama",  # Clé factice pour Ollama (non utilisée)
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
            # Détecter si c'est une demande de méditation sur un verset
            is_meditation_request = self._is_meditation_request(user_message)
            verse_info = None
            if is_meditation_request:
                verse_info = self._extract_verse_from_user_message(user_message)
            
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
            if is_meditation_request and verse_info:
                logger.info(f"🧘 Demande de méditation détectée sur: {verse_info['reference']}")

            # Charger le prompt de l'assistant pour l'utiliser dans le template
            assistant_prompt_text = load_assistant_prompt()

            # Construire le message système avec contexte supplémentaire si méditation
            if is_meditation_request and verse_info:
                # Créer un prompt spécialisé pour la méditation
                meditation_prompt = ChatPromptTemplate.from_messages(
                    [
                        ("system", assistant_prompt_text),
                        (
                            "system",
                            f"""L'utilisateur demande de méditer ensemble sur le verset suivant :
Verset : "{verse_info['text']}"
Référence : {verse_info['reference']}

Engage-toi directement dans une méditation spirituelle approfondie sur ce verset. Explique son contexte, son sens, et comment l'appliquer dans la vie quotidienne. Ne demande pas plus de précisions.

Historique de la conversation (pour contexte) :\n{history_text if history_text else "Aucun historique."}""",
                        ),
                        ("user", "{user_message}"),
                    ]
                )
                messages = meditation_prompt.format_messages(user_message=user_message)
            else:
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

    def _is_meditation_request(self, user_message: str) -> bool:
        """Détecte si le message est une demande de méditation sur un verset."""
        lower_message = user_message.lower()
        meditation_keywords = [
            "méditons ensemble",
            "méditons sur",
            "méditer sur",
            "méditation sur",
            "méditons ce verset",
            "méditer ce verset",
        ]
        return any(keyword in lower_message for keyword in meditation_keywords)

    def _extract_verse_from_user_message(self, user_message: str) -> Optional[dict]:
        """
        Extrait le verset et sa référence du message utilisateur.
        
        Returns:
            Dict avec 'text' et 'reference' si trouvé, None sinon
        """
        import re
        
        # Pattern pour détecter les références bibliques (ex: job.9.28.LSG, Job 9:28, etc.)
        # Format 1: livre.chapitre.verset.traduction (ex: job.9.28.LSG)
        pattern1 = r'([a-z]+)\.(\d+)\.(\d+)\.([A-Z]+)'
        match1 = re.search(pattern1, user_message, re.IGNORECASE)
        
        if match1:
            book_abbr = match1.group(1).lower()
            chapter = match1.group(2)
            verse = match1.group(3)
            translation = match1.group(4)
            
            # Mapper les abréviations de livres
            book_map = {
                'job': 'Job', 'gn': 'Genèse', 'ex': 'Exode', 'lv': 'Lévitique',
                'nb': 'Nombres', 'dt': 'Deutéronome', 'js': 'Josué', 'jg': 'Juges',
                'rt': 'Ruth', '1s': '1 Samuel', '2s': '2 Samuel', '1r': '1 Rois',
                '2r': '2 Rois', '1ch': '1 Chroniques', '2ch': '2 Chroniques',
                'esd': 'Esdras', 'ne': 'Néhémie', 'est': 'Esther', 'ps': 'Psaumes',
                'pr': 'Proverbes', 'ec': 'Ecclésiaste', 'ct': 'Cantique des Cantiques',
                'es': 'Ésaïe', 'jer': 'Jérémie', 'la': 'Lamentations', 'ez': 'Ézéchiel',
                'da': 'Daniel', 'os': 'Osée', 'jl': 'Joël', 'am': 'Amos',
                'ab': 'Abdias', 'jon': 'Jonas', 'mi': 'Michée', 'na': 'Nahum',
                'hab': 'Habacuc', 'so': 'Sophonie', 'ag': 'Aggée', 'za': 'Zacharie',
                'mal': 'Malachie', 'mt': 'Matthieu', 'mr': 'Marc', 'lu': 'Luc',
                'jn': 'Jean', 'ac': 'Actes', 'ro': 'Romains', '1co': '1 Corinthiens',
                '2co': '2 Corinthiens', 'ga': 'Galates', 'ep': 'Éphésiens',
                'ph': 'Philippiens', 'col': 'Colossiens', '1th': '1 Thessaloniciens',
                '2th': '2 Thessaloniciens', '1ti': '1 Timothée', '2ti': '2 Timothée',
                'tit': 'Tite', 'phm': 'Philémon', 'he': 'Hébreux', 'ja': 'Jacques',
                '1pi': '1 Pierre', '2pi': '2 Pierre', '1jn': '1 Jean', '2jn': '2 Jean',
                '3jn': '3 Jean', 'jud': 'Jude', 'ap': 'Apocalypse'
            }
            
            book_name = book_map.get(book_abbr, book_abbr.capitalize())
            reference = f"{book_name} {chapter}:{verse}"
            
            # Extraire le texte du verset (entre guillemets ou après "verset:")
            verse_text_match = re.search(r'verset[:\s]+["\'](.+?)["\']', user_message, re.IGNORECASE)
            if not verse_text_match:
                verse_text_match = re.search(r'["\'](.+?)["\']', user_message)
            
            verse_text = verse_text_match.group(1) if verse_text_match else reference
            
            return {
                'text': verse_text.strip(),
                'reference': reference
            }
        
        # Format 2: Livre Chapitre:verset (ex: Job 9:28)
        pattern2 = r'([A-Za-zÀ-ÿ\s]+)\s+(\d+):(\d+)'
        match2 = re.search(pattern2, user_message)
        
        if match2:
            book = match2.group(1).strip()
            chapter = match2.group(2)
            verse = match2.group(3)
            reference = f"{book} {chapter}:{verse}"
            
            # Extraire le texte du verset
            verse_text_match = re.search(r'["\'](.+?)["\']', user_message)
            verse_text = verse_text_match.group(1) if verse_text_match else reference
            
            return {
                'text': verse_text.strip(),
                'reference': reference
            }
        
        return None

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

