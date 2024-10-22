from unittest.mock import MagicMock, patch

import pytest

from pygnverifier.verification import GNVerifier, GNVerifierResponse, VerificationRequest


@pytest.fixture
def verification_request():
    return VerificationRequest(names=["Pomatomus saltatrix"])


@patch("requests.post")
def test_verify_request(mock_post, verification_request):
    # Mock the response from the GNVerifier API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "metadata": {"namesNumber": 1},
        "names": [{"name": "Pomatomus saltatrix", "matchType": "Exact"}],
    }
    mock_post.return_value = mock_response

    verifier = GNVerifier()
    response = verifier.verify(verification_request)

    assert isinstance(response, GNVerifierResponse)
    assert response.get_metadata() == {"namesNumber": 1}
    assert len(response.get_names()) == 1
    assert response.get_names()[0]["input_name"] == "Pomatomus saltatrix"
