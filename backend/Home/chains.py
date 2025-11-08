"""Chaînes LangChain utilisées par l'API Home."""

from __future__ import annotations

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import RateLimitError

from .schemas import AnalysisResult, SpiritualContent

# Groq utilise l'interface OpenAI compatible, donc on peut utiliser ChatOpenAI avec base_url
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


logger = logging.getLogger(__name__)

# Charger le .env depuis le dossier backend (parent du dossier Home)
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info(f"✅ Fichier .env chargé depuis: {env_path}")
else:
    # Essayer aussi depuis le répertoire courant
    load_dotenv()
    logger.warning(f"⚠️ Fichier .env non trouvé à {env_path}, utilisation du chargement par défaut")


class HomeChains:
    """Ensemble de chaînes LangChain (analyse + génération)."""

    def __init__(self) -> None:
        # Utiliser GROQ_API_KEY au lieu de OPENAI_API_KEY
        api_key = os.getenv("GROQ_API_KEY")

        # Modèles Groq par défaut (mixtral-8x7b-32768 a été décommissionné)
        # Modèles disponibles: llama3-70b-8192, llama3-8b-8192, gemma-7b-it, gemma2-9b-it
        self._analysis_model_name = os.getenv("GROQ_MODEL_ANALYSIS", "llama-3.1-8b-instant")
        self._generation_model_name = os.getenv("GROQ_MODEL_GENERATION", "llama-3.1-8b-instant")

        # Log pour diagnostic
        logger.info(f"🔑 Vérification GROQ_API_KEY: {'✅ Présente' if api_key else '❌ Absente'}")
        if api_key:
            logger.debug(f"   Longueur de la clé: {len(api_key)} caractères")
            logger.debug(f"   Début de la clé: {api_key[:20]}...")

        if not api_key:
            logger.warning(
                "GROQ_API_KEY non défini. Les chaînes LangChain utiliseront les heuristiques locales."
            )
            self._analysis_llm = None
            self._generation_llm = None
        else:
            # Initialisation avec Groq (compatible OpenAI avec base_url)
            try:
                # Créer le client Groq via l'interface OpenAI compatible
                self._analysis_llm = ChatOpenAI(
                    api_key=api_key,
                    model=self._analysis_model_name,
                    temperature=0.2,
                    base_url=GROQ_BASE_URL,
                )
                # Appliquer with_structured_output après
                self._analysis_llm = self._analysis_llm.with_structured_output(AnalysisResult)
                logger.info(f"✅ LLM d'analyse Groq initialisé avec succès - Modèle: {self._analysis_model_name}")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation de l'analyse LLM: {e}")
                logger.warning("⚠️ Utilisation des heuristiques locales pour l'analyse")
                self._analysis_llm = None

            try:
                logger.info(f"🔧 Initialisation du LLM de génération avec le modèle Groq {self._generation_model_name}...")
                logger.debug(f"API Key présente: {bool(api_key)}, longueur: {len(api_key) if api_key else 0}")
                
                # Essayer différentes méthodes d'initialisation selon les versions
                try:
                    # Méthode 1: Initialisation directe avec with_structured_output
                    self._generation_llm = ChatOpenAI(
                        api_key=api_key,
                        model=self._generation_model_name,
                        temperature=0.7,  # Température plus élevée pour plus de créativité
                        base_url=GROQ_BASE_URL,
                    ).with_structured_output(SpiritualContent)
                except Exception as e1:
                    logger.warning(f"⚠️ Première méthode d'initialisation échouée: {e1}")
                    try:
                        # Méthode 2: Initialisation en deux étapes
                        base_llm = ChatOpenAI(
                            api_key=api_key,
                            model=self._generation_model_name,
                            temperature=0.7,
                            base_url=GROQ_BASE_URL,
                        )
                        self._generation_llm = base_llm.with_structured_output(SpiritualContent)
                    except Exception as e2:
                        logger.error(f"❌ Deuxième méthode d'initialisation échouée: {e2}")
                        raise e2
                
                logger.info(f"✅ LLM de génération Groq initialisé avec succès - Modèle: {self._generation_model_name}")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'initialisation de la génération LLM: {e}")
                logger.exception("Détails de l'erreur:")
                logger.warning("⚠️ Utilisation des heuristiques locales pour la génération")
                self._generation_llm = None

        self._analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Tu es un pasteur chrétien. Analyse le message utilisateur et identifie au maximum trois "
                    "émotions, trois thèmes et cinq mots-clés pertinents. Fourni un résumé pastoral concis en {language}.",
                ),
                (
                    "user",
                    "Message utilisateur : {text}",
                ),
            ]
        )

        self._spiritual_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Tu es un pasteur et conseiller spirituel chrétien expérimenté. "
                    "Ta mission est de créer un contenu spirituel profondément ancré dans le verset biblique fourni, "
                    "tout en étant personnellement adapté aux besoins émotionnels et spirituels de la personne.\n\n"
                    "Instructions importantes :\n"
                    "- L'explication doit être spécifique au verset, expliquer son contexte biblique, son sens profond et son application pratique\n"
                    "- La méditation doit inviter à une réflexion personnelle basée sur les mots et le message du verset\n"
                    "- La prière doit être inspirée directement par le verset et les besoins exprimés\n"
                    "- Utilise un ton bienveillant, biblique, encourageant et authentique\n"
                    "- Sois précis et évite les généralités - chaque verset a un message unique\n"
                    "- Réponds en {language}",
                ),
                (
                    "user",
                    "Verset biblique : {verse_text}\n"
                    "Référence biblique : {verse_reference}\n"
                    "Message de la personne : {user_message}\n"
                    "Émotions détectées : {emotions}\n"
                    "Thèmes détectés : {themes}\n"
                    "Mots-clés : {keywords}\n\n"
                    "Génère maintenant :\n"
                    "1. Une EXPLICATION approfondie du verset (2-3 phrases) qui explique le contexte, le sens et l'application\n"
                    "2. Une MÉDITATION personnelle (2-3 phrases) qui invite à réfléchir sur ce verset dans sa situation actuelle\n"
                    "3. Une PRIÈRE suggérée (2-3 phrases) inspirée par le verset et adaptée aux besoins exprimés",
                ),
            ]
        )

    async def run_analysis(self, text: str, language: str) -> AnalysisResult:
        """Analyse le texte utilisateur via LangChain ou heuristiques locales."""

        if not text.strip():
            raise ValueError("Le texte à analyser ne peut pas être vide.")

        if self._analysis_llm is None:
            return self._heuristic_analysis(text)

        chain = self._analysis_prompt | self._analysis_llm
        try:
            return await chain.ainvoke({"text": text, "language": language})
        except Exception as exc:  # pragma: no cover - fallback heuristique
            logger.error("Erreur lors de l'analyse LangChain: %s", exc)
            return self._heuristic_analysis(text)

    async def generate_spiritual_content(
        self, verse_text: str, verse_reference: str, analysis: AnalysisResult, language: str, user_message: Optional[str] = None
    ) -> SpiritualContent:
        """
        Génère le contenu spirituel avec Groq (Mixtral) directement en fonction du verset attribué.
        
        Args:
            verse_text: Le texte du verset biblique
            verse_reference: La référence du verset (ex: "Jean 3:16")
            analysis: L'analyse du message utilisateur
            language: La langue pour la réponse
            user_message: Le message original de l'utilisateur (optionnel)
        """

        if self._generation_llm is None:
            logger.error("❌ Groq non disponible pour la génération du contenu spirituel")
            # Vérifier si la clé API existe
            api_key_check = os.getenv("GROQ_API_KEY")
            if not api_key_check:
                raise ValueError(
                    "GROQ_API_KEY n'est pas défini dans les variables d'environnement. "
                    "Veuillez créer un fichier .env dans le dossier backend avec: GROQ_API_KEY=votre_cle_api"
                )
            else:
                raise ValueError(
                    f"Groq n'a pas pu être initialisé malgré la présence de GROQ_API_KEY. "
                    f"Vérifiez les logs pour plus de détails. Longueur de la clé: {len(api_key_check)}"
                )

        chain = self._spiritual_prompt | self._generation_llm
        try:
            logger.info(f"🤖 Génération du contenu spirituel avec Groq pour le verset {verse_reference}...")
            result = await chain.ainvoke(
                {
                    "verse_text": verse_text,
                    "verse_reference": verse_reference,
                    "user_message": user_message or analysis.summary or "Recherche de guidance spirituelle",
                    "emotions": ", ".join(analysis.emotions) or "aucune",
                    "themes": ", ".join(analysis.themes) or "aucun",
                    "keywords": ", ".join(analysis.keywords) or "aucun",
                    "language": language,
                }
            )
            logger.info("✅ Contenu spirituel généré avec succès par Groq")
            return result
        except RateLimitError as exc:
            # Gérer spécifiquement les erreurs de quota/rate limit
            logger.error(f"❌ Quota Groq dépassé ou rate limit atteint: {exc}")
            logger.warning("⚠️ Utilisation du fallback heuristique pour générer le contenu spirituel")
            # Utiliser le fallback heuristique avec un message informatif
            fallback_content = self._heuristic_content(verse_text, verse_reference, analysis)
            # Ajouter une note dans l'explication pour indiquer que c'est un fallback
            fallback_content.explanation = (
                f"[Note: Groq temporairement indisponible - quota dépassé] {fallback_content.explanation}"
            )
            return fallback_content
        except Exception as exc:
            # Gérer les autres erreurs Groq
            error_str = str(exc).lower()
            if "429" in error_str or "insufficient_quota" in error_str or "rate limit" in error_str:
                logger.error(f"❌ Quota Groq dépassé ou rate limit atteint: {exc}")
                logger.warning("⚠️ Utilisation du fallback heuristique pour générer le contenu spirituel")
                fallback_content = self._heuristic_content(verse_text, verse_reference, analysis)
                fallback_content.explanation = (
                    f"[Note: Groq temporairement indisponible - quota dépassé] {fallback_content.explanation}"
                )
                return fallback_content
            else:
                logger.exception(f"❌ Erreur lors de la génération du contenu spirituel avec Groq: {exc}")
                # Pour les autres erreurs, utiliser aussi le fallback plutôt que de faire échouer
                logger.warning("⚠️ Utilisation du fallback heuristique en raison d'une erreur Groq")
                fallback_content = self._heuristic_content(verse_text, verse_reference, analysis)
                fallback_content.explanation = (
                    f"[Note: Groq temporairement indisponible] {fallback_content.explanation}"
                )
                return fallback_content

    @staticmethod
    def _heuristic_analysis(text: str) -> AnalysisResult:
        """Analyse simple basée sur des mots-clés si LangChain indisponible."""

        lowered = text.lower()

        mapping = {
            "seul": ("solitude", "présence de Dieu"),
            "solitude": ("solitude", "communion"),
            "fatigu": ("fatigue", "repos en Christ"),
            "épuisé": ("fatigue", "repos en Christ"),
            "peur": ("peur", "confiance"),
            "ango": ("anxiété", "paix"),
            "stress": ("stress", "repos"),
            "doute": ("doute", "foi"),
            "trist": ("tristesse", "espérance"),
            "culp": ("culpabilité", "pardon"),
        }

        emotions: List[str] = []
        themes: List[str] = []
        keywords: List[str] = []

        for key, (emotion, theme) in mapping.items():
            if key in lowered:
                emotions.append(emotion)
                themes.append(theme)
                keywords.append(key)

        if not emotions:
            emotions.append("quête de paix")
        if not themes:
            themes.append("espérance")
        if not keywords:
            keywords = text.split()[:5]

        summary = (
            "Analyse heuristique : l'utilisateur exprime {emotion} et recherche {theme}."
        ).format(emotion=emotions[0], theme=themes[0])

        return AnalysisResult(
            emotions=list(dict.fromkeys(emotions)),
            themes=list(dict.fromkeys(themes)),
            keywords=list(dict.fromkeys(keywords)),
            summary=summary,
        )

    @staticmethod
    def _heuristic_content(verse_text: str, verse_reference: str, analysis: Optional[AnalysisResult] = None) -> SpiritualContent:
        """
        Contenu généré basé sur des heuristiques lorsque Groq n'est pas disponible.
        Génère un contenu plus spécifique au verset basé sur des mots-clés et des patterns.
        """
        
        verse_lower = verse_text.lower()
        
        # Patterns pour générer une explication plus spécifique
        explanation_patterns = {
            "amour": "Ce verset révèle l'amour infini de Dieu pour nous. Il nous rappelle que nous sommes précieux à Ses yeux, peu importe nos circonstances.",
            "foi": "Ce verset nous invite à placer notre confiance en Dieu, même lorsque nous ne comprenons pas tout. La foi grandit dans l'obéissance et la confiance.",
            "espoir": "Ce verset apporte une lumière dans les moments sombres. Il nous rappelle que Dieu a un plan pour notre vie et que notre espoir est fondé sur Ses promesses.",
            "pardon": "Ce verset nous rappelle la grâce infinie de Dieu. Son pardon est disponible pour tous ceux qui se tournent vers Lui avec un cœur repentant.",
            "paix": "Ce verset nous invite à trouver la paix qui dépasse toute compréhension en remettant nos soucis entre les mains de Dieu.",
            "force": "Ce verset nous encourage à puiser notre force en Dieu. Il ne nous abandonne jamais et nous donne la capacité de surmonter les épreuves.",
            "protection": "Ce verset nous assure de la protection divine. Dieu veille sur nous et nous garde dans Sa main puissante.",
        }
        
        # Rechercher des mots-clés dans le verset pour une explication plus pertinente
        explanation = None
        for keyword, pattern_explanation in explanation_patterns.items():
            if keyword in verse_lower:
                explanation = pattern_explanation
                break
        
        # Si aucun pattern ne correspond, utiliser une explication générique mais adaptée
        if not explanation:
            explanation = (
                f"Ce verset de {verse_reference} contient une vérité profonde qui peut transformer notre vie. "
                "Il nous invite à réfléchir sur notre relation avec Dieu et à Lui faire confiance dans toutes les circonstances."
            )
        
        # Méditation personnalisée
        meditation = (
            f"Prends un moment pour méditer sur ce verset de {verse_reference}. "
            "Laisse chaque mot résonner dans ton cœur. Que te dit Dieu aujourd'hui à travers cette parole ? "
            "Comment peux-tu appliquer cette vérité dans ta situation actuelle ?"
        )
        
        # Prière adaptée
        if analysis and analysis.emotions:
            emotion = analysis.emotions[0]
            prayer = (
                f"Seigneur, merci pour ta parole dans {verse_reference}. "
                f"Je Te confie mon {emotion} et je Te demande de m'aider à trouver la paix et la force en Toi. "
                "Aide-moi à recevoir ce que Tu veux me dire aujourd'hui. Amen."
            )
        else:
            prayer = (
                f"Seigneur, merci pour ta parole dans {verse_reference}. "
                "Aide-moi à la méditer, à la comprendre et à la vivre dans ma vie quotidienne. "
                "Que cette parole transforme mon cœur et guide mes pas. Amen."
            )

        return SpiritualContent(
            explanation=explanation,
            meditation=meditation,
            prayer=prayer,
        )


