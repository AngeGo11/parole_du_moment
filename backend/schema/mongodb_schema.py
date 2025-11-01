"""
Schéma MongoDB pour les données bibliques
Optimisé pour les requêtes et la recherche
"""

from datetime import datetime
from typing import Dict, List, Any

# Structure des collections MongoDB
MONGODB_SCHEMA = {
    # Collection: traductions
    "traductions": {
        "indexes": [
            {"abreviation": 1},  # Index unique sur l'abréviation
            {"nom": 1}           # Index sur le nom
        ],
        "sample_document": {
            "_id": "ObjectId",
            "nom": "string",
            "abreviation": "string",
            "description": "string",
            "langue": "string",
            "created_at": "datetime",
            "updated_at": "datetime"
        }
    },
    
    # Collection: testaments
    "testaments": {
        "indexes": [
            {"nom": 1}  # Index unique sur le nom
        ],
        "sample_document": {
            "_id": "ObjectId",
            "nom": "string",
            "created_at": "datetime"
        }
    },
    
    # Collection: livres
    "livres": {
        "indexes": [
            {"testament_id": 1},     # Index sur testament
            {"abreviation": 1},      # Index unique sur l'abréviation
            {"ordre": 1}             # Index sur l'ordre
        ],
        "sample_document": {
            "_id": "ObjectId",
            "testament_id": "ObjectId",
            "nom": "string",
            "abreviation": "string",
            "ordre": "number",
            "created_at": "datetime"
        }
    },
    
    # Collection: versets (collection principale)
    "versets": {
        "indexes": [
            {"traduction_id": 1, "livre_id": 1, "chapitre": 1, "numero": 1},  # Index composé
            {"ref_unique": 1},      # Index unique sur la référence
            {"contenu": "text"},    # Index de recherche full-text
            {"traduction_id": 1},   # Index sur la traduction
            {"livre_id": 1},        # Index sur le livre
            {"chapitre": 1},        # Index sur le chapitre
            {"numero": 1}           # Index sur le numéro
        ],
        "sample_document": {
            "_id": "ObjectId",
            "traduction_id": "ObjectId",
            "livre_id": "ObjectId",
            "chapitre": "number",
            "numero": "number",
            "contenu": "string",
            "ref_unique": "string",
            "mots_cles": ["string"],  # Mots-clés extraits pour la recherche
            "longueur": "number",     # Longueur du verset
            "created_at": "datetime"
        }
    },
    
    # Collection: themes
    "themes": {
        "indexes": [
            {"nom": 1}  # Index unique sur le nom
        ],
        "sample_document": {
            "_id": "ObjectId",
            "nom": "string",
            "description": "string",
            "couleur": "string",  # Couleur pour l'interface
            "created_at": "datetime"
        }
    },
    
    # Collection: emotions
    "emotions": {
        "indexes": [
            {"nom": 1}  # Index unique sur le nom
        ],
        "sample_document": {
            "_id": "ObjectId",
            "nom": "string",
            "description": "string",
            "icone": "string",  # Icône pour l'interface
            "created_at": "datetime"
        }
    },
    
    # Collection: versets_themes (liaison)
    "versets_themes": {
        "indexes": [
            {"verset_id": 1, "theme_id": 1},  # Index composé
            {"verset_id": 1},
            {"theme_id": 1}
        ],
        "sample_document": {
            "_id": "ObjectId",
            "verset_id": "ObjectId",
            "theme_id": "ObjectId",
            "poids_ia": "number",
            "created_at": "datetime"
        }
    },
    
    # Collection: versets_emotions (liaison)
    "versets_emotions": {
        "indexes": [
            {"verset_id": 1, "emotion_id": 1},  # Index composé
            {"verset_id": 1},
            {"emotion_id": 1}
        ],
        "sample_document": {
            "_id": "ObjectId",
            "verset_id": "ObjectId",
            "emotion_id": "ObjectId",
            "poids_ia": "number",
            "created_at": "datetime"
        }
    }
}

# Mapping des livres bibliques (même structure que pour Firestore)
BIBLE_BOOKS = {
    "ancien_testament": [
        {"nom": "Genèse", "abreviation": "gn", "ordre": 1},
        {"nom": "Exode", "abreviation": "ex", "ordre": 2},
        {"nom": "Lévitique", "abreviation": "lv", "ordre": 3},
        {"nom": "Nombres", "abreviation": "nb", "ordre": 4},
        {"nom": "Deutéronome", "abreviation": "dt", "ordre": 5},
        {"nom": "Josué", "abreviation": "js", "ordre": 6},
        {"nom": "Juges", "abreviation": "jg", "ordre": 7},
        {"nom": "Ruth", "abreviation": "rt", "ordre": 8},
        {"nom": "1 Samuel", "abreviation": "1s", "ordre": 9},
        {"nom": "2 Samuel", "abreviation": "2s", "ordre": 10},
        {"nom": "1 Rois", "abreviation": "1r", "ordre": 11},
        {"nom": "2 Rois", "abreviation": "2r", "ordre": 12},
        {"nom": "1 Chroniques", "abreviation": "1ch", "ordre": 13},
        {"nom": "2 Chroniques", "abreviation": "2ch", "ordre": 14},
        {"nom": "Esdras", "abreviation": "esd", "ordre": 15},
        {"nom": "Néhémie", "abreviation": "ne", "ordre": 16},
        {"nom": "Esther", "abreviation": "est", "ordre": 17},
        {"nom": "Job", "abreviation": "job", "ordre": 18},
        {"nom": "Psaumes", "abreviation": "ps", "ordre": 19},
        {"nom": "Proverbes", "abreviation": "pr", "ordre": 20},
        {"nom": "Ecclésiaste", "abreviation": "ec", "ordre": 21},
        {"nom": "Cantique des Cantiques", "abreviation": "ct", "ordre": 22},
        {"nom": "Ésaïe", "abreviation": "es", "ordre": 23},
        {"nom": "Jérémie", "abreviation": "jer", "ordre": 24},
        {"nom": "Lamentations", "abreviation": "la", "ordre": 25},
        {"nom": "Ézéchiel", "abreviation": "ez", "ordre": 26},
        {"nom": "Daniel", "abreviation": "da", "ordre": 27},
        {"nom": "Osée", "abreviation": "os", "ordre": 28},
        {"nom": "Joël", "abreviation": "jl", "ordre": 29},
        {"nom": "Amos", "abreviation": "am", "ordre": 30},
        {"nom": "Abdias", "abreviation": "ab", "ordre": 31},
        {"nom": "Jonas", "abreviation": "jon", "ordre": 32},
        {"nom": "Michée", "abreviation": "mi", "ordre": 33},
        {"nom": "Nahum", "abreviation": "na", "ordre": 34},
        {"nom": "Habacuc", "abreviation": "hab", "ordre": 35},
        {"nom": "Sophonie", "abreviation": "so", "ordre": 36},
        {"nom": "Aggée", "abreviation": "ag", "ordre": 37},
        {"nom": "Zacharie", "abreviation": "za", "ordre": 38},
        {"nom": "Malachie", "abreviation": "mal", "ordre": 39}
    ],
    "nouveau_testament": [
        {"nom": "Matthieu", "abreviation": "mt", "ordre": 40},
        {"nom": "Marc", "abreviation": "mr", "ordre": 41},
        {"nom": "Luc", "abreviation": "lu", "ordre": 42},
        {"nom": "Jean", "abreviation": "jn", "ordre": 43},
        {"nom": "Actes", "abreviation": "ac", "ordre": 44},
        {"nom": "Romains", "abreviation": "ro", "ordre": 45},
        {"nom": "1 Corinthiens", "abreviation": "1co", "ordre": 46},
        {"nom": "2 Corinthiens", "abreviation": "2co", "ordre": 47},
        {"nom": "Galates", "abreviation": "ga", "ordre": 48},
        {"nom": "Éphésiens", "abreviation": "ep", "ordre": 49},
        {"nom": "Philippiens", "abreviation": "ph", "ordre": 50},
        {"nom": "Colossiens", "abreviation": "col", "ordre": 51},
        {"nom": "1 Thessaloniciens", "abreviation": "1th", "ordre": 52},
        {"nom": "2 Thessaloniciens", "abreviation": "2th", "ordre": 53},
        {"nom": "1 Timothée", "abreviation": "1ti", "ordre": 54},
        {"nom": "2 Timothée", "abreviation": "2ti", "ordre": 55},
        {"nom": "Tite", "abreviation": "tit", "ordre": 56},
        {"nom": "Philémon", "abreviation": "phm", "ordre": 57},
        {"nom": "Hébreux", "abreviation": "he", "ordre": 58},
        {"nom": "Jacques", "abreviation": "ja", "ordre": 59},
        {"nom": "1 Pierre", "abreviation": "1pi", "ordre": 60},
        {"nom": "2 Pierre", "abreviation": "2pi", "ordre": 61},
        {"nom": "1 Jean", "abreviation": "1jn", "ordre": 62},
        {"nom": "2 Jean", "abreviation": "2jn", "ordre": 63},
        {"nom": "3 Jean", "abreviation": "3jn", "ordre": 64},
        {"nom": "Jude", "abreviation": "jud", "ordre": 65},
        {"nom": "Apocalypse", "abreviation": "ap", "ordre": 66}
    ]
}

# Mapping des versions disponibles
BIBLE_VERSIONS = {
    "fr_apee": {"nom": "La Bible de l'Épée", "abreviation": "LSG", "description": "Version française", "langue": "fr"},
    "en_kjv": {"nom": "King James Version", "abreviation": "KJV", "description": "Version anglaise classique", "langue": "en"},
    "en_bbe": {"nom": "Basic English Bible", "abreviation": "BBE", "description": "Version anglaise simplifiée", "langue": "en"},
    "es_rvr": {"nom": "Reina Valera", "abreviation": "RVR", "description": "Version espagnole", "langue": "es"},
    "de_schlachter": {"nom": "Schlachter", "abreviation": "SCH", "description": "Version allemande", "langue": "de"},
    "pt_nvi": {"nom": "Nova Versão Internacional", "abreviation": "NVI", "description": "Version portugaise moderne", "langue": "pt"},
    "ru_synodal": {"nom": "Синодальный перевод", "abreviation": "SYN", "description": "Version russe", "langue": "ru"},
    "zh_cuv": {"nom": "Chinese Union Version", "abreviation": "CUV", "description": "Version chinoise", "langue": "zh"},
    "ar_svd": {"nom": "Arabic Bible", "abreviation": "SVD", "description": "Version arabe", "langue": "ar"},
    "ko_ko": {"nom": "Korean Bible", "abreviation": "KO", "description": "Version coréenne", "langue": "ko"},
    "vi_vietnamese": {"nom": "Vietnamese Bible", "abreviation": "VI", "description": "Version vietnamienne", "langue": "vi"},
    "fi_finnish": {"nom": "Finnish Bible", "abreviation": "FI", "description": "Version finlandaise", "langue": "fi"},
    "ro_cornilescu": {"nom": "Cornilescu", "abreviation": "RO", "description": "Version roumaine", "langue": "ro"},
    "el_greek": {"nom": "Greek Bible", "abreviation": "GR", "description": "Version grecque", "langue": "el"},
    "eo_esperanto": {"nom": "Esperanto Bible", "abreviation": "EO", "description": "Version espéranto", "langue": "eo"}
}
