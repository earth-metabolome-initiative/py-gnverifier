from unittest.mock import MagicMock, patch

from pygnverifier.data_sources import DataSource, DataSourceClient


@patch("requests.get")
def test_get_data_sources(mock_get):
    # Mock the response from the data sources endpoint
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
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
        }
    ]
    mock_get.return_value = mock_response

    client = DataSourceClient()
    data_sources = client.get_data_sources()

    assert len(data_sources) == 1
    assert isinstance(data_sources[0], DataSource)
    assert data_sources[0].title == "Catalogue of Life"
