import logging

from appconfig import AppConfig
from controllers import AppController
from views import AppView
from pathlib import Path # Python 3.5+
def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Initialize the application settings with a config file
    kConfigPath = ".config/EasyAuth/config.ini"
    home_dir_str = str(Path.home())
    filepath = Path.home().joinpath(home_dir_str, kConfigPath)
    config = AppConfig(filepath)


    # Initialize the controller and view
    controller = AppController()
    view = AppView(controller)

    # Start the application
    view.run()

if __name__ == '__main__':
    main()