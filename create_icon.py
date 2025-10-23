import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """יוצר אייקון פשוט עבור האפליקציה"""
    # צור תמונה 64x64 פיקסלים
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # צור רקע עגול כחול
    draw.ellipse([2, 2, size-2, size-2], fill=(0, 100, 200, 255))
    
    # הוסף טקסט "עב"
    try:
        # נסה להשתמש בפונט גדול יותר
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # אם אין פונט זמין, השתמש בברירת מחדל
        font = ImageFont.load_default()
    
    # צייר את הטקסט "עב" במרכז
    text = "עב"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 5
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # שמור את האייקון
    image.save("icon.ico", format="ICO")
    print("Icon created successfully!")

if __name__ == "__main__":
    create_icon()
