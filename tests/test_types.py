"""Tests for justetf_scraping.types module."""

import typing

from justetf_scraping.types import Country, Currency


def _get_literal_values(literal_type: type) -> list:
    """Extract values from a Literal type."""
    return list(typing.get_args(literal_type))


class TestCountry:
    def test_all_country_codes_are_two_letter_uppercase(self):
        for code in _get_literal_values(Country):
            assert len(code) == 2, f"Country code '{code}' is not 2 characters"
            assert code == code.upper(), f"Country code '{code}' is not uppercase"

    def test_original_countries_present(self):
        values = _get_literal_values(Country)
        for code in ["DE", "AT", "CH", "GB", "IT", "FR", "ES", "NL", "BE"]:
            assert code in values, f"Original country '{code}' missing"

    def test_extended_countries_present(self):
        values = _get_literal_values(Country)
        for code in ["US", "CA", "JP", "AU", "BR", "MX", "IN", "CN", "KR", "ID"]:
            assert code in values, f"Extended country '{code}' missing"

    def test_no_duplicate_country_codes(self):
        values = _get_literal_values(Country)
        assert len(values) == len(set(values)), "Duplicate country codes found"


class TestCurrency:
    def test_all_currency_codes_are_three_letter_uppercase(self):
        for code in _get_literal_values(Currency):
            assert len(code) == 3, f"Currency code '{code}' is not 3 characters"
            assert code == code.upper(), f"Currency code '{code}' is not uppercase"

    def test_original_currencies_present(self):
        values = _get_literal_values(Currency)
        for code in ["EUR", "USD", "CHF", "GBP"]:
            assert code in values, f"Original currency '{code}' missing"

    def test_extended_currencies_present(self):
        values = _get_literal_values(Currency)
        for code in ["AUD", "CAD", "JPY", "BRL", "MXN", "INR", "CNY", "KRW", "IDR"]:
            assert code in values, f"Extended currency '{code}' missing"

    def test_no_duplicate_currency_codes(self):
        values = _get_literal_values(Currency)
        assert len(values) == len(set(values)), "Duplicate currency codes found"
