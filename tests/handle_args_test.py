import sys
import unittest
from unittest.mock import patch, MagicMock
import os
from handle_args import validate_arguments
from appconfig import AppConfig
import argparse
# NOTE: This test can't be run as part of the suite because it resets AppConfig and that
# causes a bunch of other tests to fail.  I suspect the best solution is to restore
# defaults at the start of every unit test that needs to mess with the settings.
# This test deals with how AppConfig is initialized, so it's kind of a special case.
# I tried mocking AppConfig for the tests but it didn't work.
class TestHandleArgs(unittest.TestCase):

    @patch("os.path.exists")
    def test_validate_arguments_relative_file_exists(self, mock_exists):
        AppConfig._instance = None
        # setup argument
        args = argparse.Namespace(config_file = "test_data/config_test1.ini")

        # Mock os.path.exists to return True (file exists)
        mock_exists.return_value = True

        # Call the function
        validate_arguments(args)

        # Check that AppConfig was called with the absolute path
        abspath = os.path.abspath(args.config_file)
        appconfig = AppConfig()
        assert appconfig._initialized == True
        assert appconfig.filepath == abspath

    @patch("os.path.exists")
    def test_validate_arguments_absolute_file_exists(self, mock_exists):
        AppConfig._instance = None
        # Create an absolute path to existing config file
        command_path = os.path.join(os.getcwd(), "test_data","config_test1.ini")

        # setup argument
        args = argparse.Namespace(config_file = command_path)

        # Mock os.path.exists to return True (file exists)
        mock_exists.return_value = True

        # Call the function
        validate_arguments(args)

        # Check that AppConfig was called with the absolute path
        abspath = os.path.abspath(args.config_file)
        appconfig = AppConfig()
        assert appconfig._initialized == True
        assert appconfig.filepath == abspath

    @patch("os.path.exists")
    @patch("appconfig.AppConfig")  # Replace 'your_module' with the actual module
    def test_validate_arguments_file_not_found(self, MockAppConfig, mock_exists):
        # Mock os.path.exists to return False (file does not exist)
        mock_exists.return_value = False

        # Create a mock argument object
        class Args:
            config_file = "config.json"

        args = Args()

        # Call the function
        with patch("builtins.print") as mock_print:
            validate_arguments(args)

            # Check if the appropriate print message was called
            mock_print.assert_called_with(f"{args.config_file} not found, using default config file.")

        # Check that AppConfig was not called because the file doesn't exist
        MockAppConfig.assert_not_called()


if __name__ == "__main__":
    unittest.main()
