from provider_map import get_color_for_letter

class TestProviderMap:
    def test_get_color_for_valid_letter(self):
        result = get_color_for_letter('A')
        assert result == 'lightpink'

    def test_not_valid_letter(self):
        result = get_color_for_letter('1')
        assert result == 'white'
