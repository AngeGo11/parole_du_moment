"""Chaînes LangChain utilisées par l'API Home."""

from __future__ import annotations

import logging
import os
from typing import List

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .schemas import AnalysisResult, SpiritualContent


logger = logging.getLogger(__name__)

load_dotenv()


class HomeChains:
    """Ensemble de chaînes LangChain (analyse + génération)."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        self._analysis_model_name = os.getenv("OPENAI_MODEL_ANALYSIS", "gpt-4o")
        self._generation_model_name = os.getenv("OPENAI_MODEL_GENERATION", "gpt-4o")

        if not api_key:
            logger.warning(
                "OPENAI_API_KEY non défini. Les chaînes LangChain utiliseront les heuristiques locales."
            )
            self._analysis_llm = None
            self._generation_llm = None
        else:
            self._analysis_llm = ChatOpenAI(
                model=self._analysis_model_name,
                temperature=0.2,
            ).with_structured_output(AnalysisResult)

            self._generation_llm = ChatOpenAI(
                model=self._generation_model_name,
                temperature=0.35,
            ).with_structured_output(SpiritualContent)

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
                    "Tu es un conseiller spirituel chrétien. En te basant sur le verset fourni et le ressenti "
                    "de la personne, rédige une explication, une méditation et une prière personnalisées en {language}."
                    "Utilise un ton bienveillant, biblique et encourageant.",
                ),
                (
                    "user",
                    "Verset : {verse_text}\n"
                    "Référence : {verse_reference}\n"
                    "Émotions détectées : {emotions}\n"
                    "Thèmes détectés : {themes}\n"
                    "Mots-clés : {keywords}",
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
        self, verse_text: str, verse_reference: str, analysis: AnalysisResult, language: str
    ) -> SpiritualContent:
        """Génère le contenu spirituel avec LangChain ou heuristiques."""

        if self._generation_llm is None:
            return self._heuristic_content(verse_text, verse_reference)

        chain = self._spiritual_prompt | self._generation_llm
        try:
            return await chain.ainvoke(
                {
                    "verse_text": verse_text,
                    "verse_reference": verse_reference,
                    "emotions": ", ".join(analysis.emotions) or "aucune",
                    "themes": ", ".join(analysis.themes) or "aucun",
                    "keywords": ", ".join(analysis.keywords) or "aucun",
                    "language": language,
                }
            )
        except Exception as exc:  # pragma: no cover - fallback heuristique
            logger.error(
                "Erreur lors de la génération du contenu spirituel LangChain: %s", exc
            )
            return self._heuristic_content(verse_text, verse_reference)

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
    def _heuristic_content(verse_text: str, verse_reference: str) -> SpiritualContent:
        """Contenu générique si LangChain indisponible."""

        explanation = (
            "Ce verset rappelle la fidélité de Dieu au coeur de nos situations. "
            "Il invite à placer sa confiance en Lui malgré les circonstances."
        )
        meditation = (
            "Relis ce verset lentement et laisse chaque mot descendre dans ton coeur. "
            "Que veux-tu confier à Dieu aujourd'hui ?"
        )
        prayer = (
            f"Seigneur, merci pour ta parole dans {verse_reference}. Aide-moi à la vivre aujourd'hui et "
            "à recevoir la paix que tu promets. Amen."
        )

        return SpiritualContent(
            explanation=explanation,
            meditation=meditation,
            prayer=prayer,
        )


