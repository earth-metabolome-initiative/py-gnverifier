"""Improved module to call the gnverifier API."""

import time
import warnings
from typing import Any, Optional

from requests.exceptions import HTTPError
from tqdm import tqdm

from pygnverifier.base_api import BaseAPI


class VerificationRequest:
    """Class to encapsulate all parameters for a GNVerifier API call."""

    def __init__(
        self,
        names: list[str],
        data_sources: Optional[list[int]] = None,
        with_all_matches: bool = False,
        with_capitalization: bool = False,
        with_species_group: bool = False,
        with_uninomial_fuzzy_match: bool = False,
        with_stats: bool = False,
        main_taxon_threshold: float = 0.6,
    ):
        """Initialize request parameters for GNVerifier.

        Parameters
        ----------
        names : List[str]
            List of scientific names to be verified.
        data_sources : Optional[List[int]], optional
            List of data source IDs to limit the search, by default None.
        with_all_matches : bool, optional
            Return all possible matches, by default False.
        with_capitalization : bool, optional
            Consider capitalization when verifying, by default False.
        with_species_group : bool, optional
            Include species group in the verification, by default False.
        with_uninomial_fuzzy_match : bool, optional
            Enable fuzzy matching for uninomial names, by default False.
        with_stats : bool, optional
            Return statistics along with the results, by default False.
        main_taxon_threshold : float, optional
            Set the threshold for main taxon match, by default 0.6.
        """
        self.names = names
        self.data_sources = data_sources
        self.with_all_matches = with_all_matches
        self.with_capitalization = with_capitalization
        self.with_species_group = with_species_group
        self.with_uninomial_fuzzy_match = with_uninomial_fuzzy_match
        self.with_stats = with_stats
        self.main_taxon_threshold = main_taxon_threshold

    def to_dict(self) -> dict[str, Any]:
        """Convert request parameters to a dictionary suitable for the API call."""
        return {
            "nameStrings": self.names,
            "dataSources": self.data_sources,
            "withAllMatches": self.with_all_matches,
            "withCapitalization": self.with_capitalization,
            "withSpeciesGroup": self.with_species_group,
            "withUninomialFuzzyMatch": self.with_uninomial_fuzzy_match,
            "withStats": self.with_stats,
            "mainTaxonThreshold": self.main_taxon_threshold,
        }


class GNVerifier(BaseAPI):
    """Class to call the gnverifier API."""

    def __init__(self, timeout: int = 10, sleep: int = 2, user_agent: Optional[str] = None, verbose: bool = False):
        super().__init__(base_url="https://verifier.globalnames.org/api/v1", timeout=timeout)
        self.sleep = sleep
        self.user_agent = user_agent
        self.verbose = verbose

    def _sleeping_loading_bar(self, names_count: int, reason: str) -> None:
        """Display a loading bar proportional to the number of names.

        Parameters
        ----------
        names_count : int
            Number of names in the verification request.
        reason : str
            Reason for the loading bar (description).
        """
        if self.verbose:
            with tqdm(total=names_count, desc=reason, unit="name", dynamic_ncols=True) as pbar:
                for _ in range(names_count):
                    time.sleep(self.sleep)  # Simulate waiting between API calls
                    pbar.update(1)  # Update progress bar for each name

    def verify(self, request: VerificationRequest) -> "GNVerifierResponse":
        """Send a verification request to the GNVerifier API."""
        headers = {
            "User-Agent": self.user_agent or "pygnverifier/0.1.0",
        }

        try:
            # Specify "verifications" as the endpoint
            response = self._post(
                "verifications", json=request.to_dict(), headers=headers
            )  # Use the base class _post method
            return GNVerifierResponse(response.json())
        except HTTPError as http_err:
            warnings.warn(f"HTTP error occurred: {http_err}", stacklevel=2)
        except Exception as err:
            warnings.warn(f"Other error occurred: {err}", stacklevel=2)
        finally:
            self._sleeping_loading_bar(len(request.names), "Processing names")
        return GNVerifierResponse({})


class GNVerifierResponse:
    """Handles the response from the GNVerifier API."""

    def __init__(self, data: dict):
        """Initialize the GNVerifierResponse with the API response data."""
        self.metadata = data.get("metadata", {})
        self.names = data.get("names", [])

    def get_metadata(self) -> Any:
        """Return metadata from the response."""
        return self.metadata

    def get_names(self) -> list[dict]:
        """Return a more user-friendly representation of the names."""
        formatted_names = []
        for name_data in self.names:
            best_result = name_data.get("bestResult", {})
            formatted_name = {
                "input_name": name_data.get("name"),
                "match_type": name_data.get("matchType"),
                "best_matched_name": best_result.get("matchedName", "N/A"),
                "taxonomic_status": best_result.get("taxonomicStatus", "N/A"),
                "classification_path": best_result.get("classificationPath", "N/A"),
                "source_title": best_result.get("dataSourceTitleShort", "N/A"),
                "source_outlink": best_result.get("outlink", "N/A"),
            }
            formatted_names.append(formatted_name)
        return formatted_names

    def print_formatted_names(self) -> None:
        """Print formatted names in a more readable way."""
        for name in self.get_names():
            print(f"Input Name: {name['input_name']}")
            print(f"  Match Type: {name['match_type']}")
            print(f"  Best Matched Name: {name['best_matched_name']}")
            print(f"  Taxonomic Status: {name['taxonomic_status']}")
            print(f"  Classification Path: {name['classification_path']}")
            print(f"  Source Title: {name['source_title']}")
            print(f"  Source Link: {name['source_outlink']}")
            print()


# Example usage
if __name__ == "__main__":
    # Create a verification request
    request = VerificationRequest(
        names=["Pomatomus saltatrix", "Bubo bubo (Linnaeus, 1758)", "Isoetes longissimum"],
        data_sources=[1, 12, 170],
        with_all_matches=False,
        with_capitalization=False,
        with_species_group=False,
        with_uninomial_fuzzy_match=False,
        with_stats=True,
        main_taxon_threshold=0.6,
    )

    # Initialize the verifier and send the request
    gn = GNVerifier(verbose=True)
    response = gn.verify(request)

    # Print response details
    response.print_formatted_names()
