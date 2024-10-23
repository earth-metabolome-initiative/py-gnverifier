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

    # Mock the pretty print and export as JSON behaviors
    with (
        patch.object(mock_response, "print_formatted_names") as mock_print,
        patch.object(
            mock_response, "export_as_json", return_value='{"input_name": "Pomatomus saltatrix"}'
        ) as mock_export,
    ):
        # Test the pretty output format
        result = runner.invoke(
            cli,
            [
                "verify",
                "-n",
                "Pomatomus saltatrix, Bubo bubo",
                "--with-stats",
                "--verbose",
                "--output-format",
                "pretty",
            ],
        )
        assert result.exit_code == 0
        mock_print.assert_called_once()
        mock_export.assert_not_called()

        # Reset the mock to verify JSON output behavior
        mock_print.reset_mock()

        # Test the JSON output format
        result = runner.invoke(cli, ["verify", "-n", "Pomatomus saltatrix, Bubo bubo", "--output-format", "json"])
        assert result.exit_code == 0
        mock_export.assert_called_once()
        mock_print.assert_not_called()
        assert '{"input_name": "Pomatomus saltatrix"}' in result.output


@patch("pygnverifier.cli.DataSourceClient")  # Adjusted path to match cli.py imports
def test_data_sources_command_pretty(mock_data_source_client, runner):
    # Mocking DataSourceClient's get_data_sources method
    mock_client_instance = MagicMock()
    mock_data_source_client.return_value = mock_client_instance
    mock_client_instance.get_data_sources.return_value = [
        MagicMock(
            datasource_id=1,
            title="Catalogue of Life",
            version="2024-09-25",
            record_count=5209963,
            uuid="d4df2968-4257-4ad9-ab81-bedbbfb25e2a",
            curation="Curated",
            updated_at="2024-10-08",
        )
    ]

    mock_client_instance.display_data_sources = MagicMock()

    result = runner.invoke(cli, ["data-sources", "--output-format", "pretty"])

    assert result.exit_code == 0
    mock_client_instance.display_data_sources.assert_called_once()


@patch("pygnverifier.cli.DataSourceClient")  # Adjusted path to match cli.py imports
def test_data_sources_command_json(mock_data_source_client, runner):
    # Mocking DataSourceClient's get_data_sources method
    mock_client_instance = MagicMock()
    mock_data_source_client.return_value = mock_client_instance
    mock_client_instance.get_data_sources.return_value = [
        MagicMock(
            datasource_id=1,
            title="Catalogue of Life",
            version="2024-09-25",
            record_count=5209963,
            uuid="d4df2968-4257-4ad9-ab81-bedbbfb25e2a",
            curation="Curated",
            updated_at="2024-10-08",
        )
    ]

    mock_client_instance.export_data_sources_as_json.return_value = (
        '[{"id": 1, "title": "Catalogue of Life", "version": "2024-09-25"}]'
    )

    result = runner.invoke(cli, ["data-sources", "--output-format", "json"])

    assert result.exit_code == 0
    assert "Catalogue of Life" in result.output


@patch("pygnverifier.cli.DataSourceClient")  # Adjusted path to match cli.py imports
def test_data_sources_command_json_to_file(mock_data_source_client, runner, tmp_path):
    # Mocking DataSourceClient's get_data_sources method
    mock_client_instance = MagicMock()
    mock_data_source_client.return_value = mock_client_instance
    mock_client_instance.get_data_sources.return_value = [
        MagicMock(
            datasource_id=1,
            title="Catalogue of Life",
            version="2024-09-25",
            record_count=5209963,
            uuid="d4df2968-4257-4ad9-ab81-bedbbfb25e2a",
            curation="Curated",
            updated_at="2024-10-08",
        )
    ]

    mock_client_instance.export_data_sources_as_json.return_value = (
        '[{"id": 1, "title": "Catalogue of Life", "version": "2024-09-25"}]'
    )

    output_file = tmp_path / "data_sources.json"
    result = runner.invoke(cli, ["data-sources", "--output-format", "json", "--output-file", str(output_file)])

    assert result.exit_code == 0
    with open(output_file) as file:
        content = file.read()
        assert "Catalogue of Life" in content


# Example Usage of the CLI

#     Verify scientific names with pretty output:

#     sh

# python pygnverifier/cli.py verify -n "Pomatomus saltatrix, Bubo bubo" --with-stats --verbose

# This command verifies the scientific names "Pomatomus saltatrix" and "Bubo bubo" and displays the results in a formatted way.

# Verify scientific names with JSON output:

# sh

# python pygnverifier/cli.py verify -n "Pomatomus saltatrix, Bubo bubo" --with-stats --verbose --output-format json

# This command verifies the names and returns the output in JSON format.

# Export verification results to a JSON file:

# sh

# python pygnverifier/cli.py verify -n "Pomatomus saltatrix, Bubo bubo" --with-stats --output-format json --output-file verified.json

# This command exports the verification results as a JSON file named verified.json.

# Display data sources in a pretty table:

# sh

# python pygnverifier/cli.py data-sources --output-format pretty --sort-key record_count --descending True

# This command displays the data sources in a formatted table, sorted by record count in descending order.

# Export data sources to a JSON file:

# sh

# python pygnverifier/cli.py data-sources --output-format json --output-file data_sources.json

# This command exports the data sources as a JSON file named data_sources.json.

# Display data sources in JSON format in the terminal:

# sh

# python pygnverifier/cli.py data-sources --output-format json

# This command outputs the data sources in raw JSON format to the terminal.
