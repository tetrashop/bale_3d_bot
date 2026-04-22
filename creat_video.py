from PIL import Image, ImageDraw, ImageFont
import os
def create_sample_images(output_dir="frames", width=320, height=240, frame_count=50):
    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.load_default()  # بارگذاری فونت پیشفرض
    for i in range(frame_count):
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        text = f"Frame {i + 1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text(((width - text_w) / 2, (height - text_h) / 2), text, fill=(0, 255, 0), font=font)
        img.save(f"{output_dir}/frame_{i+1:03d}.jpg")
        print(f"{frame_count} sample images saved in '{output_dir}/' folder.")
        if __name__ == "__main__":
            create_sample_images()
