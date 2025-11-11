#!/usr/bin/env python3
"""
Script d'import MongoDB depuis un export précédent.
Utile pour restaurer les données sur un nouvel ordinateur.
"""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from pymongo import MongoClient
    from bson import ObjectId, json_util
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("❌ MongoDB non disponible - installez pymongo")


def init_mongodb():
    """Initialise la connexion MongoDB."""
    if not MONGODB_AVAILABLE:
        return None, None
    
    try:
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("MONGODB_DATABASE", "parole_du_moment_db")
        client = MongoClient(mongo_url)
        db = client[mongo_db]
        print(f"✅ Connexion MongoDB établie: {mongo_url}")
        print(f"📚 Base de données: {mongo_db}")
        return db, client
    except Exception as e:
        print(f"❌ Erreur d'initialisation MongoDB: {e}")
        return None, None


def import_collection(db, collection_name, json_file):
    """Importe une collection depuis un fichier JSON."""
    if not json_file.exists():
        print(f"   ⚠️  Fichier non trouvé: {json_file}")
        return False
    
    collection = db[collection_name]
    
    print(f"\n📥 Import de {collection_name}...")
    
    # Charger les données JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    if not json_data:
        print(f"   ⚠️  Fichier vide, ignoré")
        return False
    
    # Convertir les strings ObjectId en ObjectId MongoDB
    documents = json_util.loads(json.dumps(json_data))
    
    # Vérifier si la collection existe déjà
    existing_count = collection.count_documents({})
    if existing_count > 0:
        print(f"   ⚠️  Collection existe déjà avec {existing_count} documents")
        response = input(f"   ❓ Voulez-vous supprimer les données existantes? (o/N): ")
        if response.lower() == 'o':
            collection.delete_many({})
            print(f"   🗑️  {existing_count} documents supprimés")
        else:
            print(f"   ⏭️  Import annulé pour cette collection")
            return False
    
    # Insérer les documents
    if isinstance(documents, list):
        if documents:
            collection.insert_many(documents)
            print(f"   ✅ {len(documents)} documents importés")
        else:
            print(f"   ⚠️  Aucun document à importer")
    else:
        collection.insert_one(documents)
        print(f"   ✅ 1 document importé")
    
    return True


def main():
    """Fonction principale."""
    print("=" * 60)
    print("🚀 Import MongoDB - Restauration des données")
    print("=" * 60)
    
    # Initialiser MongoDB
    db, client = init_mongodb()
    if db is None or client is None:
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    try:
        # Trouver le répertoire d'export
        dataset_dir = Path(__file__).parent
        export_dir = dataset_dir / "mongodb_export"
        
        if not export_dir.exists():
            print(f"❌ Répertoire d'export non trouvé: {export_dir}")
            print("   💡 Exécutez d'abord export_mongodb.py pour créer l'export")
            return
        
        print(f"\n📁 Répertoire d'import: {export_dir}")
        
        # Liste des collections à importer (dans l'ordre de dépendance)
        collections_to_import = [
            "testaments",
            "traductions",
            "livres",
            "emotions",
            "themes",
            "versets",
            "versets_emotions",
            "versets_themes",
            "users",
            "profiles",
            "verse_history",
            "favorite_verses",
            "assistant_conversations",
            "communautes",
            "membres_communaute",
            "messages"
        ]
        
        imported_count = 0
        skipped_count = 0
        
        # Importer chaque collection
        for collection_name in collections_to_import:
            json_file = export_dir / f"{collection_name}.json"
            try:
                if import_collection(db, collection_name, json_file):
                    imported_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                print(f"   ❌ Erreur lors de l'import de {collection_name}: {e}")
                skipped_count += 1
        
        # Résumé
        print("\n" + "=" * 60)
        print("✅ Import terminé!")
        print(f"📊 Résumé:")
        print(f"   ✅ {imported_count} collections importées")
        print(f"   ⚠️  {skipped_count} collections ignorées")
        print("=" * 60)
        print("\n💡 Prochaines étapes:")
        print("   1. Vérifiez que les données sont bien importées")
        print("   2. Si nécessaire, recalculez les embeddings:")
        print("      python backend/scripts/compute_embeddings.py --translation lsg")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'import: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()
            print("\n🔌 Connexion MongoDB fermée")


if __name__ == "__main__":
    main()

