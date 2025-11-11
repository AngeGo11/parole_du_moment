#!/usr/bin/env python3
"""
Script d'export MongoDB pour sauvegarder toutes les données.
Utile pour migrer les données vers un autre ordinateur.
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


def export_collection(db, collection_name, output_dir):
    """Exporte une collection MongoDB vers un fichier JSON."""
    collection = db[collection_name]
    
    print(f"\n📤 Export de {collection_name}...")
    
    # Compter les documents
    count = collection.count_documents({})
    print(f"   📊 {count} documents trouvés")
    
    if count == 0:
        print(f"   ⚠️  Collection vide, ignorée")
        return False
    
    # Récupérer tous les documents
    documents = list(collection.find({}))
    
    # Convertir ObjectId en string pour JSON
    json_data = json.loads(json_util.dumps(documents))
    
    # Sauvegarder dans un fichier JSON
    output_file = output_dir / f"{collection_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Exporté vers {output_file}")
    return True


def main():
    """Fonction principale."""
    print("=" * 60)
    print("🚀 Export MongoDB - Sauvegarde des données")
    print("=" * 60)
    
    # Initialiser MongoDB
    db, client = init_mongodb()
    if db is None or client is None:
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    try:
        # Créer le répertoire d'export
        dataset_dir = Path(__file__).parent
        export_dir = dataset_dir / "mongodb_export"
        export_dir.mkdir(exist_ok=True)
        
        print(f"\n📁 Répertoire d'export: {export_dir}")
        
        # Liste des collections à exporter
        collections_to_export = [
            "versets",
            "emotions",
            "themes",
            "versets_emotions",
            "versets_themes",
            "traductions",
            "livres",
            "testaments",
            "profiles",
            "verse_history",
            "favorite_verses",
            "assistant_conversations",
            "users",
            "communautes",
            "membres_communaute",
            "messages"
        ]
        
        exported_count = 0
        skipped_count = 0
        
        # Exporter chaque collection
        for collection_name in collections_to_export:
            try:
                if export_collection(db, collection_name, export_dir):
                    exported_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                print(f"   ❌ Erreur lors de l'export de {collection_name}: {e}")
                skipped_count += 1
        
        # Créer un fichier README avec les instructions
        readme_content = f"""# Export MongoDB - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Instructions pour réimporter les données

### Option 1 : Utiliser mongorestore (Recommandé)

```bash
# Sur le nouvel ordinateur, restaurer depuis les fichiers BSON
mongorestore --db parole_du_moment_db --dir mongodb_export/
```

### Option 2 : Utiliser le script d'import Python

```bash
# Les fichiers JSON peuvent être réimportés avec import_all_data.py
python backend/scripts/import_all_data.py
```

### Option 3 : Utiliser MongoDB Atlas (Cloud)

Pour éviter de réimporter à chaque changement d'ordinateur :

1. Créez un compte gratuit sur https://www.mongodb.com/cloud/atlas
2. Créez un cluster gratuit (M0)
3. Modifiez MONGODB_URL dans votre .env :
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   ```

## Collections exportées

- versets : {db.versets.count_documents({})} documents
- emotions : {db.emotions.count_documents({})} documents
- themes : {db.themes.count_documents({})} documents
- versets_emotions : {db.versets_emotions.count_documents({})} documents
- versets_themes : {db.versets_themes.count_documents({})} documents
- traductions : {db.traductions.count_documents({})} documents
- livres : {db.livres.count_documents({})} documents
- testaments : {db.testaments.count_documents({})} documents
- profiles : {db.profiles.count_documents({})} documents
- verse_history : {db.verse_history.count_documents({})} documents
- favorite_verses : {db.favorite_verses.count_documents({})} documents
- assistant_conversations : {db.assistant_conversations.count_documents({})} documents

## Notes importantes

⚠️ Les embeddings vectoriels sont inclus dans les versets exportés.
⚠️ Après réimport, vous devrez peut-être recalculer les embeddings si nécessaire.
⚠️ Les ObjectId MongoDB sont préservés dans les fichiers JSON.
"""
        
        readme_file = export_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Résumé
        print("\n" + "=" * 60)
        print("✅ Export terminé!")
        print(f"📊 Résumé:")
        print(f"   ✅ {exported_count} collections exportées")
        print(f"   ⚠️  {skipped_count} collections ignorées (vides ou erreurs)")
        print(f"📁 Fichiers sauvegardés dans: {export_dir}")
        print("=" * 60)
        print("\n💡 Pour réimporter sur un autre ordinateur:")
        print("   1. Copiez le dossier 'mongodb_export' sur le nouvel ordinateur")
        print("   2. Utilisez mongorestore ou le script d'import Python")
        print("   3. Ou mieux: utilisez MongoDB Atlas (cloud) pour éviter les réimports")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'export: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()
            print("\n🔌 Connexion MongoDB fermée")


if __name__ == "__main__":
    main()

