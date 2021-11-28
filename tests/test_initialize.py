from unittest import mock

import pytest
from elasticsearch.exceptions import ConnectionError

from gumby import initialize_indexes_by_model


def test_initialize_indexes_by_model():
    # Control the input so that we can control the output
    mock_model = mock.MagicMock()
    models = [mock_model]

    stub_es_client = object()

    # Target
    initialize_indexes_by_model(models, using=stub_es_client)

    mock_model.init.assert_called_with(using=stub_es_client)


def test_initialize_indexes_by_model__with_connection_error():
    # Control the input so that we can control the output
    mock_model = mock.MagicMock()
    #: create a ConnectionError senario
    mock_model.init.side_effect = ConnectionError
    models = [mock_model]

    stub_es_client = object()

    # Target
    with pytest.raises(ConnectionError):
        initialize_indexes_by_model(models, using=stub_es_client)


def test_initialize_indexes_by_model__and_fail_gracefully():
    # Control the input so that we can control the output
    mock_model = mock.MagicMock()
    #: create a ConnectionError senario
    mock_model.init.side_effect = ConnectionError
    models = [mock_model]

    stub_es_client = object()

    # Target
    with pytest.warns(RuntimeWarning, match=r'connection error while initializing .*$'):
        initialize_indexes_by_model(models, using=stub_es_client, fail_gracefully=True)

    mock_model.init.assert_called_with(using=stub_es_client)
