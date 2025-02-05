from PIL import Image

def change_colors(image_path, output_path):
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        if item[0] != 0 or item[1] != 0 or item[2] != 0 or item[3] == 0:
            new_data.append((255, 255, 255, item[3]))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path)

change_colors("images/voiture.png", "voiture_blanche.png")