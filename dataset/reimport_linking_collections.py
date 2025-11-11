#!/usr/bin/env python3
"""
Script de réimportation des collections versets_themes et versets_emotions
avec correction des IDs pour utiliser les ObjectId MongoDB réels.
"""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from pymongo import MongoClient
    from pymongo.operations import UpdateOne, InsertOne
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("❌ MongoDB non disponible - installez pymongo")


def load_json_data(file_path):
    """Charge les données JSON depuis un fichier."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON dans {file_path}: {e}")
        return []


def convert_date_string(date_str):
    """Convertit une chaîne de date ISO en objet datetime Python."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return datetime.now()


def init_mongodb():
    """Initialise la connexion MongoDB."""
    if not MONGODB_AVAILABLE:
        return None
    
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


def create_id_mappings(db):
    """Crée les mappings entre les anciens IDs (strings) et les ObjectId MongoDB."""
    
    print("\n🔍 Création des mappings d'IDs...")
    
    # Mapping versets: verset_001, verset_002, etc. → ObjectId
    print("   📖 Chargement des versets...")
    versets = list(db.versets.find({}, {"_id": 1, "ref_unique": 1}).sort("ref_unique"))
    verset_mapping = {}
    for idx, verset in enumerate(versets, start=1):
        old_id = f"verset_{idx:03d}"  # verset_001, verset_002, etc.
        verset_mapping[old_id] = verset["_id"]
    print(f"   ✅ {len(verset_mapping)} versets mappés")
    
    # Mapping emotions: emotion_1, emotion_2, etc. → ObjectId
    print("   😊 Chargement des émotions...")
    emotions = list(db.emotions.find({}, {"_id": 1, "nom": 1}).sort("nom"))
    emotion_mapping = {}
    for idx, emotion in enumerate(emotions, start=1):
        old_id = f"emotion_{idx}"
        emotion_mapping[old_id] = emotion["_id"]
    print(f"   ✅ {len(emotion_mapping)} émotions mappées")
    
    # Mapping themes: theme_1, theme_2, etc. → ObjectId
    print("   🎨 Chargement des thèmes...")
    themes = list(db.themes.find({}, {"_id": 1, "nom": 1}).sort("nom"))
    theme_mapping = {}
    for idx, theme in enumerate(themes, start=1):
        old_id = f"theme_{idx}"
        theme_mapping[old_id] = theme["_id"]
    print(f"   ✅ {len(theme_mapping)} thèmes mappés")
    
    return verset_mapping, emotion_mapping, theme_mapping


def reimport_collection(db, collection_name, json_data, verset_mapping, id_mapping, id_field_name):
    """Réimporte une collection de liaison avec les bons ObjectId."""
    
    print(f"\n🔄 Réimportation de {collection_name}...")
    
    collection = db[collection_name]
    
    # Supprimer toutes les données existantes
    print(f"   🗑️  Suppression des données existantes...")
    result = collection.delete_many({})
    print(f"   ✅ {result.deleted_count} documents supprimés")
    
    # Préparer les nouveaux documents
    new_documents = []
    skipped_count = 0
    
    for item in json_data:
        old_verset_id = item.get("verset_id")
        old_id = item.get(id_field_name)  # emotion_id ou theme_id
        
        # Mapper vers les ObjectId
        verset_object_id = verset_mapping.get(old_verset_id)
        id_object_id = id_mapping.get(old_id)
        
        if not verset_object_id:
            print(f"   ⚠️  Verset ID '{old_verset_id}' non trouvé dans le mapping")
            skipped_count += 1
            continue
        
        if not id_object_id:
            print(f"   ⚠️  {id_field_name} '{old_id}' non trouvé dans le mapping")
            skipped_count += 1
            continue
        
        # Créer le nouveau document
        new_doc = {
            "verset_id": verset_object_id,
            id_field_name: id_object_id,
            "poids_ia": item.get("poids_ia", 0.0),
            "created_at": convert_date_string(item.get("created_at", datetime.now().isoformat()))
        }
        
        new_documents.append(new_doc)
    
    # Insérer les nouveaux documents
    if new_documents:
        print(f"   💾 Insertion de {len(new_documents)} documents...")
        collection.insert_many(new_documents)
        print(f"   ✅ {len(new_documents)} documents insérés")
    else:
        print(f"   ⚠️  Aucun document à insérer")
    
    if skipped_count > 0:
        print(f"   ⚠️  {skipped_count} documents ignorés (IDs non trouvés)")
    
    return len(new_documents), skipped_count


def main():
    """Fonction principale."""
    print("=" * 60)
    print("🚀 Réimportation des collections de liaison")
    print("   versets_themes et versets_emotions")
    print("=" * 60)
    
    # Initialiser MongoDB
    db, client = init_mongodb()
    if db is None or client is None:
        print("❌ Impossible de se connecter à MongoDB")
        return
    
    try:
        # Charger les fichiers JSON
        dataset_dir = Path(__file__).parent
        versets_emotions_file = dataset_dir / "versets_emotions.json"
        versets_themes_file = dataset_dir / "versets_themes.json"
        
        print("\n📂 Chargement des fichiers JSON...")
        versets_emotions_data = load_json_data(versets_emotions_file)
        versets_themes_data = load_json_data(versets_themes_file)
        
        print(f"   ✅ {len(versets_emotions_data)} liaisons versets_emotions chargées")
        print(f"   ✅ {len(versets_themes_data)} liaisons versets_themes chargées")
        
        # Créer les mappings
        verset_mapping, emotion_mapping, theme_mapping = create_id_mappings(db)
        
        # Réimporter versets_emotions
        inserted_emotions, skipped_emotions = reimport_collection(
            db,
            "versets_emotions",
            versets_emotions_data,
            verset_mapping,
            emotion_mapping,
            "emotion_id"
        )
        
        # Réimporter versets_themes
        inserted_themes, skipped_themes = reimport_collection(
            db,
            "versets_themes",
            versets_themes_data,
            verset_mapping,
            theme_mapping,
            "theme_id"
        )
        
        # Résumé
        print("\n" + "=" * 60)
        print("✅ Réimportation terminée!")
        print(f"📊 Résumé:")
        print(f"   versets_emotions: {inserted_emotions} insérés, {skipped_emotions} ignorés")
        print(f"   versets_themes: {inserted_themes} insérés, {skipped_themes} ignorés")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la réimportation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            client.close()
            print("\n🔌 Connexion MongoDB fermée")


if __name__ == "__main__":
    main()

