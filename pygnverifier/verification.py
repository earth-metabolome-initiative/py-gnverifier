"""Improved module to call the gnverifier API."""

import json
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
        names : list[str]
            List of scientific names to be verified.
        data_sources : Optional[list[int]], optional
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
        self.metadata = Metadata(data.get("metadata", {}))
        self.names = [NameResult(name_data) for name_data in data.get("names", [])]

    def get_metadata(self) -> "Metadata":
        """Return metadata from the response."""
        return self.metadata

    def get_names(self) -> list["NameResult"]:
        """Return a list of NameResult objects representing the names."""
        return self.names

    def print_formatted_names(self) -> None:
        """Print formatted names in a more readable way."""
        for name in self.get_names():
            name.print_details()

    def print_metadata(self) -> None:
        """Print the metadata information in a readable format."""
        self.metadata.print_details()

    def export_as_json(self, file_path: Optional[str] = None) -> str:
        """Export the GNVerifier response as a JSON string or save to a file.

        Parameters
        ----------
        file_path : Optional[str]
            Path to save the JSON file. If None, the JSON string will be returned.

        Returns
        -------
        str
            A JSON string representing the response if file_path is None.
        """
        json_data = json.dumps(
            {"metadata": self.metadata.to_dict(), "names": [name.to_dict() for name in self.names]}, indent=2
        )

        if file_path:
            with open(file_path, "w") as json_file:
                json_file.write(json_data)
        return json_data


class Metadata:
    """Class to encapsulate metadata from the GNVerifier API response."""

    def __init__(self, data: dict):
        self.names_number = data.get("namesNumber", 0)
        self.with_stats = data.get("withStats", False)
        self.data_sources = data.get("dataSources", [])
        self.main_taxon_threshold = data.get("mainTaxonThreshold", 0.0)
        self.stats_names_num = data.get("statsNamesNum", 0)
        self.main_taxon = data.get("mainTaxon", "N/A")
        self.main_taxon_percentage = data.get("mainTaxonPercentage", 0.0)
        self.kingdom = data.get("kingdom", "N/A")
        self.kingdom_percentage = data.get("kingdomPercentage", 0.0)
        self.kingdoms = data.get("kingdoms", [])

    def print_details(self) -> None:
        """Print metadata details in a readable format."""
        print("Metadata Information:")
        print(f"  Number of Names: {self.names_number}")
        print(f"  With Stats: {self.with_stats}")
        print(f"  Data Sources: {', '.join(map(str, self.data_sources))}")
        print(f"  Main Taxon Threshold: {self.main_taxon_threshold}")
        print(f"  Stats Names Number: {self.stats_names_num}")
        print(f"  Main Taxon: {self.main_taxon} ({self.main_taxon_percentage * 100:.2f}%)")
        print(f"  Kingdom: {self.kingdom} ({self.kingdom_percentage * 100:.2f}%)")
        print("  Kingdoms:")
        for kingdom in self.kingdoms:
            print(f"    - {kingdom['kingdomName']}: {kingdom['namesNumber']} ({kingdom['percentage'] * 100:.2f}%)")

    def to_dict(self) -> dict:
        """Return a dictionary representation of the metadata."""
        return {
            "namesNumber": self.names_number,
            "withStats": self.with_stats,
            "dataSources": self.data_sources,
            "mainTaxonThreshold": self.main_taxon_threshold,
            "statsNamesNum": self.stats_names_num,
            "mainTaxon": self.main_taxon,
            "mainTaxonPercentage": self.main_taxon_percentage,
            "kingdom": self.kingdom,
            "kingdomPercentage": self.kingdom_percentage,
            "kingdoms": self.kingdoms,
        }


class NameResult:
    """Class to encapsulate name result information from the GNVerifier API response."""

    def __init__(self, data: dict):
        self.input_name = data.get("name", "N/A")
        self.cardinality = data.get("cardinality", 0)
        self.match_type = data.get("matchType", "N/A")

        best_result = data.get("bestResult", {})
        self.data_source_id = best_result.get("dataSourceId", "N/A")
        self.data_source_title = best_result.get("dataSourceTitleShort", "N/A")
        self.curation = best_result.get("curation", "N/A")
        self.record_id = best_result.get("recordId", "N/A")
        self.outlink = best_result.get("outlink", "N/A")
        self.entry_date = best_result.get("entryDate", "N/A")
        self.sort_score = best_result.get("sortScore", 0.0)
        self.matched_name_id = best_result.get("matchedNameID", "N/A")
        self.matched_name = best_result.get("matchedName", "N/A")
        self.matched_cardinality = best_result.get("matchedCardinality", 0)
        self.matched_canonical_simple = best_result.get("matchedCanonicalSimple", "N/A")
        self.matched_canonical_full = best_result.get("matchedCanonicalFull", "N/A")
        self.current_record_id = best_result.get("currentRecordId", "N/A")
        self.current_name_id = best_result.get("currentNameId", "N/A")
        self.current_name = best_result.get("currentName", "N/A")
        self.current_cardinality = best_result.get("currentCardinality", 0)
        self.current_canonical_simple = best_result.get("currentCanonicalSimple", "N/A")
        self.current_canonical_full = best_result.get("currentCanonicalFull", "N/A")
        self.taxonomic_status = best_result.get("taxonomicStatus", "N/A")
        self.is_synonym = best_result.get("isSynonym", False)
        self.classification_path = best_result.get("classificationPath", "N/A")
        self.classification_ranks = best_result.get("classificationRanks", "N/A")
        self.classification_ids = best_result.get("classificationIds", "N/A")
        self.edit_distance = best_result.get("editDistance", 0)
        self.stem_edit_distance = best_result.get("stemEditDistance", 0)
        self.match_type_detail = best_result.get("matchType", "N/A")
        self.score_details = best_result.get("scoreDetails", {})

    def print_details(self) -> None:
        """Print name result details in a readable format."""
        print(f"Input Name: {self.input_name}")
        print(f"  Match Type: {self.match_type}")
        print(f"  Best Matched Name: {self.matched_name}")
        print(f"  Taxonomic Status: {self.taxonomic_status}")
        print(f"  Classification Path: {self.classification_path}")
        print(f"  Source Title: {self.data_source_title}")
        print(f"  Source Link: {self.outlink}")
        print()

    def to_dict(self) -> dict:
        """Return a dictionary representation of the name result."""
        return {
            "inputName": self.input_name,
            "cardinality": self.cardinality,
            "matchType": self.match_type,
            "bestResult": {
                "dataSourceId": self.data_source_id,
                "dataSourceTitleShort": self.data_source_title,
                "curation": self.curation,
                "recordId": self.record_id,
                "outlink": self.outlink,
                "entryDate": self.entry_date,
                "sortScore": self.sort_score,
                "matchedNameID": self.matched_name_id,
                "matchedName": self.matched_name,
                "matchedCardinality": self.matched_cardinality,
                "matchedCanonicalSimple": self.matched_canonical_simple,
                "matchedCanonicalFull": self.matched_canonical_full,
                "currentRecordId": self.current_record_id,
                "currentNameId": self.current_name_id,
                "currentName": self.current_name,
                "currentCardinality": self.current_cardinality,
                "currentCanonicalSimple": self.current_canonical_simple,
                "currentCanonicalFull": self.current_canonical_full,
                "taxonomicStatus": self.taxonomic_status,
                "isSynonym": self.is_synonym,
                "classificationPath": self.classification_path,
                "classificationRanks": self.classification_ranks,
                "classificationIds": self.classification_ids,
                "editDistance": self.edit_distance,
                "stemEditDistance": self.stem_edit_distance,
                "matchType": self.match_type_detail,
                "scoreDetails": self.score_details,
            },
        }


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

    # response.print_metadata()
    print(response.get_names()[0].is_synonym)

    # # Print response details
    # # response.print_formatted_names()
    # # Export response to JSON
    # json_data = response.export_as_json()

    # # Write JSON data directly to stdout
    # # Here we avoid using print() to prevent any extra characters being added
    # sys.stdout.write(json_data + "\n")
