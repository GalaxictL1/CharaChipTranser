import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image

def load_images():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.gif *.bmp")])
    return file_paths

def apply_transparency(img):
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[:3] == datas[0][:3]:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img

def rearrange_slices(img):
    img_np = np.array(img)
    height = img_np.shape[0] // 4
    slices = [img_np[i * height:(i + 1) * height, :] for i in range(4)]
    reordered_img_np = np.vstack([slices[2], slices[3], slices[1], slices[0]])
    reordered_img = Image.fromarray(reordered_img_np)
    return reordered_img

def process_image(file_path):
    img = Image.open(file_path)
    width, height = img.size
    processed_images = []

    if width == 72 and height in [128, 256]:
        if height == 256:
            for y in range(0, height, 128):
                section = img.crop((0, y, width, y + 128))
                section = apply_transparency(section)
                processed_images.append(rearrange_slices(section))
        else:
            section = apply_transparency(img)
            processed_images.append(rearrange_slices(section))
    elif width in [144, 216, 288] and height in [128, 256]:
        for y in range(0, height, 128):
            for x in range(0, width, 72):
                section = img.crop((x, y, x + 72, y + 128))
                section = apply_transparency(section)
                processed_images.append(rearrange_slices(section))
    elif width in [72, 144, 216, 288] and height == 128:
        for x in range(0, width, 72):
            section = img.crop((x, 0, x + 72, height))
            section = apply_transparency(section)
            processed_images.append(rearrange_slices(section))
    else:
        section = apply_transparency(img)
        processed_images.append(section)

    return processed_images

def save_image(img, file_path, index=None):
    output_dir = os.path.join(os.path.dirname(file_path), "Transparent")
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.basename(file_path).replace(".png", "").replace(".gif", "").replace(".bmp", "")
    
    if index is not None:
        output_path = os.path.join(output_dir, f"{base_name}_Wolf{index}.png")
    else:
        output_path = os.path.join(output_dir, f"{base_name}_Wolf.png")
    
    img.save(output_path)
    print(f"保存しました: {output_path}")

def main():
    file_paths = load_images()
    if not file_paths:
        print("画像が選択されませんでした。")
        return

    for file_path in file_paths:
        processed_images = process_image(file_path)
        if processed_images is not None:
            for i, img in enumerate(processed_images):
                save_image(img, file_path, index=i+1 if len(processed_images) > 1 else None)

if __name__ == "__main__":
    main()