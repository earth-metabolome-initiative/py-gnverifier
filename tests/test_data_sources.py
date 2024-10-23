from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException

from pygnverifier.data_sources import DataSource, DataSourceClient


@pytest.fixture
def mock_data():
    return [
        {
            "id": 1,
            "uuid": "uuid1",
            "title": "Catalogue of Life",
            "titleShort": "COL",
            "version": "2024-09",
            "description": "Sample description",
            "homeURL": "https://www.catalogueoflife.org",
            "isOutlinkReady": True,
            "curation": "Curated",
            "hasTaxonData": True,
            "recordCount": 1000,
            "updatedAt": "2024-10-08",
        },
        {
            "id": 2,
            "uuid": "uuid2",
            "title": "Biodiversity Heritage Library",
            "titleShort": "BHL",
            "version": "2024-08",
            "description": "Sample description",
            "homeURL": "https://www.biodiversitylibrary.org",
            "isOutlinkReady": True,
            "curation": "Curated",
            "hasTaxonData": True,
            "recordCount": 500,
            "updatedAt": "2024-09-08",
        },
    ]


@patch("requests.get")
def test_get_data_sources(mock_get, mock_data):
    # Mock the response from the data sources endpoint
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data
    mock_get.return_value = mock_response

    client = DataSourceClient()
    data_sources = client.get_data_sources()

    assert len(data_sources) == len(mock_data)
    assert isinstance(data_sources[0], DataSource)
    assert data_sources[0].title == "Catalogue of Life"


@patch("requests.get")
def test_get_data_sources_empty(mock_get):
    # Mock the response with an empty list
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    client = DataSourceClient()
    data_sources = client.get_data_sources()

    assert len(data_sources) == 0


@patch("requests.get")
def test_get_data_sources_error(mock_get):
    # Mock the response with an error status
    mock_get.side_effect = RequestException("Server error")

    client = DataSourceClient()
    with pytest.raises(RequestException):
        client.get_data_sources()
