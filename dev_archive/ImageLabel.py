from tkinter import Tk, Label, PhotoImage, Button
from PIL import Image, ImageDraw, ImageFont
import io


# Function to create an image from a single character
def create_text_image(text, font_size, image_size):
    # Create a blank image with a white background
    image = Image.new("RGB", image_size, color="white")

    # Load a font
    font = ImageFont.truetype("arial.ttf", font_size)  # You can use other fonts too

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Calculate the width and height of the text to center it in the image using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)  # Get bounding box of the text
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate position to center text horizontally and vertically
    position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)

    # Draw the text on the image
    draw.text(position, text, font=font, fill="black")  # Black text

    return image


# Function to convert the PIL Image to PhotoImage (Tkinter format)
def pil_to_tkimage(pil_image):
    with io.BytesIO() as byte_io:
        pil_image.save(byte_io, format="PNG")
        byte_io.seek(0)
        return PhotoImage(data=byte_io.read())


root = Tk()

# Load an external image (e.g., "your_image.png")
external_image = PhotoImage(file="images/favicon_96x96.png")

# Create the text-based image from character 'A'
text_image = create_text_image("A", 90, (96, 96))
text_image_tk = pil_to_tkimage(text_image)

# Create a label to hold either the image or text
label = Label(root, image=text_image_tk)  # Initially show text image
label.pack(side="top", pady=10)


# Toggle function to switch between the text image and the external image
def toggle_content():
    if label.cget("image") == str(text_image_tk):  # Check if text image is displayed
        label.config(image=external_image)  # Switch to external image
    else:
        label.config(image=text_image_tk)  # Switch to text image


# Create a button to toggle between text and image
button = Button(root, text="Toggle", command=toggle_content)
button.pack(side="top")

root.mainloop()
