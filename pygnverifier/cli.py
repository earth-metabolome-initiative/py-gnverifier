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
@click.option("--names", "-n", multiple=True, required=True, help="Scientific names to verify.")
@click.option("--data-sources", "-d", multiple=True, type=int, help="List of data source IDs to limit the search.")
@click.option("--with-all-matches", is_flag=True, help="Return all possible matches.")
@click.option("--with-capitalization", is_flag=True, help="Consider capitalization when verifying.")
@click.option("--with-species-group", is_flag=True, help="Include species group in the verification.")
@click.option("--with-uninomial-fuzzy-match", is_flag=True, help="Enable fuzzy matching for uninomial names.")
@click.option("--with-stats", is_flag=True, help="Return statistics along with the results.")
@click.option("--main-taxon-threshold", default=0.6, type=float, help="Set the threshold for main taxon match.")
@click.option("--verbose", is_flag=True, help="Enable verbose mode.")
def verify(
    names: list[str],
    data_sources: Optional[list[int]] = None,
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
    # Create a verification request
    request = VerificationRequest(
        names=list(names),
        data_sources=list(data_sources) if data_sources else None,
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
    response.print_formatted_names()


@click.command()
def data_sources() -> None:
    """
    List all available data sources from the GNVerifier API.
    """
    client = DataSourceClient()
    try:
        data_sources = client.get_data_sources()
        for ds in data_sources:
            print(ds)
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
   python pygnverifier/cli.py verify -n "Pomatomus saltatrix" -n "Bubo bubo" --with-stats --verbose
   ```
   This command will verify the scientific names "Pomatomus saltatrix" and "Bubo bubo", include statistics, and enable verbose mode.

2. Verify scientific names with specific data sources:
   ```
   python pygnverifier/gnverifier_cli.py verify -n "Isoetes longissimum" -d 1 -d 12 --with-all-matches
   ```
   This command will verify the name "Isoetes longissimum" using data sources with IDs 1 and 12, and return all possible matches.

3. List available data sources:
   ```
   python pygnverifier/gnverifier_cli.py data-sources
   ```
   This command will list all available data sources from the GNVerifier API.
"""
