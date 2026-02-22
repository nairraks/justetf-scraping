"""Tests for justetf_scraping.helpers module."""

import pytest
import requests

from justetf_scraping.helpers import (
    ASSET_CLASSES,
    EXCHANGES,
    INSTRUMENTS,
    REGIONS,
    STRATEGIES,
    USER_AGENT,
    assert_response_status_ok,
)


class TestMappingDictionaries:
    def test_strategies_has_expected_keys(self):
        expected = {"epg-longOnly", "epg-activeEtfs", "epg-shortAndLeveraged"}
        assert set(STRATEGIES.keys()) == expected

    def test_asset_classes_has_expected_keys(self):
        expected = {
            "class-equity", "class-bonds", "class-preciousMetals",
            "class-commodities", "class-currency", "class-realEstate",
            "class-moneyMarket",
        }
        assert set(ASSET_CLASSES.keys()) == expected

    def test_regions_has_expected_keys(self):
        expected = {
            "Africa", "Asia%2BPacific", "Eastern%2BEurope",
            "Emerging%2BMarkets", "Europe", "Latin%2BAmerica",
            "North%2BAmerica", "World",
        }
        assert set(REGIONS.keys()) == expected

    def test_exchanges_has_expected_keys(self):
        expected = {
            "MUND", "XETR", "XLON", "XPAR", "XSTU",
            "XSWX", "XMIL", "XAMS", "XBRU",
        }
        assert set(EXCHANGES.keys()) == expected

    def test_instruments_has_expected_keys(self):
        expected = {"ETC", "ETF", "ETN"}
        assert set(INSTRUMENTS.keys()) == expected

    def test_all_mapping_values_are_strings(self):
        for mapping in [STRATEGIES, ASSET_CLASSES, REGIONS, EXCHANGES, INSTRUMENTS]:
            for value in mapping.values():
                assert isinstance(value, str)


class TestUserAgent:
    def test_user_agent_is_nonempty_string(self):
        assert isinstance(USER_AGENT, str)
        assert len(USER_AGENT) > 0


class TestAssertResponseStatusOk:
    def test_raises_on_404(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        response = requests.models.Response()
        response.status_code = 404
        response._content = b"<html>Not Found</html>"

        with pytest.raises(RuntimeError, match="Got status 404"):
            assert_response_status_ok(response, "test-page")

    def test_raises_on_500(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        response = requests.models.Response()
        response.status_code = 500
        response._content = b"<html>Server Error</html>"

        with pytest.raises(RuntimeError, match="Got status 500"):
            assert_response_status_ok(response)

    def test_saves_error_page_with_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        response = requests.models.Response()
        response.status_code = 403
        response._content = b"<html>Forbidden</html>"

        with pytest.raises(RuntimeError):
            assert_response_status_ok(response, "my-request")

        error_file = tmp_path / "my-request-error-page.html"
        assert error_file.exists()
        assert error_file.read_text() == "<html>Forbidden</html>"

    def test_saves_error_page_without_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        response = requests.models.Response()
        response.status_code = 403
        response._content = b"<html>Forbidden</html>"

        with pytest.raises(RuntimeError):
            assert_response_status_ok(response)

        error_file = tmp_path / "error-page.html"
        assert error_file.exists()

    def test_does_not_raise_on_200(self):
        response = requests.models.Response()
        response.status_code = 200

        # Should not raise
        assert_response_status_ok(response)
