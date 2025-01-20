import json
import logging
import zipfile

from urllib.parse import urlparse

from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import QByteArray
from PyQt5.QtWidgets import QLabel, QApplication, QMessageBox


class Providers:
    kZipPath = "assets/favicons.zip"
    kProvidersPath = "assets/providers.json"
    logwriter = logging.getLogger(__name__)

    def __init__(self):
        self.provider_map = Providers._build_map()

    @staticmethod
    def _load_imgdict_from_zipimages():
        """
        Loads images from a ZIP file into a dictionary where the key is the file name
        and the value is a QPixmap.

        Returns:
            dict: Dictionary with file names as keys and raw image data as values.
        """
        image_dict = {}

        try:
            with zipfile.ZipFile(Providers.kZipPath, 'r') as z:
                for name in z.namelist():
                    # process each item in the zip file
                    with z.open(name) as file:
                        # Read image data into a QByteArray
                        image_dict[name] = file.read()
        except FileNotFoundError:
            Providers.logwriter.warning("Missing favicons.zip file - no favicons will be displayed.")
        return image_dict

    @staticmethod
    def _build_map():
        """
        Build a map with provider_name as key and (domain,raw_image) as value.
        This facilitates looking up a favicon given the provider name
        """
        # Create an empty dictionary to store the mapping
        provider_map = {}

        # Retrieve the dictionary of images
        img_dict = Providers._load_imgdict_from_zipimages()
        # If no images were retrieved, return empty map
        if len(img_dict) == 0:
            return {}

        # Populate the dictionary with provider_name as key and domain,raw_image as value
        try:
            f = open(Providers.kProvidersPath, )
        except FileNotFoundError:
            Providers.logwriter.warning("Missing providers.json file - no favicons will be displayed.")
            return {}
        json_data = json.load(f)
        # Sort the data dictionary by 'provider_name'
        sorted_data = sorted(json_data, key=lambda x: x['provider_name'].lower())
        # Build a map of provider name to domain and image
        for record in sorted_data:
            provider_name = record['provider_name']
            website = record['website']
            png_filename = urlparse(website).netloc + '.png'
            provider_map[provider_name] = {'png_filename':png_filename, 'raw_image':img_dict[png_filename]}

        return provider_map

    @staticmethod
    def make_pixmap(raw_img):
        # Assuming you have raw binary image data in variable 'raw_data'
        # Specify the image width, height, and format
        # width = 16
        # height = 16
        # format = QImage.Format_ARGB32  # Use ARGB32 format for PNG images
        #
        # # Create a QImage from raw binary data
        # image = QImage(raw_img, width, height, format)
        #
        # # Convert the QImage to QPixmap
        # pixmap = QPixmap.fromImage(image)
        # return pixmap
        # Read image data into a QByteArray
        pixmap = QPixmap()
        image_data = QByteArray(raw_img)
        # Load QPixmap from QByteArray
        pixmap.loadFromData(image_data)
        pixmap = pixmap.scaled(16, 16)
        return pixmap

    def get_provider_icon_pixmap(self, provider):
        # REFS: https://favicon.im/  https://opendata.stackexchange.com/questions/14007/list-of-top-10k-websites-and-their-favicons
        # https://github.com/opendns/public-domain-lists/blob/master/opendns-top-domains.txt
        # https://pypi.org/project/favicon/
        # Look up provider icon
        try:
            img_raw = self.provider_map[provider]['raw_image']
        except KeyError:
            Providers.logwriter.info(f"Missing {provider} in map, can't get favicon.")
            return None
        pixmap = self.make_pixmap(img_raw)
        return pixmap

    def get_provider_icon(self,provider):
        my_icon_label = QLabel()
        provider_icon_pixmap = self.get_provider_icon_pixmap(provider)
        if provider_icon_pixmap:
            # Set the QPixmap to the QLabel
            my_icon_label.setPixmap(provider_icon_pixmap)
        else:
            Providers.logwriter.info(f"No icon for {provider}, generating initial.")
            # IF icon not available show the first letter of provider's name
            provider_initial = provider[0]  # get first letter of provider name
            my_icon_label.setText(provider_initial + '')
            color_name = get_color_for_letter(provider_initial)
            css_string = "QLabel { border: 1px solid " + color_name + "; "
            css_string += "border-radius: 8px; color: white; background-color: "
            css_string += color_name + "; "
            css_string += "font-size: 12px;font-weight: bold;text-align: center;}"
            my_icon_label.setStyleSheet(css_string)
            """
                QLabel {
                border: 1px solid #488AC7;  /* 'silk blue' */
                border-radius: 8px;
                color: white;
                background-color: #488AC7;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
                }
            """
        return my_icon_label

def get_color_for_letter(letter):
    """
    Returns the color associated with the given letter.

    Args:
        letter (str): A single letter (case-insensitive).

    Returns:
        str: The color associated with the letter, or None if the input is invalid.
    """
    # Mapping of letters to colors
    letter_to_color = {
        'A': 'lightpink',
        'B': 'lightcoral',
        'C': 'lightsalmon',
        'D': 'lightgoldenrodyellow',
        'E': 'palegreen',
        'F': 'lightseagreen',
        'G': 'mediumturquoise',
        'H': 'paleturquoise',
        'I': 'lightblue',
        'J': 'deepskyblue',
        'K': 'lightskyblue',
        'L': 'lightgray',
        'M': 'lavender',
        'N': 'lightpink',
        'O': 'lightcoral',
        'P': 'lightsalmon',
        'Q': 'lightgoldenrodyellow',
        'R': 'palegreen',
        'S': 'lightseagreen',
        'T': 'mediumturquoise',
        'U': 'paleturquoise',
        'V': 'lightblue',
        'W': 'deepskyblue',
        'X': 'lightskyblue',
        'Y': 'lightgray',
        'Z': 'lavender',
    }

    if not letter or len(letter) != 1 or not letter.isalpha():
        return 'white'
    return letter_to_color.get(letter.upper())

# Example Usage
if __name__ == "__main__":
    app = QApplication([])
    providers = Providers()
    pm = providers.get_provider_icon_pixmap('007Names')
    # Set the QPixmap to the QLabel
    icon_label = QLabel()
    icon_label.setPixmap(pm)
    print (icon_label)
