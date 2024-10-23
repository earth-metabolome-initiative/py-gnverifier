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
@click.option(
    "--output-format",
    type=click.Choice(["pretty", "json"], case_sensitive=False),
    default="pretty",
    help="Choose the output format: pretty or raw JSON.",
)
@click.option(
    "--output-file",
    type=str,
    default=None,
    help="Specify a file path to save the output as JSON.",
)
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
    output_format: str = "pretty",
    output_file: Optional[str] = None,
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

    if output_format.lower() == "json":
        json_data = response.export_as_json()
        if output_file:
            with open(output_file, "w") as file:
                file.write(json_data)
            print(f"Data exported to {output_file}")
        else:
            print(json_data)
    else:
        # Print response details in a pretty format
        response.print_formatted_names()


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
