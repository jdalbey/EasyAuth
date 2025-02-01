from PyQt5.QtWidgets import QApplication, QLabel

from appconfig import AppConfig
from provider_map import get_color_for_letter
from provider_map import Providers
import logging, unittest
logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
    )
class TestProviderMap(unittest.TestCase):

    def test_buildmap_success(self):
        # This statement is needed so log msgs from unit under test will display
        logging.getLogger().addHandler(logging.StreamHandler())
        # Verify default path
        assert Providers.kZipPath == "assets/favicons.zip"
        ret_map = Providers._build_map()
        assert ret_map is not None
        assert len(ret_map) > 0
        map_tuple = ret_map['login.gov']
        assert len(map_tuple['png_filename']) > 0
        assert map_tuple['png_filename'] == "login.gov.png"

    def test_buildmap_imgdict_empty(self):
        # This statement is needed so log msgs from unit under test will display
        logging.getLogger().addHandler(logging.StreamHandler())
        #set zip path to non-existant file
        Providers.kZipPath = "/tmp/thisfiledoesntexist"
        ret_map = Providers._build_map()
        assert ret_map is not None
        assert len(ret_map) == 0
        # Reset the correct path
        Providers.kZipPath = "assets/favicons.zip"

    def test_buildmap_providers_empty(self):
        # This statement is needed so log msgs from unit under test will display
        logging.getLogger().addHandler(logging.StreamHandler())
        #set zip path to non-existant file
        Providers.kProvidersPath = "/tmp/thisfiledoesntexist"
        ret_map = Providers._build_map()
        assert ret_map is not None
        assert len(ret_map) == 0
        # Reset the correct path
        Providers.kProvidersPath = "assets/providers.json"

    def test_get_provider_icon(self):
        map = Providers()
        result = map.get_provider_icon("Mint")
        assert result is not None
        assert isinstance(result, QLabel)
        assert result.text() == ''
        assert result.pixmap() is not None
        result = map.get_provider_icon("missing provider")
        assert result is not None
        assert result.text() == "m"  #first letter of 'missing'
        assert result.pixmap() == None

    def test_get_provider_icon_missingmap(self):
        map = Providers()
        map.provider_map = {}
        result = map.get_provider_icon("Mint")
        assert result is not None
        assert result.text() == "M"  #first letter of 'Mint'

    def test_zipfile_present(self):
        # This statement is needed so log msgs from unit under test will display
        logging.getLogger().addHandler(logging.StreamHandler())
        # Verify default path
        assert Providers.kZipPath == "assets/favicons.zip"
        ret_dict = Providers._load_imgdict_from_zipimages()
        assert ret_dict is not None
        assert len(ret_dict) > 0
        assert ret_dict['101domain.com.png'][:4] == b'\x89PNG'

    def test_zipfile_notfound(self):
        # This statement is needed so log msgs from unit under test will display
        logging.getLogger().addHandler(logging.StreamHandler())
        # Verify default path
        assert Providers.kZipPath == "assets/favicons.zip"
        #set zip path to non-existant file
        Providers.kZipPath = "/tmp/thisfiledoesntexist"
        ret_dict = Providers._load_imgdict_from_zipimages()
        assert ret_dict is not None
        assert len(ret_dict) == 0
        Providers.kZipPath = "assets/favicons.zip" #reset

    # Tests of utility method
    def test_get_color_for_valid_letter(self):
        result = get_color_for_letter('A')
        assert result == 'lightpink'

    def test_not_valid_letter(self):
        result = get_color_for_letter('1')
        assert result == 'white'

    # Using setUpClass and tearDownClass ensures that QApplication is created once for the entire test suite, preventing multiple instances.
    @classmethod
    def setUpClass(cls):
        # QApplication is created once for the entire test suite
        cls.app = QApplication([])
        cls.appconfig = AppConfig()

    @classmethod
    def tearDownClass(cls):
        # Ensure QApplication is properly cleaned up after all tests
        cls.app.quit()

    def setUp(self):
        # No need to create QApplication here; it's already done in setUpClass
        pass

    def tearDown(self):
        # Clean up dialog and other resources
        pass
