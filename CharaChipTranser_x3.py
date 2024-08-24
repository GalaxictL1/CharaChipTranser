import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageSequence

def load_images():
    # ファイルダイアログを表示して複数の画像ファイルを選択
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.gif *.bmp")])
    return file_paths

def apply_transparency(img):
    # 背景色を自動で検出し、透過する
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # 背景色（左上隅のピクセル）と一致するピクセルを透明にする
        if item[:3] == datas[0][:3]:
            newData.append((255, 255, 255, 0))  # 透明に設定
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def rearrange_slices(img):
    # 画像をnumpy配列に変換
    img_np = np.array(img)

    # 縦に4分割して順番を変更して再結合
    height = img_np.shape[0] // 4
    slices = [img_np[i * height:(i + 1) * height, :] for i in range(4)]
    reordered_img_np = np.vstack([slices[2], slices[3], slices[1], slices[0]])

    # numpy配列を画像に戻す
    reordered_img = Image.fromarray(reordered_img_np)
    return reordered_img

def resize_image(img, scale_factor):
    # 画像を指定のスケールでリサイズ
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    return img.resize(new_size, Image.NEAREST)

def process_image(file_path):
    img = Image.open(file_path)
    img = apply_transparency(img)

    width, height = img.size

    # 縦のピクセル数が128または256でない場合は処理をスキップ
    if height not in [128, 256]:
        print(f"無効な画像サイズです（縦: {height}ピクセル）: {file_path}")
        return None

    if width == 72 and height == 128:
        # 直接透過処理と再結合
        img = rearrange_slices(img)
    else:
        # 画像を72x128のセクションに分割して処理
        processed_sections = []
        for y in range(0, height, 128):
            for x in range(0, width, 72):
                section = img.crop((x, y, x + 72, y + 128))
                section = rearrange_slices(section)
                processed_sections.append(section)
        
        # キャンバスサイズを修正し、分割したセクションを再結合
        img = Image.new('RGBA', (width, height))
        sections_per_row = width // 72
        for i, section in enumerate(processed_sections):
            row = i // sections_per_row
            col = i % sections_per_row
            img.paste(section, (col * 72, row * 128))

    # 画像を2倍に拡大
    img = resize_image(img, 3)

    return img

def save_image(img, file_path):
    # 出力先の「Transparent」フォルダを作成
    output_dir = os.path.join(os.path.dirname(file_path), "Transparent")
    os.makedirs(output_dir, exist_ok=True)

    # 画像ファイルを保存
    output_path = os.path.join(output_dir, os.path.basename(file_path).replace(".png", "_x3.png").replace(".gif", "_x3.png").replace(".bmp", "_x3.png"))
    img.save(output_path)
    print(f"保存しました: {output_path}")

def main():
    file_paths = load_images()
    if not file_paths:
        print("画像が選択されませんでした。")
        return

    for file_path in file_paths:
        processed_img = process_image(file_path)
        if processed_img is not None:
            save_image(processed_img, file_path)

if __name__ == "__main__":
    main()