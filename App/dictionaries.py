# Dictionnaires centralisés pour l'application

# Dictionnaire de correspondance type -> nom fichier STL
mapping_stl = {
    "Support palier_ex": "Support_palier_exemple.stl",
    "Nozzle": "Jet_Engine-Compressor_Housing.stl",
    "Distributeur": "Rotor_compresseur_distributeur.stl",
    "Roues": "Roue.stl",
    "Barettes": "Jet_Engine_Fan-Stator.stl",
    "Pales": "Jet_Engine_Fan-Stator.stl",  # Idem si pas de fichier distinct
    "Autre (forme libre)": None
}

# Dictionnaire des cotes critiques associées aux types de pièces
cotes_critiques_par_type = {
    "Support palier_ex": ["Rayon extérieur", "Alésage moyen", "Épaisseur patin"],
    "Nozzle": ["Rayon fond", "Rayon extérieur"],
    "Distributeur": ["Rayon hors tout", "Rayon intérieur jante"],
    "Roues": ["Diamètre global max", "Rayon fond"],
    "Barettes": ["Petit alésage", "Rayon congé usinage"],
    "Pales": ["Rayon extérieur", "Épaisseur patin"],
    "Autre (forme libre)": []
}
