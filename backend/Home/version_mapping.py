"""Utilitaires pour mapper les versions bibliques du profil vers les traduction_id MongoDB."""

from typing import Optional

# Mapping des noms de versions du profil vers les traduction_id MongoDB
# Basé sur les données réelles de la collection "traductions" dans MongoDB
# Format: "nom" (de la collection) -> "abreviation" (en lowercase = translation_id)
VERSION_NAME_TO_TRANSLATION_ID = {
    # Versions françaises
    "La Bible de l'Épée": "lsg",
    "La bible de l'épée": "lsg",
    "louis segond 1910": "lsg",  # Alias commun
    "Louis Segond 1910": "lsg",
    "LSG": "lsg",
    "lsg": "lsg",
    
    # Versions anglaises
    "King James Version": "kjv",
    "king james version": "kjv",
    "KJV": "kjv",
    "kjv": "kjv",
    "Basic English Bible": "bbe",
    "basic english bible": "bbe",
    "BBE": "bbe",
    "bbe": "bbe",
    
    # Version espagnole
    "Reina Valera": "rvr",
    "reina valera": "rvr",
    "RVR": "rvr",
    "rvr": "rvr",
    
    # Version allemande
    "Schlachter": "sch",
    "schlachter": "sch",
    "SCH": "sch",
    "sch": "sch",
    
    # Version portugaise
    "Nova Versão Internacional": "nvi",
    "nova versão internacional": "nvi",
    "NVI": "nvi",
    "nvi": "nvi",
    
    # Version russe
    "Синодальный перевод": "syn",
    "синодальный перевод": "syn",
    "SYN": "syn",
    "syn": "syn",
    
    # Version chinoise
    "Chinese Union Version": "cuv",
    "chinese union version": "cuv",
    "CUV": "cuv",
    "cuv": "cuv",
    
    # Version arabe
    "Arabic Bible": "svd",
    "arabic bible": "svd",
    "SVD": "svd",
    "svd": "svd",
    
    # Version coréenne
    "Korean Bible": "ko",
    "korean bible": "ko",
    "KO": "ko",
    "ko": "ko",
    
    # Version vietnamienne
    "Vietnamese Bible": "vi",
    "vietnamese bible": "vi",
    "VI": "vi",
    "vi": "vi",
    
    # Version finlandaise
    "Finnish Bible": "fi",
    "finnish bible": "fi",
    "FI": "fi",
    "fi": "fi",
    
    # Version roumaine
    "Cornilescu": "ro",
    "cornilescu": "ro",
    "RO": "ro",
    "ro": "ro",
    
    # Version grecque
    "Greek Bible": "gr",
    "greek bible": "gr",
    "GR": "gr",
    "gr": "gr",
    
    # Version espéranto
    "Esperanto Bible": "eo",
    "esperanto bible": "eo",
    "EO": "eo",
    "eo": "eo",
    
    # Autres versions possibles mentionnées dans le profil (si elles existent)
    "Bible du Semeur": "semeur",  # À vérifier si cette version existe dans MongoDB
    "bible du semeur": "semeur",
    "NEG": "neg",  # Nouvelle Edition de Genève - À vérifier
    "neg": "neg",
    "Nouvelle Edition de Genève": "neg",
    "nouvelle edition de genève": "neg",
    "Segond 21": "segond21",  # À vérifier
    "segond 21": "segond21",
}

def get_translation_id_from_version_name(version_name: str) -> Optional[str]:
    """
    Convertit un nom de version biblique du profil en traduction_id MongoDB.
    
    Args:
        version_name: Nom de la version (ex: "Louis Segond 1910", "King James Version")
        
    Returns:
        traduction_id correspondant (ex: "lsg", "kjv") ou None si non trouvé
    """
    if not version_name:
        return None
        
    version_name_normalized = version_name.strip()
    version_name_lower = version_name_normalized.lower()
    
    # Recherche exacte d'abord (insensible à la casse)
    for name, translation_id in VERSION_NAME_TO_TRANSLATION_ID.items():
        if name.lower() == version_name_lower:
            return translation_id
    
    # Recherche partielle (le nom du profil contient le nom de la traduction)
    for name, translation_id in VERSION_NAME_TO_TRANSLATION_ID.items():
        name_lower = name.lower()
        # Vérifier si le nom recherché contient le nom de la traduction ou vice versa
        if version_name_lower in name_lower or name_lower in version_name_lower:
            return translation_id
    
    # Si rien n'est trouvé, retourner None
    return None

