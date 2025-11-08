"""Script pour pré-calculer et stocker les embeddings de tous les versets dans MongoDB."""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from tqdm import tqdm

# Ajouter le dossier backend au path pour les imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from Home.embeddings import get_embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger le .env depuis le dossier backend
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


async def compute_and_store_embeddings(translation_id: Optional[str] = None, batch_size: int = 100):
    """
    Calcule et stocke les embeddings pour tous les versets dans MongoDB.
    
    Args:
        translation_id: Si fourni, ne traiter que cette traduction. Sinon, traiter toutes les traductions.
        batch_size: Nombre de versets à traiter par batch
    """
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGODB_DATABASE", "parole_du_moment_db")
    
    logger.info(f"🔌 Connexion à MongoDB: {mongo_url}")
    logger.info(f"📚 Base de données: {mongo_db}")
    
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[mongo_db]
    verses_collection = db["versets"]
    
    # Initialiser le service d'embeddings
    embedding_service = get_embedding_service()
    embedding_dim = embedding_service.get_embedding_dimension()
    logger.info(f"✅ Service d'embeddings initialisé (dimension: {embedding_dim})")
    
    # Construire la requête
    query = {}
    if translation_id:
        query["traduction_id"] = translation_id
        logger.info(f"📖 Traitement uniquement de la traduction: {translation_id}")
    else:
        logger.info("📖 Traitement de toutes les traductions")
    
    # Compter le nombre total de versets
    total_count = await verses_collection.count_documents(query)
    logger.info(f"📊 Nombre total de versets à traiter: {total_count}")
    
    if total_count == 0:
        logger.warning("⚠️ Aucun verset trouvé avec les critères spécifiés")
        return
    
    # Traiter par batches
    processed = 0
    skipped = 0
    updated = 0
    
    with tqdm(total=total_count, desc="Calcul des embeddings") as pbar:
        async for verse in verses_collection.find(query, {"_id": 1, "contenu": 1, "embedding": 1}):
            verse_id = verse["_id"]
            contenu = verse.get("contenu", "")
            
            # Vérifier si l'embedding existe déjà
            existing_embedding = verse.get("embedding")
            if existing_embedding is not None:
                skipped += 1
                pbar.update(1)
                continue
            
            if not contenu or not contenu.strip():
                logger.warning(f"⚠️ Verset {verse_id} sans contenu, ignoré")
                skipped += 1
                pbar.update(1)
                continue
            
            try:
                # Générer l'embedding
                embedding = embedding_service.encode(contenu)
                # Convertir en liste pour MongoDB (numpy array n'est pas sérialisable directement)
                embedding_list = embedding[0].tolist()
                
                # Mettre à jour le document dans MongoDB
                await verses_collection.update_one(
                    {"_id": verse_id},
                    {"$set": {"embedding": embedding_list}}
                )
                
                updated += 1
                processed += 1
                
                # Log tous les 100 versets
                if processed % 100 == 0:
                    logger.info(f"✅ {processed} versets traités ({updated} mis à jour, {skipped} ignorés)")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du traitement du verset {verse_id}: {e}")
                skipped += 1
            
            pbar.update(1)
    
    logger.info("=" * 60)
    logger.info("✅ Traitement terminé!")
    logger.info(f"   Total traité: {processed}")
    logger.info(f"   Mis à jour: {updated}")
    logger.info(f"   Ignorés (déjà calculés ou erreurs): {skipped}")
    logger.info("=" * 60)
    
    client.close()


async def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pré-calcule les embeddings pour tous les versets")
    parser.add_argument(
        "--translation",
        type=str,
        help="ID de traduction spécifique à traiter (ex: lsg, kjv). Si non fourni, traite toutes les traductions.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Taille des batches pour le traitement (défaut: 100)",
    )
    
    args = parser.parse_args()
    
    try:
        await compute_and_store_embeddings(
            translation_id=args.translation,
            batch_size=args.batch_size
        )
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        logger.exception(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    from typing import Optional
    asyncio.run(main())

