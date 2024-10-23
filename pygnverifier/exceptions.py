"""Submodule providing exceptions for more semantically clear errors."""


class PyGNVerifierError(Exception):
    """Base class for all exceptions in the package."""


class UnknownDataSourceError(PyGNVerifierError):
    """Raised when an unknown data source is provided."""

    def __init__(self, data_source: str, available_data_sources: list[str]):
        super().__init__(f"Unknown data source '{data_source}'. Available data sources are: {available_data_sources}")


class InvalidTaxonThresholdError(PyGNVerifierError):
    """Raised when an invalid taxon threshold is provided."""

    def __init__(self, taxon_threshold: float):
        super().__init__(
            f"Invalid taxon threshold '{taxon_threshold}'. Taxon threshold must be a float between 0 and 1."
        )


class UnsupportedOutputFormatError(PyGNVerifierError):
    """Raised when an unsupported output format is provided."""

    def __init__(self, output_format: str, available_output_formats: list[str]):
        super().__init__(
            f"Unsupported output format '{output_format}'. Available output formats are: {available_output_formats}"
        )
