from typing import Optional

import click
import requests

from pygnverifier.data_sources import DataSourceClient
from pygnverifier.verification import GNVerifier, VerificationRequest


@click.group()
def cli() -> None:
    """
    Command Line Interface for interacting with the Global Names Verifier API.
    """
    pass


@click.command()
@click.option("--names", "-n", required=True, help="Comma-separated list of scientific names to verify.")
@click.option("--data-sources", "-d", help="Comma-separated list of data source IDs to limit the search.")
@click.option("--with-all-matches", is_flag=True, help="Return all possible matches.")
@click.option("--with-capitalization", is_flag=True, help="Consider capitalization when verifying.")
@click.option("--with-species-group", is_flag=True, help="Include species group in the verification.")
@click.option("--with-uninomial-fuzzy-match", is_flag=True, help="Enable fuzzy matching for uninomial names.")
@click.option("--with-stats", is_flag=True, help="Return statistics along with the results.")
@click.option("--main-taxon-threshold", default=0.6, type=float, help="Set the threshold for main taxon match.")
@click.option("--verbose", is_flag=True, help="Enable verbose mode.")
def verify(
    names: str,
    data_sources: Optional[str] = None,
    with_all_matches: bool = False,
    with_capitalization: bool = False,
    with_species_group: bool = False,
    with_uninomial_fuzzy_match: bool = False,
    with_stats: bool = False,
    main_taxon_threshold: float = 0.6,
    verbose: bool = False,
) -> None:
    """
    Verify scientific names using the GNVerifier API.
    """
    # Parse comma-separated names and data sources
    names_list = [name.strip() for name in names.split(",")]
    data_sources_list = [int(ds.strip()) for ds in data_sources.split(",")] if data_sources else None

    # Create a verification request
    request = VerificationRequest(
        names=names_list,
        data_sources=data_sources_list,
        with_all_matches=with_all_matches,
        with_capitalization=with_capitalization,
        with_species_group=with_species_group,
        with_uninomial_fuzzy_match=with_uninomial_fuzzy_match,
        with_stats=with_stats,
        main_taxon_threshold=main_taxon_threshold,
    )

    # Initialize the verifier and send the request
    verifier = GNVerifier(verbose=verbose)
    response = verifier.verify(request)

    # Print response details
    formatted_names = response.get_names()
    for name in formatted_names:
        print(f"Input Name: {name['input_name']}")
        print(f"  Match Type: {name['match_type']}")
        print(f"  Best Matched Name: {name['best_matched_name']}")
        print(f"  Taxonomic Status: {name['taxonomic_status']}")
        print(f"  Classification Path: {name['classification_path']}")
        print(f"  Source Title: {name['source_title']}")
        print(f"  Source Link: {name['source_outlink']}")
        print()


@click.command()
@click.option(
    "--output-format",
    type=click.Choice(["pretty", "json"], case_sensitive=False),
    default="pretty",
    help="Choose the output format: pretty table or raw JSON.",
)
@click.option(
    "--sort-key",
    type=str,
    default=None,
    help="Specify the field to sort the data sources by (e.g., 'record_count', 'title').",
)
@click.option(
    "--descending",
    type=bool,
    default=True,
    help="Set the order of sorting. True for descending, False for ascending.",
)
@click.option(
    "--output-file",
    type=str,
    default=None,
    help="Specify a file path to save the output as JSON.",
)
def data_sources(output_format: str, sort_key: Optional[str], descending: bool, output_file: Optional[str]) -> None:
    """
    List all available data sources from the GNVerifier API in different formats.
    """
    client = DataSourceClient()
    try:
        data_sources = client.get_data_sources()

        if output_format.lower() == "pretty":
            client.display_data_sources(data_sources, sort_key=sort_key, descending=descending)
        elif output_format.lower() == "json":
            json_data = client.export_data_sources_as_json(data_sources)
            if output_file:
                with open(output_file, "w") as file:
                    file.write(json_data)
                print(f"Data exported to {output_file}")
            else:
                print(json_data)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")


# Add commands to the CLI
cli.add_command(verify)
cli.add_command(data_sources)

if __name__ == "__main__":
    cli()


"""
Examples on how to use the CLI:

1. Verify scientific names:
   ```
   python pygnverifier/cli.py verify -n "Pomatomus saltatrix, Bubo bubo" --with-stats --verbose
   ```
   This command will verify the scientific names "Pomatomus saltatrix" and "Bubo bubo", include statistics, and enable verbose mode.

2. Verify scientific names with specific data sources:
   ```
   python pygnverifier/cli.py verify -n "Isoetes longissimum" -d "1, 12" --with-all-matches
   ```
   This command will verify the name "Isoetes longissimum" using data sources with IDs 1 and 12, and return all possible matches.

3. List available data sources:
   ```
   python pygnverifier/cli.py data-sources
   ```
   This command will list all available data sources from the GNVerifier API.
"""


"""
Examples on how to use the CLI:

1. Display data sources in a pretty table:
   ```
   python pygnverifier/cli.py data-sources --format pretty --sort-key record_count --descending True
   ```
   This command will display the data sources in a formatted table, sorted by record count in descending order.

2. Export data sources to a JSON file:
   ```
   python pygnverifier/cli.py data-sources --format json --output-file data_sources.json
   ```
   This command will export the data sources as a JSON file named 'data_sources.json'.

3. Display data sources in JSON format in the terminal:
   ```
   python pygnverifier/cli.py data-sources --format json
   ```
   This command will output the data sources in raw JSON format to the terminal.
"""
