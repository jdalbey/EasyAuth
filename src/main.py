import logging
from controllers import AppController
from views import AppView

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Initialize the controller and view
    controller = AppController()
    view = AppView(controller)

    # Start the application
    view.run()

if __name__ == '__main__':
    main()