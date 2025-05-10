import sys
sys.path.append('/usr/lib/freecad/lib')

try:
    import FreeCAD
    import FreeCADGui
except ImportError as e:
    print("Error: Unable to import FreeCAD modules. Ensure FreeCAD is installed and the library path is correct.")
    sys.exit(1)
    
import os
import time
import math

# === Configuration personnalisée ===
fichier_fcstd = "/home/riccardo/Visual_Studio_Code/freelance/FreeCad_integration/Part_ex.FCStd"
dossier_sortie = "/home/riccardo/Visual_Studio_Code/freelance/FreeCad_integration/video"
os.makedirs(dossier_sortie, exist_ok=True)

# === Chargement de la pièce ===
doc = FreeCAD.openDocument(fichier_fcstd)
FreeCAD.setActiveDocument(doc.Name)
FreeCADGui.ActiveDocument = FreeCADGui.getDocument(doc.Name)

# === Vue initiale ===
view = FreeCADGui.ActiveDocument.ActiveView
view.viewAxonometric()
view.setCameraType("Perspective")
view.fitAll()

# === Paramètres de rotation autour de Z ===
center = view.getViewDirection().normalize() * -500  # position caméra initiale
steps = 72  # 72 images = 5°/image pour 360°
radius = 500
height = 0

print("Capture en cours...")

for i in range(steps):
    angle_deg = i * (360 / steps)
    angle_rad = math.radians(angle_deg)

    x = radius * math.sin(angle_rad)
    y = radius * math.cos(angle_rad)
    z = height
    position = FreeCAD.Vector(x, y, z)

    view.setCameraOrientation(FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), angle_deg))
    view.setCamera(position, FreeCAD.Vector(0, 0, 0))  # focus sur l'origine
    time.sleep(0.05)

    filename = os.path.join(dossier_sortie, f"frame_{i:03d}.png")
    view.saveImage(filename, 800, 600, 'White')

print("Captures terminées dans :", dossier_sortie)
