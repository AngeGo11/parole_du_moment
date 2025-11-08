"""Routes FastAPI pour l'analyse Home."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .chains import HomeChains
from .retriever import MongoVerseRetriever
from .schemas import AnalysisResult, VerseMetadata, VerseRequest, VerseResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/home", tags=["home"])

# Initialisation lazy pour éviter les erreurs au démarrage
_chains = None
_retriever = None


def get_chains() -> HomeChains:
    """Retourne l'instance de HomeChains (initialisation lazy)."""
    global _chains
    if _chains is None:
        try:
            _chains = HomeChains()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de HomeChains: {e}")
            logger.warning("Les heuristiques locales seront utilisées à la place")
            # Si l'initialisation échoue complètement, on ne peut pas créer l'instance
            # Mais avec le try/except dans chains.py, cela ne devrait pas arriver
            raise
    return _chains


def get_retriever() -> MongoVerseRetriever:
    """Retourne l'instance de MongoVerseRetriever (initialisation lazy)."""
    global _retriever
    if _retriever is None:
        try:
            _retriever = MongoVerseRetriever()
            logger.info("✅ MongoVerseRetriever initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation de MongoVerseRetriever: {e}")
            raise
    return _retriever


@router.get("/test/mongodb", tags=["test"])
async def test_mongodb() -> dict:
    """Endpoint de test pour vérifier MongoDB."""
    import asyncio
    
    try:
        logger.info("🔍 Test de connexion MongoDB...")
        retriever = get_retriever()
        
        # Ajouter un timeout pour éviter que ça bloque indéfiniment
        try:
            # Tester la connexion avec un timeout
            verse_count = await asyncio.wait_for(
                retriever.verses.count_documents({}), 
                timeout=5.0
            )
            emotions_count = await asyncio.wait_for(
                retriever.emotions.count_documents({}),
                timeout=5.0
            )
            themes_count = await asyncio.wait_for(
                retriever.themes.count_documents({}),
                timeout=5.0
            )
            
            logger.info(f"✅ MongoDB OK - Versets: {verse_count}, Emotions: {emotions_count}, Thèmes: {themes_count}")
            
            return {
                "status": "ok",
                "mongodb_connected": True,
                "versets_count": verse_count,
                "emotions_count": emotions_count,
                "themes_count": themes_count,
            }
        except asyncio.TimeoutError:
            logger.error("❌ Timeout lors de la connexion à MongoDB")
            return {
                "status": "error",
                "mongodb_connected": False,
                "error": "Timeout: MongoDB ne répond pas. Vérifiez que MongoDB est démarré (mongod)",
            }
    except Exception as e:
        logger.exception("Erreur lors du test MongoDB")
        return {
            "status": "error",
            "mongodb_connected": False,
            "error": str(e),
            "message": "Vérifiez que MongoDB est démarré: mongod"
        }


@router.post("/search", response_model=VerseResponse)
async def search_home(request: VerseRequest) -> VerseResponse:
    """Analyse le texte utilisateur et renvoie un verset pertinent."""

    logger.info(f"📥 Requête reçue: text='{request.text[:50]}...', language={request.language}")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide.")

    try:
        chains = get_chains()
        logger.info("✅ HomeChains initialisé")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de HomeChains: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erreur d'initialisation: {str(e)}"
        ) from e

    try:
        retriever = get_retriever()
        logger.info("✅ MongoVerseRetriever initialisé")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de MongoVerseRetriever: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erreur de connexion MongoDB: {str(e)}"
        ) from e

    analysis: AnalysisResult
    try:
        logger.info("🔍 Début de l'analyse du texte...")
        analysis = await chains.run_analysis(request.text, request.language)
        logger.info(f"✅ Analyse terminée: emotions={analysis.emotions}, themes={analysis.themes}, keywords={analysis.keywords[:3]}")
    except ValueError as exc:
        logger.error(f"❌ Erreur de validation: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("❌ Erreur d'analyse : %s", exc)
        raise HTTPException(
            status_code=500, detail="Impossible d'analyser le message pour le moment."
        ) from exc

    try:
        logger.info("🔍 Recherche du verset dans MongoDB...")
        verse_doc = await retriever.get_best_verse(analysis, request.translation_id, request.language, request.bible_version, request.text)
        if verse_doc is None:
            logger.warning("⚠️ Aucun verset trouvé dans MongoDB")
            raise HTTPException(
                status_code=404,
                detail="Aucun verset correspondant n'a été trouvé. Veuillez reformuler votre message.",
            )
        logger.info(f"✅ Verset trouvé: {verse_doc.reference}")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Erreur lors de la récupération du verset: %s", exc)
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la récupération du verset: {str(exc)}"
        ) from exc

    try:
        logger.info("🔍 Génération du contenu spirituel...")
        spiritual_content = await chains.generate_spiritual_content(
            verse_doc.text,
            verse_doc.reference,
            analysis,
            request.language,
            request.text,  # Passer le message original de l'utilisateur
        )
        logger.info("✅ Contenu spirituel généré")
    except Exception as exc:
        logger.exception("❌ Erreur lors de la génération du contenu spirituel: %s", exc)
        raise HTTPException(
            status_code=500, detail="Erreur lors de la génération du contenu spirituel."
        ) from exc

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

    logger.info("✅ Réponse envoyée avec succès")
    return response

