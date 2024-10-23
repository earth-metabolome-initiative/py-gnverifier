"""Submodule for handling data sources from the Global Names Verifier API."""

from typing import Optional

import requests
from rich import print
from rich.console import Console
from rich.table import Table

from pygnverifier.base_api import BaseAPI


class DataSource:
    """Class to encapsulate information about a data source.

    Parameters
    ----------
    id : int
        Unique identifier for the data source.
    uuid : str, optional
        UUID for the data source. Defaults to 'N/A' if missing.
    title : str
        Full title of the data source.
    title_short : str, optional
        Short title of the data source. If missing, defaults to 'N/A'.
    version : str, optional
        Version of the data source. If missing, defaults to 'N/A'.
    description : str, optional
        Description of the data source. If missing, defaults to 'No description available'.
    home_url : str, optional
        URL for the home page of the data source. If missing, defaults to 'N/A'.
    is_outlink_ready : bool, optional
        Flag indicating if the data source is outlink ready. Defaults to False.
    curation : str, optional
        Curation status of the data source. If missing, defaults to 'Unknown'.
    has_taxon_data : bool, optional
        Flag indicating if the data source has taxon data. Defaults to False.
    record_count : int, optional
        Number of records in the data source. Defaults to 0 if not provided.
    updated_at : str, optional
        Date and time of the last update. If missing, defaults to 'N/A'.
    """

    def __init__(
        self,
        datasource_id: int,
        uuid: str = "N/A",
        title: str = "N/A",
        title_short: str = "N/A",
        version: str = "N/A",
        description: str = "No description available",
        home_url: str = "N/A",
        is_outlink_ready: bool = False,
        curation: str = "Unknown",
        has_taxon_data: bool = False,
        record_count: int = 0,
        updated_at: str = "N/A",
    ):
        self.datasource_id = datasource_id
        self.uuid = uuid
        self.title = title
        self.title_short = title_short
        self.version = version
        self.description = description
        self.home_url = home_url
        self.is_outlink_ready = is_outlink_ready
        self.curation = curation
        self.has_taxon_data = has_taxon_data
        self.record_count = record_count
        self.updated_at = updated_at

    def to_table_row(self) -> list[str]:
        """Return a list representing the row of the data source for the table."""
        return [
            str(self.datasource_id),
            self.title,
            self.version,
            self.uuid,
            str(self.record_count),
            self.curation,
            self.updated_at,
        ]


class DataSourceClient(BaseAPI):
    """Class to interact with the data sources endpoint of the Global Names Verifier API."""

    def __init__(self) -> None:
        super().__init__(base_url="https://verifier.globalnames.org/api/v1")

    def get_data_sources(self) -> list[DataSource]:
        """Get a list of data sources from the Global Names Verifier API.

        Returns
        -------
        list[DataSource]
            A list of DataSource objects with information about each data source.
        """
        response = self._get("data_sources")  # Using the base class method

        data_sources_data = response.json()
        data_sources = [
            DataSource(
                datasource_id=ds["id"],
                uuid=ds.get("uuid", "N/A"),  # Use default if key missing
                title=ds.get("title", "N/A"),  # Use default if key missing
                title_short=ds.get("titleShort", "N/A"),  # Use default if key missing
                version=ds.get("version", "N/A"),  # Use default if key missing
                description=ds.get("description", "No description available"),  # Use default if key missing
                home_url=ds.get("homeURL", "N/A"),  # Use default if key missing
                is_outlink_ready=ds.get("isOutlinkReady", False),  # Use default if key missing
                curation=ds.get("curation", "Unknown"),  # Use default if key missing
                has_taxon_data=ds.get("hasTaxonData", False),  # Use default if key missing
                record_count=ds.get("recordCount", 0),  # Use default if key missing
                updated_at=ds.get("updatedAt", "N/A"),  # Use default if key missing
            )
            for ds in data_sources_data
        ]
        return data_sources

    def display_data_sources(
        self, data_sources: list[DataSource], sort_key: Optional[str] = None, descending: bool = True
    ) -> None:
        """Display data sources in a table format, optionally sorted by a key.

        Parameters
        ----------
        data_sources : list[DataSource]
            A list of DataSource objects to be displayed.
        sort_key : Optional[str] = None
            Key function to sort the data sources. If None, no sorting is applied.
        descending : bool = True
            Flag to indicate if the data sources should be sorted in descending
        """
        if sort_key:
            data_sources = sorted(data_sources, key=lambda ds: getattr(ds, sort_key), reverse=descending)

        # Create a single table for all data sources
        table = Table(title="All Data Sources Information", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Title", style="green")
        table.add_column("Version", style="yellow")
        table.add_column("UUID", style="magenta")
        table.add_column("Record Count", style="red")
        table.add_column("Curation", style="blue")
        table.add_column("Updated At", style="white")

        for ds in data_sources:
            table.add_row(*ds.to_table_row())

        console = Console()
        console.print(table)


if __name__ == "__main__":
    client = DataSourceClient()
    try:
        data_sources = client.get_data_sources()

        # Example usage: Display data sources sorted by record count
        client.display_data_sources(data_sources, sort_key="record_count", descending=True)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
