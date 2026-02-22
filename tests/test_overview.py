"""Tests for justetf_scraping.overview module."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from justetf_scraping.overview import (
    load_overview,
    load_raw_overview,
    make_etf_params,
)


class TestMakeEtfParams:
    def test_default_params(self):
        result = make_etf_params()
        assert result.startswith("search=ETF&productGroup=epg-longOnly")
        assert "&ls=any" in result

    def test_with_asset_class(self):
        result = make_etf_params(asset_class="class-equity")
        assert "&assetClass=class-equity" in result

    def test_with_region(self):
        result = make_etf_params(region="Europe")
        assert "&region=Europe" in result

    def test_with_country_alpha2(self):
        result = make_etf_params(country="GB")
        assert "&country=GB" in result

    def test_with_country_name(self):
        result = make_etf_params(country="Germany")
        assert "&country=DE" in result

    def test_with_invalid_country_raises(self):
        with pytest.raises(ValueError, match="not recognized"):
            make_etf_params(country="Atlantis")

    def test_with_instrument_currency(self):
        result = make_etf_params(instrument_currency="JPY")
        assert "&currency=JPY" in result

    def test_with_instrument_currency_none(self):
        result = make_etf_params(instrument_currency=None)
        assert "&currency=" not in result

    def test_with_exchange_none(self):
        result = make_etf_params(exchange=None)
        assert "&ls=" not in result

    def test_with_instrument(self):
        result = make_etf_params(instrument="ETF")
        assert "&instrumentType=ETF" in result

    def test_with_isin(self):
        result = make_etf_params(isin="IE00B4L5Y983")
        assert "&query=IE00B4L5Y983" in result

    def test_with_provider(self):
        result = make_etf_params(provider="iShares")
        assert "&ic=iShares" in result

    def test_with_index(self):
        result = make_etf_params(index="MSCI+World")
        assert "&index=MSCI+World" in result

    def test_with_multiple_params(self):
        result = make_etf_params(
            asset_class="class-bonds",
            region="Europe",
            instrument_currency="GBP",
        )
        assert "&assetClass=class-bonds" in result
        assert "&region=Europe" in result
        assert "&currency=GBP" in result


class TestLoadRawOverview:
    @patch("justetf_scraping.overview.requests.Session")
    def test_returns_list_of_dicts(self, mock_session_cls, mock_html_response):
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_session_cls.return_value.__exit__ = MagicMock(return_value=False)

        # Mock HTML response
        html_resp = MagicMock()
        html_resp.status_code = 200
        html_resp.text = mock_html_response

        # Mock POST response
        post_resp = MagicMock()
        post_resp.status_code = 200
        post_resp.json.return_value = {
            "data": [
                {"isin": "IE00B4L5Y983", "name": "Test ETF", "strategy": ""},
            ]
        }

        mock_session.get.return_value = html_resp
        mock_session.post.return_value = post_resp

        result = load_raw_overview(strategy="epg-longOnly")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["isin"] == "IE00B4L5Y983"

    @patch("justetf_scraping.overview.requests.Session")
    def test_deduplicates_across_strategies(self, mock_session_cls, mock_html_response):
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_session_cls.return_value.__exit__ = MagicMock(return_value=False)

        html_resp = MagicMock()
        html_resp.status_code = 200
        html_resp.text = mock_html_response

        # Return the same ETF for two different strategy calls
        post_resp = MagicMock()
        post_resp.status_code = 200
        post_resp.json.return_value = {
            "data": [{"isin": "IE00B4L5Y983", "name": "Test ETF"}]
        }

        mock_session.get.return_value = html_resp
        mock_session.post.return_value = post_resp

        result = load_raw_overview(strategy=None)  # Requests all strategies
        # Should deduplicate: only 1 entry even though 3 strategies called
        assert len(result) == 1

    @patch("justetf_scraping.overview.requests.Session")
    def test_instrument_currency_passed_through(
        self, mock_session_cls, mock_html_response
    ):
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_session_cls.return_value.__exit__ = MagicMock(return_value=False)

        html_resp = MagicMock()
        html_resp.status_code = 200
        html_resp.text = mock_html_response

        post_resp = MagicMock()
        post_resp.status_code = 200
        post_resp.json.return_value = {"data": []}

        mock_session.get.return_value = html_resp
        mock_session.post.return_value = post_resp

        load_raw_overview(
            strategy="epg-longOnly",
            instrument_currency="JPY",
        )

        # Verify the POST was called with etfsParams containing currency=JPY
        call_args = mock_session.post.call_args
        post_data = call_args[0][1] if len(call_args[0]) > 1 else call_args[1]
        assert "&currency=JPY" in post_data["etfsParams"]


class TestLoadOverview:
    @patch("justetf_scraping.overview.load_raw_overview")
    def test_returns_dataframe(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert isinstance(df, pd.DataFrame)

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_sets_isin_as_index(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert df.index.name == "isin"
        assert "IE00B4L5Y983" in df.index

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_renames_columns(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert "ticker" in df.columns
        assert "name" in df.columns
        assert "ter" in df.columns
        assert "last_year" in df.columns

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_converts_ter_to_float(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert df["ter"].dtype == "float64"
        assert df["ter"].iloc[0] == pytest.approx(0.20)

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_converts_bool_columns(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert df["securities_lending"].dtype == "bool"
        assert df["securities_lending"].iloc[0] == True  # noqa: E712 (numpy bool)
        assert df["is_sustainable"].dtype == "bool"
        assert df["is_sustainable"].iloc[0] == False  # noqa: E712 (numpy bool)

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_parses_inception_date(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert "inception_date" in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df["inception_date"])

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_adds_age_columns(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert "age_in_days" in df.columns
        assert "age_in_years" in df.columns
        assert df["age_in_days"].iloc[0] > 0

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_adds_hedged_column_false(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert "hedged" in df.columns
        assert df["hedged"].iloc[0] == False  # noqa: E712 (numpy bool)

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_adds_hedged_column_true(self, mock_get_raw, sample_raw_row_hedged):
        mock_get_raw.return_value = [sample_raw_row_hedged]
        df = load_overview(strategy="epg-longOnly")
        assert df["hedged"].iloc[0] == True  # noqa: E712 (numpy bool)

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_empty_response_returns_empty_df(self, mock_get_raw):
        mock_get_raw.return_value = []
        df = load_overview(strategy="epg-longOnly")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_converts_int64_columns(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        df = load_overview(strategy="epg-longOnly")
        assert df["size"].dtype == "Int64"
        assert df["size"].iloc[0] == 85123

    @patch("justetf_scraping.overview.load_raw_overview")
    def test_instrument_currency_passed_to_raw(self, mock_get_raw, sample_raw_row):
        mock_get_raw.return_value = [sample_raw_row]
        load_overview(strategy="epg-longOnly", instrument_currency="JPY")
        mock_get_raw.assert_called_once()
        call_kwargs = mock_get_raw.call_args
        # instrument_currency should be in the args passed to get_raw_overview
        # It's passed as a positional arg based on the function signature
        assert "JPY" in str(call_kwargs)
