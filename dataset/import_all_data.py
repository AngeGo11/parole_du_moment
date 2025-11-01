#!/usr/bin/env python3
"""
Script d'importation complet pour l'application Parole du Moment
Importe toutes les données de base dans Firestore et MongoDB
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    print("⚠️  Firestore non disponible - installez firebase-admin")

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️  MongoDB non disponible - installez pymongo")

def load_json_data(file_path):
    """Charge les données JSON depuis un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON dans {file_path}: {e}")
        return []

def load_bible_data(bible_dir):
    """Charge et traite les données bibliques depuis les fichiers JSON"""
    bible_data = []
    bible_files = [
        'fr_apee.json', 'en_kjv.json', 'en_bbe.json', 'es_rvr.json',
        'de_schlachter.json', 'pt_nvi.json', 'ru_synodal.json', 'zh_cuv.json',
        'ar_svd.json', 'ko_ko.json', 'vi_vietnamese.json', 'fi_finnish.json',
        'ro_cornilescu.json', 'el_greek.json', 'eo_esperanto.json'
    ]
    
    # Mapping des fichiers vers les versions
    version_mapping = {
        'fr_apee.json': 'LSG',
        'en_kjv.json': 'KJV', 
        'en_bbe.json': 'BBE',
        'es_rvr.json': 'RVR',
        'de_schlachter.json': 'SCH',
        'pt_nvi.json': 'NVI',
        'ru_synodal.json': 'SYN',
        'zh_cuv.json': 'CUV',
        'ar_svd.json': 'SVD',
        'ko_ko.json': 'KO',
        'vi_vietnamese.json': 'VI',
        'fi_finnish.json': 'FI',
        'ro_cornilescu.json': 'RO',
        'el_greek.json': 'GR',
        'eo_esperanto.json': 'EO'
    }
    
    # Mapping des noms de livres vers les IDs
    book_mapping = {
        'Genesis': 'gn', 'Exodus': 'ex', 'Leviticus': 'lv', 'Numbers': 'nb',
        'Deuteronomy': 'dt', 'Joshua': 'js', 'Judges': 'jg', 'Ruth': 'rt',
        '1 Samuel': '1s', '2 Samuel': '2s', '1 Kings': '1r', '2 Kings': '2r',
        '1 Chronicles': '1ch', '2 Chronicles': '2ch', 'Ezra': 'esd',
        'Nehemiah': 'ne', 'Esther': 'est', 'Job': 'job', 'Psalms': 'ps',
        'Proverbs': 'pr', 'Ecclesiastes': 'ec', 'Song of Solomon': 'ct',
        'Isaiah': 'es', 'Jeremiah': 'jer', 'Lamentations': 'la',
        'Ezekiel': 'ez', 'Daniel': 'da', 'Hosea': 'os', 'Joel': 'jl',
        'Amos': 'am', 'Obadiah': 'ab', 'Jonah': 'jon', 'Micah': 'mi',
        'Nahum': 'na', 'Habakkuk': 'hab', 'Zephaniah': 'so', 'Haggai': 'ag',
        'Zechariah': 'za', 'Malachi': 'mal', 'Matthew': 'mt', 'Mark': 'mr',
        'Luke': 'lu', 'John': 'jn', 'Acts': 'ac', 'Romans': 'ro',
        '1 Corinthians': '1co', '2 Corinthians': '2co', 'Galatians': 'ga',
        'Ephesians': 'ep', 'Philippians': 'ph', 'Colossians': 'col',
        '1 Thessalonians': '1th', '2 Thessalonians': '2th', '1 Timothy': '1ti',
        '2 Timothy': '2ti', 'Titus': 'tit', 'Philemon': 'phm', 'Hebrews': 'he',
        'James': 'ja', '1 Peter': '1pi', '2 Peter': '2pi', '1 John': '1jn',
        '2 John': '2jn', '3 John': '3jn', 'Jude': 'jud', 'Revelation': 'ap'
    }
    
    for bible_file in bible_files:
        file_path = bible_dir / bible_file
        if not file_path.exists():
            continue
            
        try:
            print(f"📖 Chargement de {bible_file}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            version_abbr = version_mapping.get(bible_file, 'UNK')
            
            # Traiter chaque livre
            for book in data:
                book_name = book.get('name', '')
                book_abbr = book_mapping.get(book_name, book_name.lower())
                chapters = book.get('chapters', [])
                
                for chapter_num, chapter in enumerate(chapters, 1):
                    for verse_num, verse_text in enumerate(chapter, 1):
                        if verse_text and verse_text.strip():
                            # Créer la référence unique
                            ref_unique = f"{book_abbr}.{chapter_num}.{verse_num}.{version_abbr}"
                            
                            # Extraire les mots-clés (mots de plus de 3 caractères)
                            words = verse_text.split()
                            mots_cles = [word.lower().strip('.,;:!?()[]"\'') 
                                       for word in words 
                                       if len(word.strip('.,;:!?()[]"\'')) > 3]
                            
                            verse_data = {
                                "traduction_id": version_abbr.lower(),
                                "livre_id": book_abbr,
                                "chapitre": chapter_num,
                                "numero": verse_num,
                                "contenu": verse_text.strip(),
                                "ref_unique": ref_unique,
                                "mots_cles": mots_cles[:10],  # Limiter à 10 mots-clés
                                "longueur": len(verse_text.strip()),
                                "created_at": datetime.now()
                            }
                            
                            bible_data.append(verse_data)
            
            print(f"   ✓ {len([v for v in bible_data if v['traduction_id'] == version_abbr.lower()])} versets chargés")
            
        except Exception as e:
            print(f"   ❌ Erreur lors du chargement de {bible_file}: {e}")
    
    print(f"📊 Total versets bibliques chargés: {len(bible_data)}")
    return bible_data

def init_mongodb():
    """Initialise la connexion MongoDB"""
    if not MONGODB_AVAILABLE:
        return None
    
    try:
        # Configuration MongoDB locale par défaut
        client = MongoClient('mongodb://localhost:27017/')
        db = client['parole_du_moment_db']
        return db
    except Exception as e:
        print(f"❌ Erreur d'initialisation MongoDB: {e}")
        return None

def convert_date_string(date_str):
    """Convertit une chaîne de date ISO en datetime"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return datetime.now()

def import_collection_firestore(db, collection_name, data, date_fields=None):
    """Importe une collection dans Firestore"""
    if not db or not data:
        return
    
    collection = db.collection(collection_name)
    date_fields = date_fields or ['created_at']
    
    print(f"🔥 Importation de {len(data)} éléments dans Firestore/{collection_name}...")
    
    for item in data:
        try:
            # Convertir les champs de date
            for field in date_fields:
                if field in item and isinstance(item[field], str):
                    item[field] = convert_date_string(item[field])
            
            # Ajouter l'élément
            doc_ref = collection.add(item)
            print(f"   ✓ {item.get('nom', item.get('email', 'élément'))} ajouté")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

def import_collection_mongodb(db, collection_name, data, date_fields=None):
    """Importe une collection dans MongoDB"""
    if db is None or not data:
        return
    
    collection = db[collection_name]
    date_fields = date_fields or ['created_at']
    
    print(f"🍃 Importation de {len(data)} éléments dans MongoDB/{collection_name}...")
    
    # Importation par batch pour les grandes collections
    batch_size = 1000
    if len(data) > batch_size:
        print(f"   📦 Importation par batch de {batch_size} éléments...")
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            try:
                # Convertir les champs de date pour le batch
                for item in batch:
                    for field in date_fields:
                        if field in item and isinstance(item[field], str):
                            item[field] = convert_date_string(item[field])
                
                result = collection.insert_many(batch)
                print(f"   ✓ Batch {i//batch_size + 1}: {len(result.inserted_ids)} éléments ajoutés")
                
            except Exception as e:
                print(f"   ❌ Erreur batch {i//batch_size + 1}: {e}")
    else:
        # Importation normale pour les petites collections
        for item in data:
            try:
                # Convertir les champs de date
                for field in date_fields:
                    if field in item and isinstance(item[field], str):
                        item[field] = convert_date_string(item[field])
                
                # Ajouter l'élément
                result = collection.insert_one(item)
                print(f"   ✓ {item.get('nom', item.get('email', 'élément'))} ajouté (ID: {result.inserted_id})")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Début de l'importation complète des données...")
    print("=" * 60)
    
    # Chemin vers les fichiers de données
    dataset_dir = Path(__file__).parent.parent / "dataset"
    bible_dir = dataset_dir / "bible" / "json"
    
    # Définir les collections et leurs champs de date
    collections = {
        'versions.json': {
            'mongodb_collection': 'versions',
            'date_fields': ['created_at']
        },
        'testaments.json': {
            'mongodb_collection': 'testaments',
            'date_fields': ['created_at']
        },
        'livres.json': {
            'mongodb_collection': 'livres',
            'date_fields': ['created_at']
        },
        'emotions.json': {
            'mongodb_collection': 'emotions',
            'date_fields': ['created_at']
        },
        'themes.json': {
            'mongodb_collection': 'themes',
            'date_fields': ['created_at']
        },
        'users.json': {
            'mongodb_collection': 'utilisateurs',
            'date_fields': ['created_at']
        },
        'communaute.json': {
            'mongodb_collection': 'communautes',
            'date_fields': ['date_creation', 'created_at']
        },
        'membres_communaute.json': {
            'mongodb_collection': 'membres_communaute',
            'date_fields': ['date_adhesion', 'created_at']
        },
        'messages.json': {
            'mongodb_collection': 'messages',
            'date_fields': ['date_envoi', 'created_at']
        },
        'versets_emotions.json': {
            'mongodb_collection': 'versets_emotions',
            'date_fields': ['created_at']
        },
        'versets_themes.json': {
            'mongodb_collection': 'versets_themes',
            'date_fields': ['created_at']
        }
    }
    
    # Charger toutes les données
    all_data = {}
    total_items = 0
    
    # Charger les données JSON normales
    for filename, config in collections.items():
        file_path = dataset_dir / filename
        data = load_json_data(file_path)
        all_data[filename] = data
        total_items += len(data)
        print(f"📊 {filename}: {len(data)} éléments chargés")
    
    # Charger les données bibliques
    print("\n📖 Chargement des données bibliques...")
    bible_data = load_bible_data(bible_dir)
    all_data['bible_versets'] = bible_data
    total_items += len(bible_data)
    
    if total_items == 0:
        print("❌ Aucune donnée trouvée à importer")
        return
    
    print(f"\n📈 Total: {total_items} éléments à importer")
    
    # Initialiser les connexions
    mongodb_db = init_mongodb()
    
    if mongodb_db is None:
        print("❌ MongoDB non disponible")
        return

    
    # Importation dans MongoDB
    print("\n🍃 IMPORTATION MONGODB")
    print("-" * 30)
    
    # Importer les collections normales
    for filename, config in collections.items():
        data = all_data[filename]
        if data:
            import_collection_mongodb(
                mongodb_db, 
                config['mongodb_collection'], 
                data, 
                config['date_fields']
            )
    
    # Importer les versets bibliques
    if bible_data:
        import_collection_mongodb(
            mongodb_db,
            'versets',
            bible_data,
            ['created_at']
        )
    
    print("\n" + "=" * 60)
    print("✅ Importation terminée avec succès!")
    print(f"📊 {total_items} éléments importés au total")
    print("🍃 Données disponibles dans MongoDB (parole_du_moment_db)")

def test_import():
    """Teste l'importation sans réellement importer"""
    print("🧪 Test de l'importation...")
    
    dataset_dir = Path(__file__).parent.parent / "dataset"
    bible_dir = dataset_dir / "bible" / "json"
    
    files_to_test = [
        'traductions.json',
        'testaments.json',
        'livres.json',
        'emotions.json',
        'themes.json', 
        'users.json',
        'communaute.json',
        'membres_communaute.json',
        'messages.json',
        'versets_emotions.json',
        'versets_themes.json'
    ]
    
    total_items = 0
    
    # Tester les fichiers JSON normaux
    for filename in files_to_test:
        file_path = dataset_dir / filename
        data = load_json_data(file_path)
        total_items += len(data)
        
        if data:
            print(f"✅ {filename}: {len(data)} éléments")
            # Afficher un échantillon
            sample = data[0] if data else {}
            if 'nom' in sample:
                print(f"   Exemple: {sample['nom']}")
            elif 'email' in sample:
                print(f"   Exemple: {sample['email']}")
        else:
            print(f"❌ {filename}: Aucune donnée")
    
    # Tester les données bibliques
    print("\n📖 Test des données bibliques...")
    bible_data = load_bible_data(bible_dir)
    total_items += len(bible_data)
    print(f"✅ Versets bibliques: {len(bible_data)} éléments")
    
    print(f"\n📊 Total: {total_items} éléments prêts à l'importation")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_import()
    else:
        main()