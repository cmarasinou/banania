from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
import unicodedata
import re
import os

WATERMARK_FONT = "font/GoudyOldStyleBold.ttf"
TEXT_FONT = "font/Comfortaa-Regular.ttf"


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def create_image_with_text_and_image(string1, string2, image_url):
    # Define image dimensions
    width = 1024
    height = 1024
    string1 = "“ " + string1 + " ”"
    string2 = "“ " + string2 + " ”"
    string3 = "BANANIA REPUPLIC"

    # Create a new image with white background
    image = Image.new("RGBA", (width, height), "white")

    # Load the image from the URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # Resize the image to fit the bottom of the created image
    img_h = height // 3
    img_w = int(img.width * img_h / img.height)
    img = img.resize((img_w, img_h))
    img_x = (width - img_w) // 2
    img_y = height - img_h - 100

    # Define color palettes
    palettes = [
        ["#1E1E1E", "#323232", "#4B4B4B", "#656565", "#7F7F7F"],  # Dark Palette 1
        ["#232C33", "#38515E", "#527387", "#6995AE", "#7FC4D4"],  # Dark Palette 2
        ["#2B1B17", "#3F2B29", "#57372E", "#744139", "#B36259"],  # Dark Palette 3
        ["#594F4F", "#547980", "#45ADA8", "#9DE0AD", "#E5FCC2"],  # Light Palette 1
        ["#1B676B", "#519548", "#88C425", "#BEF202", "#EAFDE6"],  # Light Palette 2
        ["#404040", "#718F94", "#A5C4C7", "#CFF4FC", "#FCFCFC"],  # Light Palette 3
        ["#312736", "#D4838F", "#D6ABB1", "#D9D9D9", "#FFEFFF"],  # Pastel Palette 1
        ["#023436", "#5C968A", "#B8C7A7", "#F6EAC2", "#F5BC63"],  # Pastel Palette 2
        ["#251605", "#774A29", "#C1A172", "#E4D4A8", "#FFFEF6"],  # Earthy Palette 1
        ["#4D3B3B", "#DE6262", "#FFA78C", "#FFD0B3", "#FFECD8"],  # Earthy Palette 2
    ]

    # Choose color palette based on the image's average brightness
    avg_brightness = get_average_brightness(img)
    palette_index = int(avg_brightness / 25)  # Dividing the brightness into 25 levels to select the palette
    color_palette = palettes[palette_index]

    # Select background and font colors from the chosen palette
    bg_color = color_palette[0]
    font_color = color_palette[-1]

    # Create a draw object
    draw = ImageDraw.Draw(image)

    # Define font and size for the strings
    font = ImageFont.truetype("font/Comfortaa-Regular.ttf", height // 13, encoding="UTF-8")

    # Calculate the center position for the first string
    text1_width, text1_height = draw.textsize(string1, font=font)
    text1_x = (width - text1_width) // 2
    text1_y = height // 9

    # Calculate the center position for the second string
    text2_width, text2_height = draw.textsize(string2, font=font)
    text2_x = (width - text2_width) // 2
    text2_y = (height - 2 * text2_height) // 2

    # Split the strings into multiple lines if needed
    string1_lines = textwrap.wrap(string1, width=20)
    string2_lines = textwrap.wrap(string2, width=20)

    # Draw the background rectangle with the chosen background color
    draw.rectangle([(0, 0), (width, height)], fill=bg_color)

    # Draw the first string at the top
    for i, line in enumerate(string1_lines):
        line_width, line_height = draw.textsize(line, font=font)
        line_x = (width - line_width) // 2
        line_y = text1_y + i * line_height
        draw.text((line_x, line_y), line, font=font, fill=font_color)

    # Draw the second string in the middle
    for i, line in enumerate(string2_lines):
        line_width, line_height = draw.textsize(line, font=font)
        line_x = (width - line_width) // 2
        line_y = text2_y + i * line_height
        draw.text((line_x, line_y), line, font=font, fill=font_color)

    # Paste the resized image at the bottom
    image.paste(img, (img_x, img_y), img)

    # Draw banania text
    font = ImageFont.truetype("font/GoudyOldStyleBold.ttf", height // 16)
    text3_width, text3_height = draw.textsize(string3, font=font)
    text3_x = (width - text3_width) // 2
    text3_y = height - text3_height - height // 25
    text = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw_text = ImageDraw.Draw(text)
    draw_text.text((text3_x, text3_y), string3, font=font, fill=(255, 255, 255, 128))
    image = Image.alpha_composite(image, text)

    # Draw banania logo
    img = Image.open("static/banania-logo.png")
    img2 = img.copy()
    img.putalpha(20)
    img_x = (width - img.width) // 2
    img_y = (height - img.height) // 2

    logo = Image.new("RGBA", image.size, (255, 255, 255, 0))
    logo.paste(img, (img_x, img_y), mask=img2)
    image = Image.alpha_composite(image, logo)
    # Show the final image
    return image


def get_average_brightness(image):
    # Convert the image to grayscale
    grayscale_image = image.convert("L")

    # Calculate the average brightness by summing up the pixel values and dividing by the number of pixels
    brightness = sum(grayscale_image.getdata()) / float(image.size[0] * image.size[1])

    return brightness


if __name__ == "__main__":
    import pandas as pd

    data = pd.read_csv("./data/raw.csv")
    for idx in range(len(data.index)):
        record = data.iloc[idx]
        string1 = str(record["english"])
        string2 = str(record["greek"])
        image_url = str(record["url"])
        image_path = os.path.join("./data/generated_images", f"{slugify(string1)}.png")
        image = create_image_with_text_and_image(string1, string2, image_url)
        image.save(image_path)
