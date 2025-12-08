from utils import format_number


class TestFormatNumber:
    """Test cases for format_number function"""

    def test_format_number(self):
        """Test basic number formatting"""
        assert format_number(1000) == '1\xa0tūkst.'
        assert format_number(1500) == '1,5\xa0tūkst.'
        assert format_number(1000000) == '1\xa0milj.'

    def test_format_nubmer_edge_cases(self):
        """Test edge cases"""
        assert format_number(0) == '0'
        assert format_number(1) == '1'
        assert format_number(999) == '999'

    def test_format_number_large_values(self):
        """Test formatting of large numbers"""
        assert format_number(1234567) == '1,23\xa0milj.'
        assert format_number(1235467890) == '1,24\xa0mljrd.'

    def test_format_number_negative(self):
        """Test negative number formatting"""
        assert format_number(-1000) == '-1\xa0tūkst.'
        assert format_number(-1500) == '-1,5\xa0tūkst.'

    def test_format_number_decimal_places(self):
        """Test that excatly 2 decimal places ar shown when needed"""
        assert format_number(1500) == '1,5\xa0tūkst.'
        assert format_number(1010) == '1,01\xa0tūkst.'
        assert format_number(1000) == '1\xa0tūkst.'
