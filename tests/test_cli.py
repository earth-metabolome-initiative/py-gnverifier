from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from pygnverifier.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@patch("pygnverifier.cli.GNVerifier")  # Adjusted path to match cli.py imports
@patch("pygnverifier.cli.VerificationRequest")  # Adjusted path to match cli.py imports
def test_verify_command(mock_verification_request, mock_gnverifier, runner):
    # Mocking GNVerifier and VerificationRequest behavior
    mock_gnverifier_instance = MagicMock()
    mock_gnverifier.return_value = mock_gnverifier_instance
    mock_response = MagicMock()
    mock_gnverifier_instance.verify.return_value = mock_response
    mock_response.get_names.return_value = [
        {
            "input_name": "Pomatomus saltatrix",
            "match_type": "Exact",
            "best_matched_name": "Pomatomus saltatrix",
            "taxonomic_status": "Accepted",
            "classification_path": "Animalia|Chordata|Vertebrata|...",
            "source_title": "Catalogue of Life",
            "source_outlink": "https://www.catalogueoflife.org/data/taxon/4LQWC",
        }
    ]

    result = runner.invoke(cli, ["verify", "-n", "Pomatomus saltatrix, Bubo bubo", "--with-stats", "--verbose"])

    assert result.exit_code == 0
    assert "Input Name: Pomatomus saltatrix" in result.output
    assert "Match Type: Exact" in result.output
    assert "Best Matched Name: Pomatomus saltatrix" in result.output


@patch("pygnverifier.cli.DataSourceClient")  # Adjusted path to match cli.py imports
def test_data_sources_command(mock_data_source_client, runner):
    # Mocking DataSourceClient's get_data_sources method
    mock_client_instance = MagicMock()
    mock_data_source_client.return_value = mock_client_instance
    mock_client_instance.get_data_sources.return_value = [
        MagicMock(title="Catalogue of Life", version="2024-09-25", record_count=5209963)
    ]

    result = runner.invoke(cli, ["data-sources"])

    assert result.exit_code == 0
    assert "Title: Catalogue of Life" in result.output
    assert "Version: 2024-09-25" in result.output
    assert "Record Count: 5209963" in result.output
