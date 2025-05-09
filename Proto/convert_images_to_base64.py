# convert_images_to_base64.py
import base64
import os

image_folder = "images"
image_dict = {}

for filename in os.listdir(image_folder):
    if filename.endswith(".png"):
        path = os.path.join(image_folder, filename)
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            key = filename.replace(".png", "").replace("_", " ").title()
            image_dict[key] = encoded

# Sauvegarder dans un fichier .py
with open("base64_images.py", "w") as f:
    f.write("images_base64 = {\n")
    for key, b64 in image_dict.items():
        f.write(f'    "{key}": """{b64}""",\n')
    f.write("}")
