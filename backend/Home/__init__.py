"""Routes FastAPI pour l'analyse Home."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .chains import HomeChains
from .retriever import MongoVerseRetriever
from .schemas import AnalysisResult, VerseMetadata, VerseRequest, VerseResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/home", tags=["home"])

chains = HomeChains()
retriever = MongoVerseRetriever()


@router.post("/search", response_model=VerseResponse)
async def search_home(request: VerseRequest) -> VerseResponse:
    """Analyse le texte utilisateur et renvoie un verset pertinent."""

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide.")

    analysis: AnalysisResult
    try:
        analysis = await chains.run_analysis(request.text, request.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - protection supplémentaire
        logger.exception("Erreur d'analyse : %s", exc)
        raise HTTPException(
            status_code=500, detail="Impossible d'analyser le message pour le moment."
        ) from exc

    verse_doc = await retriever.get_best_verse(analysis)

    if verse_doc is None:
        raise HTTPException(
            status_code=404,
            detail="Aucun verset correspondant n'a été trouvé. Veuillez reformuler votre message.",
        )

    spiritual_content = await chains.generate_spiritual_content(
        verse_doc.text,
        verse_doc.reference,
        analysis,
        request.language,
    )

    response = VerseResponse(
        text=verse_doc.text,
        reference=verse_doc.reference,
        explanation=spiritual_content.explanation,
        meditation=spiritual_content.meditation,
        prayer=spiritual_content.prayer,
        keywords=verse_doc.keywords or analysis.keywords,
        metadata=VerseMetadata(
            translation=verse_doc.translation,
            book=verse_doc.book,
            chapter=verse_doc.chapter,
            verse=verse_doc.verse,
        ),
    )

    if request.include_analysis:
        response.analysis = analysis

    return response

