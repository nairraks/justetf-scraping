"""Shared fixtures for justetf_scraping tests."""

import pytest


@pytest.fixture
def sample_raw_row():
    """A single raw row as returned by the JustETF API."""
    return {
        "isin": "IE00B4L5Y983",
        "wkn": "A0RPWH",
        "ticker": "EUNL",
        "valorNumber": "10737066",
        "name": "iShares Core MSCI World UCITS ETF USD (Acc)",
        "inceptionDate": "25.09.09",
        "strategy": "Long-only",
        "domicileCountry": "Ireland",
        "fundCurrency": "USD",
        "hasSecuritiesLending": "Yes",
        "distributionPolicy": "Accumulating",
        "ter": "0.20%",
        "replicationMethod": "Optimized sampling",
        "fundSize": "85123",
        "sustainable": "No",
        "numberOfHoldings": "1483",
        "ytdReturnCUR": "5.23%",
        "weekReturnCUR": "1.02%",
        "monthReturnCUR": "3.45%",
        "threeMonthReturnCUR": "7.89%",
        "sixMonthReturnCUR": "12.34%",
        "yearReturnCUR": "22.15%",
        "threeYearReturnCUR": "35.67%",
        "fiveYearReturnCUR": "78.90%",
        "yearReturn1CUR": "22.15%",
        "yearReturn2CUR": "18.90%",
        "yearReturn3CUR": "-12.45%",
        "yearReturn4CUR": "28.70%",
        "currentDividendYield": "-",
        "yearDividendYield": "-",
        "yearVolatilityCUR": "12.50%",
        "threeYearVolatilityCUR": "15.30%",
        "fiveYearVolatilityCUR": "16.80%",
        "yearReturnPerRiskCUR": "1.77",
        "threeYearReturnPerRiskCUR": "0.78",
        "fiveYearReturnPerRiskCUR": "0.94",
        "maxDrawdownCUR": "-33.72%",
        "yearMaxDrawdownCUR": "-5.23%",
        "threeYearMaxDrawdownCUR": "-18.90%",
        "fiveYearMaxDrawdownCUR": "-33.72%",
    }


@pytest.fixture
def sample_raw_row_hedged(sample_raw_row):
    """A raw row with hedged currency."""
    row = sample_raw_row.copy()
    row["fundCurrency"] = "GBP Hedged"
    return row


@pytest.fixture
def mock_html_response():
    """Minimal HTML response containing the Wicket counter pattern."""
    return (
        '<html><body>'
        '3-1.0-container-tabsContentContainer-tabsContentRepeater-'
        '1-container-content-etfsTablePanel&search=ETFS&_wicket=1'
        '</body></html>'
    )
