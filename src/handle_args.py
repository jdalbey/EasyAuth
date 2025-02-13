import argparse
import os

from appconfig import AppConfig

# Handle command line argument parsing

def validate_arguments(args):
    # See if an alternate config file is specified
    if args.config_file:
        # Convert relative path to absolute path
        absolute_path = os.path.abspath(args.config_file)

        # Check if the file exists
        if not os.path.exists(absolute_path):
            print (f"{args.config_file} not found, using default config file.")
        else:
            # Load settings from given file
            AppConfig(absolute_path)

def handle_args():
    """ Get the command line arguments """
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A 2FA authenticator to hold your secret keys and generate one-time passwords.")
    
    # Define arguments
    parser.add_argument('-c', '--config_file', type=str, help="(Optional) The path to the config file to be used for Preferences by the application. Most users can ignore this as the preferred mode of operation is to let the application use a default location.")

    # Parse arguments
    args = parser.parse_args()

    # Validate arguments
    validate_arguments(args)
