"""Improved module to call the gnverifier API."""

from typing import Any

from pygnverifier.base_api import BaseAPI
from pygnverifier.data_sources import DataSource, DataSourceClient
from pygnverifier.exceptions import InvalidTaxonThresholdError, UnknownDataSourceError


class VerificationRequestConfiguration:
    """Class to encapsulate all parameters for a Verifier API call."""

    def __init__(self, email: str):
        """Initialize request parameters for Verifier."""
        self._data_sources: list[int] = []
        self._with_all_matches: bool = False
        self._with_capitalization: bool = False
        self._with_species_group: bool = False
        self._with_uninomial_fuzzy_match: bool = False
        self._with_stats: bool = False
        self._main_taxon_threshold: float = 0.6
        self._email: str = email
        self._data_sources_metadata: list[DataSource] = list(DataSourceClient(email).iter_data_sources())

    @property
    def email(self) -> str:
        """Return the email address used for the Verifier API."""
        return self._email

    def with_all_matches(self) -> "VerificationRequestConfiguration":
        """Set the withAllMatches parameter."""
        self._with_all_matches = True
        return self

    def with_capitalization(self) -> "VerificationRequestConfiguration":
        """Set the withCapitalization parameter."""
        self._with_capitalization = True
        return self

    def with_species_group(self) -> "VerificationRequestConfiguration":
        """Set the withSpeciesGroup parameter."""
        self._with_species_group = True
        return self

    def with_uninomial_fuzzy_match(self) -> "VerificationRequestConfiguration":
        """Set the withUninomialFuzzyMatch parameter."""
        self._with_uninomial_fuzzy_match = True
        return self

    def with_stats(self) -> "VerificationRequestConfiguration":
        """Set the withStats parameter."""
        self._with_stats = True
        return self

    def set_main_taxon_threshold(self, threshold: float) -> "VerificationRequestConfiguration":
        """Set the mainTaxonThreshold parameter."""
        if not 0.0 <= threshold <= 1.0:
            raise InvalidTaxonThresholdError(threshold)
        self._main_taxon_threshold = threshold
        return self

    def include_data_source(self, data_source_name: str) -> "VerificationRequestConfiguration":
        """Include a specific data source in the verification request."""
        identified_data_source_name: bool = False
        for data_source in self._data_sources_metadata:
            if data_source_name in (
                data_source.arg_name,
                data_source.short_arg_name,
                data_source.title,
                data_source.title_short,
            ):
                self._data_sources.append(data_source.datasource_id)
                identified_data_source_name = True
                break
        if not identified_data_source_name:
            raise UnknownDataSourceError(
                data_source=data_source_name,
                available_data_sources=[data_source.title for data_source in self._data_sources_metadata],
            )
        return self

    def build_request(self, names: list[str]) -> dict[str, Any]:
        """Convert request parameters to a dictionary suitable for the API call."""
        return {
            "nameStrings": names,
            "dataSources": self._data_sources,
            "withAllMatches": self._with_all_matches,
            "withCapitalization": self._with_capitalization,
            "withSpeciesGroup": self._with_species_group,
            "withUninomialFuzzyMatch": self._with_uninomial_fuzzy_match,
            "withStats": self._with_stats,
            "mainTaxonThreshold": self._main_taxon_threshold,
        }


class Metadata:
    """Class to encapsulate metadata from the Verifier API response."""

    def __init__(self, data: dict):
        self._names_number = data.get("namesNumber", 0)
        self._with_stats = data.get("withStats", False)
        self._data_sources = data.get("dataSources", [])
        self._main_taxon_threshold = data.get("mainTaxonThreshold", 0.0)
        self._stats_names_num = data.get("statsNamesNum", 0)
        self._main_taxon = data.get("mainTaxon", "N/A")
        self._main_taxon_percentage = data.get("mainTaxonPercentage", 0.0)
        self._kingdom = data.get("kingdom", "N/A")
        self._kingdom_percentage = data.get("kingdomPercentage", 0.0)
        self._kingdoms = data.get("kingdoms", [])

    def print_details(self) -> None:
        """Print metadata details in a readable format."""
        print("Metadata Information:")
        print(f"  Number of Names: {self._names_number}")
        print(f"  With Stats: {self._with_stats}")
        print(f"  Data Sources: {', '.join(map(str, self._data_sources))}")
        print(f"  Main Taxon Threshold: {self._main_taxon_threshold}")
        print(f"  Stats Names Number: {self._stats_names_num}")
        print(f"  Main Taxon: {self._main_taxon} ({self._main_taxon_percentage * 100:.2f}%)")
        print(f"  Kingdom: {self._kingdom} ({self._kingdom_percentage * 100:.2f}%)")
        print("  Kingdoms:")
        for kingdom in self._kingdoms:
            print(f"    - {kingdom['kingdomName']}: {kingdom['namesNumber']} ({kingdom['percentage'] * 100:.2f}%)")

    def to_dict(self) -> dict:
        """Return a dictionary representation of the metadata."""
        return {
            "namesNumber": self._names_number,
            "withStats": self._with_stats,
            "dataSources": self._data_sources,
            "mainTaxonThreshold": self._main_taxon_threshold,
            "statsNamesNum": self._stats_names_num,
            "mainTaxon": self._main_taxon,
            "mainTaxonPercentage": self._main_taxon_percentage,
            "kingdom": self._kingdom,
            "kingdomPercentage": self._kingdom_percentage,
            "kingdoms": self._kingdoms,
        }


class NameResult:
    """Class to encapsulate name result information from the Verifier API response."""

    def __init__(self, data: dict):
        self._input_name = data.get("name", "N/A")
        self._cardinality = data.get("cardinality", 0)
        self._match_type = data.get("matchType", "N/A")
        self._curation = data.get("curation", "N/A")
        self._results: list[BestResult] = [BestResult(result) for result in data.get("results", [])]

    def print_details(self) -> None:
        """Print name result details in a readable format."""
        print(f"Input Name: {self._input_name}")
        print(f"  Match Type: {self._match_type}")
        for idx, result in enumerate(self._results, start=1):
            print(f"  Result {idx}:")
            result.print_details()

    def to_dict(self) -> dict:
        """Return a dictionary representation of the name result."""
        return {
            "inputName": self._input_name,
            "cardinality": self._cardinality,
            "matchType": self._match_type,
            "curation": self._curation,
            "results": [result.to_dict() for result in self._results],
        }


class VerifierResponse:
    """Handles the response from the Verifier API."""

    def __init__(self, metadata: Metadata, names: list[NameResult]):
        """Initialize the VerifierResponse with the API response data."""
        self._metadata = metadata
        self._names = names

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerifierResponse":
        """Create a VerifierResponse object from a dictionary."""
        return cls(
            metadata=Metadata(data.get("metadata", {})),
            names=[NameResult(name) for name in data.get("names", [])],
        )

    def to_dict(self) -> dict:
        """Return a dictionary representation of the VerifierResponse."""
        return {
            "metadata": self._metadata.to_dict(),
            "names": [name.to_dict() for name in self._names],
        }

    @property
    def metadata(self) -> Metadata:
        """Return metadata from the response."""
        return self._metadata

    @property
    def names(self) -> list[NameResult]:
        """Return a list of NameResult objects representing the names."""
        return self._names

    def print_formatted_names(self) -> None:
        """Print formatted names in a more readable way."""
        for name in self._names:
            name.print_details()

    def print_metadata(self) -> None:
        """Print the metadata information in a readable format."""
        self.metadata.print_details()


class BestResult:
    """Class to represent each of the best results for a name."""

    def __init__(self, data: dict):
        self.data_source_id = data["dataSourceId"]
        self.data_source_title = data["dataSourceTitleShort"]
        self.curation = data["curation"]
        self.record_id = data["recordId"]
        self.outlink = data["outlink"]
        self.entry_date = data["entryDate"]
        self.sort_score = data["sortScore"]
        self.matched_name_id = data["matchedNameID"]
        self.matched_name = data["matchedName"]
        self.matched_cardinality = data["matchedCardinality"]
        self.matched_canonical_simple = data["matchedCanonicalSimple"]
        self.matched_canonical_full = data["matchedCanonicalFull"]
        self.current_record_id = data["currentRecordId"]
        self.current_name_id = data["currentNameId"]
        self.current_name = data["currentName"]
        self.current_cardinality = data["currentCardinality"]
        self.current_canonical_simple = data["currentCanonicalSimple"]
        self.current_canonical_full = data["currentCanonicalFull"]
        self.taxonomic_status = data["taxonomicStatus"]
        self.is_synonym = data["isSynonym"]
        self.edit_distance = data["editDistance"]
        self.stem_edit_distance = data["stemEditDistance"]
        self.match_type_detail = data["matchType"]
        self.score_details = data["scoreDetails"]

        classification_path = data.get("classificationPath", "")
        classification_ranks = data.get("classificationRanks", "")
        classification_ids = data.get("classificationIds", "")
        self.classification = Classification(classification_path, classification_ranks, classification_ids)

    def print_details(self) -> None:
        """Print best result details in a readable format."""
        print(f"    Data Source Title: {self.data_source_title}")
        print(f"    Matched Name: {self.matched_name}")
        print(f"    Taxonomic Status: {self.taxonomic_status}")
        self.classification.print_classification()
        print(f"    Source Link: {self.outlink}")
        print()

    def to_dict(self) -> dict:
        """Return a dictionary representation of the best result."""
        return {
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
            "editDistance": self.edit_distance,
            "stemEditDistance": self.stem_edit_distance,
            "matchType": self.match_type_detail,
            "scoreDetails": self.score_details,
            "classification": self.classification.to_dict(),
        }


class Classification:
    """Class to encapsulate and parse classification details of a taxon."""

    def __init__(self, path: str, ranks: str, ids: str):
        self.path = path.split("|")
        self.ranks = ranks.split("|")
        self.ids = ids.split("|")

    def get_classification_dict(self) -> list[dict]:
        """Return a list of dictionaries, each representing a taxonomic level."""
        return [{"rank": rank, "name": name, "id": id_} for rank, name, id_ in zip(self.ranks, self.path, self.ids)]

    def print_classification(self) -> None:
        """Print classification details in a readable format."""
        print("Classification Details:")
        for rank, name, id_ in zip(self.ranks, self.path, self.ids):
            print(f"  Rank: {rank}, Name: {name}, ID: {id_}")

    def to_dict(self) -> dict:
        """Return a dictionary representation of the classification."""
        return {
            "path": self.path,
            "ranks": self.ranks,
            "ids": self.ids,
            "classification": self.get_classification_dict(),
        }


class Verifier(BaseAPI):
    """Class to call the gnverifier API."""

    def __init__(self, configuration: VerificationRequestConfiguration):
        """Initialize the Verifier API client."""
        super().__init__(configuration.email)
        self._configuration: VerificationRequestConfiguration = configuration

    def verify(self, names: list[str]) -> VerifierResponse:
        """Send a verification request to the Verifier API."""
        return VerifierResponse.from_dict(
            self._post(
                "verifications",
                json=self._configuration.build_request(names),
            )
        )
