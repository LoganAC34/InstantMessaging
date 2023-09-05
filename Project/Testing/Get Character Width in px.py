from PIL import ImageFont

# Define the font, char, and char height
font_name = r'C:\Windows\Fonts\SegoeUI.ttf'  # Replace with the path to your font file
text_height = 9  # Text height in pixels

# Load the font by name
try:
    font = ImageFont.load_default()  # Load the default font
    font = ImageFont.truetype(font_name, text_height)  # Try to load the specified font by name
except IOError:
    print(f"Font '{font_name}' not found. Using default font.")
    font = ImageFont.load_default()

characters = ['   ', '=', '\u202F\u202F\u202F\u202F\u202F', '\u200B']
for char in characters:
    # Get the bounding box of the character (includes blank space)
    bbox = font.getbbox(char)

    # Calculate the width including blank space
    char_width_with_padding = bbox[2] - bbox[0]

    # Print the width of the character including blank space in pixels
    print(f"The width of '{char}' including padding is {char_width_with_padding} pixels.")
