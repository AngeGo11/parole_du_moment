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
    from pymongo.operations import UpdateOne, InsertOne
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️  MongoDB non disponible - installez pymongo")

def load_json_data(file_path):
    """
    Charge les données JSON depuis un fichier.
    
    Cette fonction gère automatiquement les erreurs de fichier non trouvé
    et les erreurs de parsing JSON pour éviter que le script ne plante.
    
    Args:
        file_path (Path): Chemin vers le fichier JSON à charger
    
    Returns:
        list: Liste des données chargées, ou liste vide en cas d'erreur
    """
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
    """
    Charge et traite les données bibliques depuis les fichiers JSON.
    
    Cette fonction :
    - Charge tous les fichiers bibliques disponibles dans différents formats
    - Extrait les versets avec leurs métadonnées (livre, chapitre, verset)
    - Génère des références uniques pour chaque verset
    - Extrait les mots-clés automatiquement
    
    Args:
        bible_dir (Path): Répertoire contenant les fichiers JSON bibliques
    
    Returns:
        list: Liste de dictionnaires contenant les données de chaque verset
    """
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
    """
    Initialise la connexion MongoDB.
    
    Configure la connexion à MongoDB en utilisant la configuration par défaut
    (localhost:27017). La base de données utilisée est 'parole_du_moment_db'.
    
    Returns:
        Database: Objet database MongoDB, ou None en cas d'erreur
    """
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
    """
    Convertit une chaîne de date ISO en objet datetime Python.
    
    Gère les formats ISO avec ou sans le 'Z' final (UTC).
    En cas d'erreur, retourne la date/heure actuelle.
    
    Args:
        date_str (str): Chaîne de date au format ISO (ex: "2024-01-01T12:00:00Z")
    
    Returns:
        datetime: Objet datetime Python
    """
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

def get_testament_mapping(db):
    """
    Crée un mapping entre les strings testament_id et les ObjectId MongoDB.
    
    Cette fonction est nécessaire car les fichiers JSON utilisent des strings
    comme 'ancien_testament' et 'nouveau_testament', alors que MongoDB utilise
    des ObjectId. Elle crée un mapping pour convertir ces strings en ObjectId.
    
    Args:
        db: Connexion MongoDB
    
    Returns:
        dict: Dictionnaire {string_id: ObjectId} pour chaque testament
    """
    if db is None:
        return {}
    
    mapping = {}
    collection = db['testaments']
    
    # Mapping entre les strings dans livres.json et les noms dans testaments.json
    testament_string_to_name = {
        'ancien_testament': 'Ancien Testament',
        'nouveau_testament': 'Nouveau Testament'
    }
    
    try:
        for string_id, nom in testament_string_to_name.items():
            testament = collection.find_one({'nom': nom})
            if testament:
                mapping[string_id] = testament['_id']
                print(f"   ✓ Mapping: '{string_id}' -> {testament['_id']} ({nom})")
            else:
                print(f"   ⚠️  Testament '{nom}' non trouvé dans la base")
    except Exception as e:
        print(f"   ❌ Erreur lors de la création du mapping: {e}")
    
    return mapping

def convert_testament_ids(livres_data, testament_mapping):
    """
    Convertit les strings testament_id en ObjectId pour les livres.
    
    Modifie directement les données des livres pour remplacer les strings
    testament_id par les ObjectId correspondants obtenus depuis MongoDB.
    
    Args:
        livres_data (list): Liste des dictionnaires de livres à convertir
        testament_mapping (dict): Mapping {string_id: ObjectId} des testaments
    
    Returns:
        list: Liste des livres avec les testament_id convertis en ObjectId
    """
    if not livres_data or not testament_mapping:
        return livres_data
    
    converted_count = 0
    for livre in livres_data:
        if 'testament_id' in livre:
            testament_id = livre['testament_id']
            # Si c'est une string et qu'on a un mapping pour elle
            if isinstance(testament_id, str) and testament_id in testament_mapping:
                livre['testament_id'] = testament_mapping[testament_id]
                converted_count += 1
            elif isinstance(testament_id, str):
                print(f"   ⚠️  Testament_id '{testament_id}' non trouvé dans le mapping")
    
    if converted_count > 0:
        print(f"   ✓ {converted_count} testament_id convertis en ObjectId")
    
    return livres_data

def get_unique_fields(collection_name):
    """
    Retourne les champs uniques pour chaque collection.
    
    Ces champs sont utilisés pour :
    - Détecter les doublons lors de l'importation
    - Trouver le point de reprise après une interruption
    
    Returns:
        list: Liste des champs uniques pour la collection
    """
    unique_fields_map = {
        'testaments': ['nom'],
        'livres': ['abreviation'],
        'traductions': ['abreviation'],
        'themes': ['nom'],
        'emotions': ['nom'],
        'versets': ['ref_unique'],  # Utilise ref_unique si disponible, sinon utilise la combinaison ci-dessous
        'users': ['email'],
        'communautes': ['nom'],
        'versets_themes': ['verset_id', 'theme_id'],
        'versets_emotions': ['verset_id', 'emotion_id'],
        'membres_communaute': ['communaute_id', 'utilisateur_id'],
        'messages': []  # Pas de champ unique défini, utiliser _id si nécessaire
    }
    return unique_fields_map.get(collection_name, [])


def find_resume_index(db, collection_name, data, unique_fields, date_fields=None):
    """
    Trouve l'index de reprise pour une collection de manière optimisée.
    
    Cette fonction utilise une approche optimisée :
    - Pour les collections avec un seul champ unique (comme ref_unique), charge tous les IDs existants en une requête
    - Utilise une recherche binaire pour trouver rapidement le point de reprise
    - Pour les autres cas, utilise une recherche par batch pour réduire le nombre de requêtes
    
    Args:
        db: Connexion MongoDB
        collection_name (str): Nom de la collection MongoDB
        data (list): Liste des données à importer (dans l'ordre)
        unique_fields (list): Liste des champs uniques pour identifier les doublons
        date_fields (list, optional): Liste des champs de date à convertir
    
    Returns:
        int: Index de départ pour reprendre l'importation (0 si tout est à importer)
    """
    if db is None or not data or not unique_fields:
        # Si pas de champs uniques, on ne peut pas détecter la reprise
        return 0
    
    collection = db[collection_name]
    date_fields = date_fields or ['created_at']
    
    # OPTIMISATION : Si on a un seul champ unique (comme ref_unique pour les versets)
    # On charge TOUS les IDs existants en une seule requête pour une détection précise
    if len(unique_fields) == 1:
        unique_field = unique_fields[0]
        
        print(f"   📥 Chargement de tous les {unique_field} existants depuis MongoDB...")
        
        # OPTIMISATION MAJEURE : Charger TOUS les ref_unique existants en une seule requête
        # Cela permet de détecter précisément le point de reprise même si les éléments
        # ont été importés dans un ordre différent ou lors d'une session précédente
        existing_docs = collection.find(
            {},  # Pas de filtre, on veut tous les documents
            {unique_field: 1, '_id': 0}  # Seulement le champ unique, pas besoin du _id
        )
        
        # Créer un set de toutes les valeurs existantes pour une recherche O(1)
        existing_values = set()
        count = 0
        for doc in existing_docs:
            value = doc.get(unique_field)
            if value is not None:
                existing_values.add(value)
            count += 1
            # Afficher la progression tous les 50000 éléments pour les grandes collections
            if count % 50000 == 0:
                print(f"   📊 {count} éléments chargés...")
        
        print(f"   ✓ {len(existing_values)} valeurs uniques trouvées dans MongoDB")
        
        # Maintenant parcourir les données dans l'ordre pour trouver le premier élément manquant
        print(f"   🔍 Recherche du point de reprise dans {len(data)} éléments à importer...")
        for index, item in enumerate(data):
            try:
                test_item = item.copy()
                for field in date_fields:
                    if field in test_item and isinstance(test_item[field], str):
                        test_item[field] = convert_date_string(test_item[field])
                
                value = test_item.get(unique_field)
                
                # Si la valeur n'est pas dans les éléments existants, c'est notre point de reprise
                if value not in existing_values:
                    print(f"   ✓ Point de reprise trouvé à l'index {index} (valeur: {value})")
                    return index
                
                # Afficher la progression tous les 10000 éléments
                if (index + 1) % 10000 == 0:
                    print(f"   📊 Vérification: {index + 1}/{len(data)} éléments vérifiés...")
                        
            except Exception as e:
                print(f"   ⚠️  Erreur lors de la vérification de l'index {index}: {e}")
                return index
        
        # Tous les éléments existent déjà
        print(f"   ✓ Tous les {len(data)} éléments existent déjà dans MongoDB")
        return len(data)
    
    else:
        # CAS MULTI-CHAMPS : Pour les collections avec plusieurs champs uniques
        # On utilise une recherche par batch pour réduire les requêtes
        batch_size = 100  # Vérifier par batch de 100 éléments
        
        for batch_start in range(0, len(data), batch_size):
            batch = data[batch_start:batch_start + batch_size]
            
            # Construire les filtres pour ce batch
            filters = []
            for item in batch:
                try:
                    test_item = item.copy()
                    for field in date_fields:
                        if field in test_item and isinstance(test_item[field], str):
                            test_item[field] = convert_date_string(test_item[field])
                    
                    filter_dict = {field: test_item.get(field) for field in unique_fields if field in test_item}
                    
                    # Pour les versets, si ref_unique n'existe pas, utiliser la combinaison des champs
                    if collection_name == 'versets' and not filter_dict.get('ref_unique'):
                        alt_fields = ['traduction_id', 'livre_id', 'chapitre', 'numero']
                        filter_dict = {field: test_item.get(field) for field in alt_fields if field in test_item}
                    
                    if filter_dict:
                        filters.append(filter_dict)
                except Exception:
                    continue
            
            if filters:
                # Utiliser $or pour vérifier tous les éléments du batch en une requête
                or_query = {'$or': filters}
                existing_count = collection.count_documents(or_query)
                
                # Si tous les éléments du batch n'existent pas, trouver le premier manquant
                if existing_count < len(batch):
                    # Parcourir ce batch pour trouver le premier élément manquant
                    for i, item in enumerate(batch):
                        try:
                            test_item = item.copy()
                            for field in date_fields:
                                if field in test_item and isinstance(test_item[field], str):
                                    test_item[field] = convert_date_string(test_item[field])
                            
                            filter_dict = {field: test_item.get(field) for field in unique_fields if field in test_item}
                            
                            if collection_name == 'versets' and not filter_dict.get('ref_unique'):
                                alt_fields = ['traduction_id', 'livre_id', 'chapitre', 'numero']
                                filter_dict = {field: test_item.get(field) for field in alt_fields if field in test_item}
                            
                            if filter_dict:
                                existing = collection.find_one(filter_dict)
                                if not existing:
                                    return batch_start + i
                        except Exception:
                            continue
            
            # Si tous les éléments de ce batch existent, continuer
    
    # Tous les éléments existent déjà
    return len(data)

def import_collection_mongodb(db, collection_name, data, date_fields=None, auto_resume=True):
    """
    Importe une collection dans MongoDB en évitant les doublons et avec reprise automatique.
    
    Cette fonction permet d'importer des données dans MongoDB avec les fonctionnalités suivantes :
    - Détection automatique des doublons grâce aux champs uniques
    - Reprise automatique après interruption (si auto_resume=True)
    - Importation par batch pour les grandes collections (optimisation des performances)
    - Gestion des erreurs individuelle pour chaque élément
    
    Args:
        db: Connexion MongoDB
        collection_name (str): Nom de la collection MongoDB cible
        data (list): Liste des données à importer
        date_fields (list, optional): Liste des champs de date à convertir en datetime
        auto_resume (bool): Si True, détecte automatiquement le point de reprise
    
    Returns:
        dict: Statistiques de l'importation {'inserted': int, 'updated': int, 'skipped': int}
    """
    if db is None or not data:
        return {'inserted': 0, 'updated': 0, 'skipped': 0}
    
    collection = db[collection_name]
    date_fields = date_fields or ['created_at']
    unique_fields = get_unique_fields(collection_name)
    
    print(f"🍃 Importation de {len(data)} éléments dans MongoDB/{collection_name}...")
    
    # DÉTECTION AUTOMATIQUE DU POINT DE REPRISE
    # Si auto_resume est activé et qu'on a des champs uniques, on cherche où reprendre
    start_index = 0
    original_data_length = len(data)  # Sauvegarder la longueur originale pour les calculs de batch
    if auto_resume and unique_fields:
        print(f"   🔍 Recherche du point de reprise...")
        start_index = find_resume_index(db, collection_name, data, unique_fields, date_fields)
        
        if start_index > 0:
            if start_index >= len(data):
                print(f"   ✓ Tous les éléments sont déjà importés ({len(data)}/{len(data)})")
                return {'inserted': 0, 'updated': 0, 'skipped': len(data)}
            else:
                print(f"   🔄 Reprise à partir de l'élément {start_index + 1}/{len(data)} ({start_index} éléments déjà importés)")
                data = data[start_index:]  # Ne garder que les éléments restants
    
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    
    # IMPORTATION PAR BATCH POUR LES GRANDES COLLECTIONS
    # Traiter par batch de 5000 éléments pour optimiser les performances
    batch_size = 5000
    if len(data) > batch_size:
        print(f"   📦 Importation par batch de {batch_size} éléments avec bulk_write()...")
        
        # Parcourir les données par batch (0, 5000, 10000, etc.)
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_inserted = 0
            batch_updated = 0
            batch_skipped = 0
            
            # Construire la liste des opérations bulk pour ce batch
            # Cela permet d'envoyer jusqu'à 5000 opérations en une seule requête réseau
            bulk_operations = []
            
            for item in batch:
                try:
                    # Convertir les champs de date en objets datetime MongoDB
                    processed_item = item.copy()
                    for field in date_fields:
                        if field in processed_item and isinstance(processed_item[field], str):
                            processed_item[field] = convert_date_string(processed_item[field])
                    
                    # CONSTRUCTION DU FILTRE ANTI-DOUBLON
                    # Si on a des champs uniques définis, on les utilise pour éviter les doublons
                    if unique_fields:
                        filter_dict = {field: processed_item.get(field) for field in unique_fields if field in processed_item}
                        
                        # Cas spécial pour les versets : utiliser ref_unique ou combinaison de champs
                        if collection_name == 'versets' and not filter_dict.get('ref_unique'):
                            alt_fields = ['traduction_id', 'livre_id', 'chapitre', 'numero']
                            filter_dict = {field: processed_item.get(field) for field in alt_fields if field in processed_item}
                        
                        if filter_dict:
                            # UPSERT : créer une opération UpdateOne avec upsert=True
                            # Cela évite les doublons tout en permettant les mises à jour
                            bulk_operations.append(
                                UpdateOne(
                                    filter_dict,
                                    {'$set': processed_item},
                                    upsert=True
                                )
                            )
                        else:
                            # Pas de champs uniques disponibles, insertion directe
                            bulk_operations.append(InsertOne(processed_item))
                    else:
                        # Pas de champ unique défini, insertion directe
                        bulk_operations.append(InsertOne(processed_item))
                        
                except Exception as e:
                    # Gestion des erreurs : on continue avec les autres éléments
                    print(f"   ⚠️  Erreur lors de la préparation de l'élément: {e}")
                    batch_skipped += 1
            
            # EXÉCUTER TOUTES LES OPÉRATIONS DU BATCH EN UNE SEULE REQUÊTE
            # C'est ici que se fait l'optimisation : au lieu de 5000 requêtes, on en fait 1 seule !
            if bulk_operations:
                try:
                    result = collection.bulk_write(bulk_operations, ordered=False)
                    
                    # Analyser les résultats pour les statistiques
                    # Note: bulk_write ne retourne pas le détail upserted_id/modified_count par élément
                    # On utilise les compteurs globaux du résultat
                    batch_inserted = result.inserted_count + result.upserted_count
                    batch_updated = result.modified_count
                    batch_skipped = len(bulk_operations) - batch_inserted - batch_updated
                    
                except Exception as e:
                    # En cas d'erreur sur le bulk_write, on peut essayer de traiter individuellement
                    # mais cela ne devrait normalement pas arriver
                    print(f"   ⚠️  Erreur lors du bulk_write: {e}")
                    print(f"   ⚠️  Tentative de traitement individuel du batch...")
                    
                    # Fallback : traitement individuel en cas d'erreur
                    for item in batch:
                        try:
                            processed_item = item.copy()
                            for field in date_fields:
                                if field in processed_item and isinstance(processed_item[field], str):
                                    processed_item[field] = convert_date_string(processed_item[field])
                            
                            if unique_fields:
                                filter_dict = {field: processed_item.get(field) for field in unique_fields if field in processed_item}
                                
                                if collection_name == 'versets' and not filter_dict.get('ref_unique'):
                                    alt_fields = ['traduction_id', 'livre_id', 'chapitre', 'numero']
                                    filter_dict = {field: processed_item.get(field) for field in alt_fields if field in processed_item}
                                
                                if filter_dict:
                                    result = collection.update_one(filter_dict, {'$set': processed_item}, upsert=True)
                                    if result.upserted_id:
                                        batch_inserted += 1
                                    elif result.modified_count > 0:
                                        batch_updated += 1
                                    else:
                                        batch_skipped += 1
                                else:
                                    collection.insert_one(processed_item)
                                    batch_inserted += 1
                            else:
                                collection.insert_one(processed_item)
                                batch_inserted += 1
                        except Exception as e2:
                            batch_skipped += 1
            
            # Mettre à jour les compteurs globaux et afficher la progression
            inserted_count += batch_inserted
            updated_count += batch_updated
            skipped_count += batch_skipped
            
            # Calculer le numéro de batch réel (en tenant compte du start_index)
            # i est l'index dans les données tronquées, start_index + i donne l'index global
            batch_num = (start_index + i) // batch_size + 1
            total_batches = (original_data_length + batch_size - 1) // batch_size
            print(f"   ✓ Batch {batch_num}/{total_batches}: {batch_inserted} ajoutés, {batch_updated} mis à jour, {batch_skipped} ignorés")
    else:
        # IMPORTATION STANDARD POUR LES PETITES COLLECTIONS
        # Pour les collections < 5000 éléments, utiliser bulk_write() aussi pour optimiser
        bulk_operations = []
        
        for item in data:
            try:
                # Convertir les champs de date
                processed_item = item.copy()
                for field in date_fields:
                    if field in processed_item and isinstance(processed_item[field], str):
                        processed_item[field] = convert_date_string(processed_item[field])
                
                # Construire le filtre pour éviter les doublons
                if unique_fields:
                    filter_dict = {field: processed_item.get(field) for field in unique_fields if field in processed_item}
                    
                    # Pour les versets, si ref_unique n'existe pas, utiliser la combinaison des champs
                    if collection_name == 'versets' and not filter_dict.get('ref_unique'):
                        alt_fields = ['traduction_id', 'livre_id', 'chapitre', 'numero']
                        filter_dict = {field: processed_item.get(field) for field in alt_fields if field in processed_item}
                    
                    if filter_dict:
                        # Utiliser UpdateOne avec upsert pour éviter les doublons
                        bulk_operations.append(
                            UpdateOne(filter_dict, {'$set': processed_item}, upsert=True)
                        )
                    else:
                        # Si les champs uniques ne sont pas présents, insérer directement
                        bulk_operations.append(InsertOne(processed_item))
                else:
                    # Pas de champ unique défini, insérer directement
                    bulk_operations.append(InsertOne(processed_item))
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                skipped_count += 1
        
        # Exécuter toutes les opérations en une seule requête bulk_write
        if bulk_operations:
            try:
                result = collection.bulk_write(bulk_operations, ordered=False)
                batch_inserted = result.inserted_count + result.upserted_count
                batch_updated = result.modified_count
                batch_skipped = len(bulk_operations) - batch_inserted - batch_updated
                
                inserted_count += batch_inserted
                updated_count += batch_updated
                skipped_count += batch_skipped
                
                # Afficher les détails pour chaque élément (si peu d'éléments)
                if len(bulk_operations) <= 100:
                    for item in data:
                        item_name = item.get('nom', item.get('email', item.get('ref_unique', 'élément')))
                        print(f"   ✓ {item_name} traité")
            except Exception as e:
                print(f"   ⚠️  Erreur lors du bulk_write: {e}")
                # Fallback : traitement individuel
                for item in data:
                    try:
                        processed_item = item.copy()
                        for field in date_fields:
                            if field in processed_item and isinstance(processed_item[field], str):
                                processed_item[field] = convert_date_string(processed_item[field])
                        
                        if unique_fields:
                            filter_dict = {field: processed_item.get(field) for field in unique_fields if field in processed_item}
                            
                            if collection_name == 'versets' and not filter_dict.get('ref_unique'):
                                alt_fields = ['traduction_id', 'livre_id', 'chapitre', 'numero']
                                filter_dict = {field: processed_item.get(field) for field in alt_fields if field in processed_item}
                            
                            if filter_dict:
                                result = collection.update_one(filter_dict, {'$set': processed_item}, upsert=True)
                                if result.upserted_id:
                                    inserted_count += 1
                                elif result.modified_count > 0:
                                    updated_count += 1
                                else:
                                    skipped_count += 1
                            else:
                                result = collection.insert_one(processed_item)
                                inserted_count += 1
                        else:
                            result = collection.insert_one(processed_item)
                            inserted_count += 1
                    except Exception as e2:
                        print(f"   ❌ Erreur: {e2}")
                        skipped_count += 1
    
    # AFFICHAGE DU RÉSUMÉ FINAL
    print(f"   📊 Résumé: {inserted_count} ajoutés, {updated_count} mis à jour, {skipped_count} ignorés")
    
    return {'inserted': inserted_count, 'updated': updated_count, 'skipped': skipped_count}

def main():
    """Fonction principale"""
    print("🚀 Début de l'importation complète des données...")
    print("=" * 60)
    
    # Chemin vers les fichiers de données
    dataset_dir = Path(__file__).parent.parent / "dataset"
    bible_dir = dataset_dir / "bible" / "json"
    
    # Définir les collections et leurs champs de date
    collections = {
        'traductions.json': {
            'mongodb_collection': 'traductions',
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
            'mongodb_collection': 'users',
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
    
    # D'abord importer les testaments pour créer le mapping
    print("\n📋 Étape 1: Importation des testaments...")
    if 'testaments.json' in collections:
        testaments_data = all_data.get('testaments.json', [])
        if testaments_data:
            import_collection_mongodb(
                mongodb_db,
                collections['testaments.json']['mongodb_collection'],
                testaments_data,
                collections['testaments.json']['date_fields']
            )
    
    # Créer le mapping testament_id string -> ObjectId
    print("\n🔗 Étape 2: Création du mapping testament_id...")
    testament_mapping = get_testament_mapping(mongodb_db)
    
    # Importer les autres collections normales
    print("\n📚 Étape 3: Importation des autres collections...")
    for filename, config in collections.items():
        # Skip testaments car déjà importés
        if filename == 'testaments.json':
            continue
            
        data = all_data[filename]
        if data:
            # Convertir les testament_id pour les livres
            if filename == 'livres.json':
                data = convert_testament_ids(data, testament_mapping)
            
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