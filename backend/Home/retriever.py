"""Service de récupération des versets depuis MongoDB."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from .schemas import AnalysisResult


logger = logging.getLogger(__name__)

load_dotenv()


@dataclass
class VerseDocument:
    """Représentation typée d'un verset extrait de MongoDB."""

    id: ObjectId
    text: str
    reference: str
    keywords: List[str]
    translation: Optional[str]
    book: Optional[str]
    chapter: Optional[int]
    verse: Optional[int]


class MongoVerseRetriever:
    """Accès MongoDB pour récupérer les versets pertinents."""

    def __init__(self) -> None:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGODB_DATABASE", "parole_du_moment_db")

        self._client = AsyncIOMotorClient(mongo_url)
        self._db = self._client[mongo_db]

    @property
    def verses(self) -> AsyncIOMotorCollection:
        return self._db["versets"]

    @property
    def emotions(self) -> AsyncIOMotorCollection:
        return self._db["emotions"]

    @property
    def themes(self) -> AsyncIOMotorCollection:
        return self._db["themes"]

    @property
    def verses_emotions(self) -> AsyncIOMotorCollection:
        return self._db["versets_emotions"]

    @property
    def verses_themes(self) -> AsyncIOMotorCollection:
        return self._db["versets_themes"]

    async def get_best_verse(self, analysis: AnalysisResult) -> Optional[VerseDocument]:
        """Retourne le verset le plus pertinent selon l'analyse fournie."""

        verse_ids: List[ObjectId] = []

        emotion_ids = await self._find_ids_by_name(self.emotions, analysis.emotions)
        theme_ids = await self._find_ids_by_name(self.themes, analysis.themes)

        if emotion_ids:
            verse_ids.extend(
                await self._find_verse_ids_by_link(
                    self.verses_emotions, "emotion_id", emotion_ids
                )
            )

        if theme_ids:
            verse_ids.extend(
                await self._find_verse_ids_by_link(
                    self.verses_themes, "theme_id", theme_ids
                )
            )

        verse_ids = list(dict.fromkeys(verse_ids))

        search_terms = self._build_search_terms(analysis)
        query = {}
        projection = {
            "contenu": 1,
            "ref_unique": 1,
            "mots_cles": 1,
            "traduction": 1,
            "livre": 1,
            "chapitre": 1,
            "numero": 1,
        }

        if verse_ids:
            query["_id"] = {"$in": verse_ids}

        if search_terms:
            query["$text"] = {"$search": " ".join(search_terms)}
            projection["score"] = {"$meta": "textScore"}

        results: List[dict] = []

        if query:
            try:
                cursor = self.verses.find(query, projection)
                if "score" in projection:
                    cursor = cursor.sort([("score", {"$meta": "textScore"})])
                results = await cursor.to_list(length=5)
            except Exception as exc:
                logger.warning("Recherche textuelle indisponible : %s", exc)

        if not results and search_terms:
            regex = re.compile("|".join(map(re.escape, search_terms)), re.IGNORECASE)
            results = await self.verses.find({"contenu": regex}, projection).to_list(5)

        if not results and verse_ids:
            cursor = self.verses.find({"_id": {"$in": verse_ids}}, projection)
            cursor = cursor.limit(3)
            results = await cursor.to_list(length=3)

        if not results:
            sample_projection = projection.copy()
            sample_projection.pop("score", None)
            sample = self.verses.aggregate([
                {"$sample": {"size": 1}},
                {"$project": sample_projection},
            ])
            results = await sample.to_list(length=1)

        if not results:
            return None

        best = results[0]
        return VerseDocument(
            id=best.get("_id"),
            text=best.get("contenu", ""),
            reference=best.get("ref_unique", "Référence inconnue"),
            keywords=list(best.get("mots_cles", [])),
            translation=best.get("traduction"),
            book=best.get("livre"),
            chapter=best.get("chapitre"),
            verse=best.get("numero"),
        )

    async def _find_ids_by_name(
        self, collection: AsyncIOMotorCollection, names: Iterable[str]
    ) -> List[ObjectId]:
        filters = [
            {"nom": {"$regex": f"^{re.escape(name)}$", "$options": "i"}}
            for name in names
            if name
        ]

        if not filters:
            return []

        cursor = collection.find({"$or": filters}, {"_id": 1})
        docs = await cursor.to_list(length=50)
        return [doc["_id"] for doc in docs if doc.get("_id")]

    async def _find_verse_ids_by_link(
        self,
        collection: AsyncIOMotorCollection,
        field_name: str,
        ids: Iterable[ObjectId],
    ) -> List[ObjectId]:
        pipeline = [
            {"$match": {field_name: {"$in": list(ids)}}},
            {
                "$group": {
                    "_id": "$verset_id",
                    "score": {"$sum": "$poids_ia"},
                }
            },
            {"$sort": {"score": -1}},
            {"$limit": 20},
        ]

        docs = await collection.aggregate(pipeline).to_list(length=20)
        return [doc["_id"] for doc in docs if doc.get("_id")]

    @staticmethod
    def _build_search_terms(analysis: AnalysisResult) -> List[str]:
        terms = list(dict.fromkeys(analysis.keywords + analysis.emotions + analysis.themes))
        return [term for term in terms if term]


