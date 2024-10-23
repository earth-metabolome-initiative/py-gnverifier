"""Test whether the verification functions work as expected."""

import compress_json
import pytest

from pygnverifier import VerificationRequestConfiguration, Verifier, VerifierResponse
from pygnverifier.exceptions import UnknownDataSourceError


def test_verify():
    """Test the verify function."""

    configuration: VerificationRequestConfiguration = VerificationRequestConfiguration(
        email="tmp@tmp.com"
    ).include_data_source("Catalogue of Life")

    verifier: Verifier = Verifier(configuration)

    for name in compress_json.local_load("data/names_to_resolve.json"):
        result: VerifierResponse = verifier.verify([name])
        print(result)


def test_improper_parametrization_verify():
    """Test the verify function."""

    with pytest.raises(UnknownDataSourceError):
        VerificationRequestConfiguration(email="tmp@tmp.com").include_data_source("open tree")
