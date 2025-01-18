import favicon
import requests
import json, os
from urllib.parse import urlparse

def provider_favicon_lookup(provider_name):
    f = open("dev_archive/providers.json", )
    data = json.load(f)
    f.close()

    # Given provider_name to search for
    #given_provider_name = "Sonic"

    # Iterate over the data to find the website for the given provider_name
    for item in data:
        if item["provider_name"].lower() == provider_name.lower():
            website = item["website"]
            break
    else:
        return None  #website = "Website not found for the given provider_name"

    domain = urlparse(website).netloc

    img_path = 'assets' + os.sep + 'favicons' + os.sep + domain + '.png'
    return img_path


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
        return None
    return letter_to_color.get(letter.upper())


# local main for unit testing
if __name__ == '__main__':
    reply = ""
    while reply != "exit":
        reply = input("What provider to lookup? ")
        print (provider_favicon_lookup(reply))

# fav = open("domain"+".png")
# img = f.read()
# f.close()
#
# print (f"{item['provider_name']}  {domain}")
# url = 'https://www.google.com/s2/favicons?domain=' + domain
# fav = requests.get(url).content
# img_path = os.sep + 'tmp' + os.sep + 'images' + os.sep + domain + '.png'
# with open(img_path, 'wb') as handler:
#     handler.write(fav)
#
