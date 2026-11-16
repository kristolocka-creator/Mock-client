from unittest.mock import patch, Mock
import pytest
import requests

from embedding_client import get_embedding


def test_success():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "embedding": [0.1, 0.2, 0.3]
    }

    with patch(
        "embedding_client.requests.post",
        return_value=fake_response
    ):
        result = get_embedding(
            "Привет",
            {
                "max_retries": 3,
                "initial_delay": 1,
                "multiplier": 2
            }
        )

    assert result == [0.1, 0.2, 0.3]


def test_retry_on_500():
    first_response = Mock()
    first_response.status_code = 500

    second_response = Mock()
    second_response.status_code = 200
    second_response.json.return_value = {
        "embedding": [0.1, 0.2, 0.3]
    }

    with patch(
        "embedding_client.requests.post",
        side_effect=[first_response, second_response]
    ) as mock_post:
        result = get_embedding(
            "Привет",
            {
                "max_retries": 1,
                "initial_delay": 0,
                "multiplier": 2
            }
        )

    assert result == [0.1, 0.2, 0.3]
    assert mock_post.call_count == 2


def test_permanent_error_404():
    fake_response = Mock()
    fake_response.status_code = 404

    with patch(
        "embedding_client.requests.post",
        return_value=fake_response
    ) as mock_post:
        with pytest.raises(
            RuntimeError,
            match="Permanent error: HTTP 404"
        ):
            get_embedding(
                "Привет",
                {
                    "max_retries": 3,
                    "initial_delay": 0,
                    "multiplier": 2
                }
            )

    assert mock_post.call_count == 1


def test_retry_on_timeout():
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "embedding": [0.1, 0.2, 0.3]
    }

    with patch(
        "embedding_client.requests.post",
        side_effect=[
            requests.exceptions.Timeout,
            fake_response
        ]
    ) as mock_post:
        result = get_embedding(
            "Привет",
            {
                "max_retries": 1,
                "initial_delay": 0,
                "multiplier": 2
            }
        )

    assert result == [0.1, 0.2, 0.3]
    assert mock_post.call_count == 2


def test_max_retries_zero():
    fake_response = Mock()
    fake_response.status_code = 500

    with patch(
        "embedding_client.requests.post",
        return_value=fake_response
    ) as mock_post:
        with pytest.raises(RuntimeError):
            get_embedding(
                "Привет",
                {
                    "max_retries": 0,
                    "initial_delay": 0,
                    "multiplier": 2
                }
            )

    assert mock_post.call_count == 1

def test_retries_exhausted():
    fake_response = Mock()
    fake_response.status_code = 500

    with patch(
        "embedding_client.requests.post",
        return_value=fake_response
    ) as mock_post:
        with pytest.raises(
            RuntimeError,
            match="Retries exhausted"
        ):
            get_embedding(
                "Привет",
                {
                    "max_retries": 3,
                    "initial_delay": 0,
                    "multiplier": 2
                }
            )

    assert mock_post.call_count == 4

