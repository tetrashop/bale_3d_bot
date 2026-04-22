from PIL import Image, ImageDraw, ImageFont
import os
def create_sample_images(output_dir="frames", width=320, height=240, frame_count=50):
    os.makedirs(output_dir, exist_ok=True)
    font = ImageFont.load_default()
    for i in range(frame_count):
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        text = f"Frame {i+1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((width - w) / 2, (height - h) / 2), text, fill='green', font=font)
        filename = os.path.join(output_dir, f"frame_{i+1:03d}.jpg")
        img.save(filename)
        print(f"{frame_count} sample images created in folder '{output_dir}'")
        if __name__ == "__main__":
            create_sample_images()
