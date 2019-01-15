#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for seeding the safelist.
"""
import os

import pytest
from mock import DEFAULT, MagicMock, patch

from code_annotations.find_django import DjangoSearch
from tests.helpers import DEFAULT_FAKE_SAFELIST_PATH, EXIT_CODE_FAILURE, EXIT_CODE_SUCCESS, call_script_isolated


@patch.multiple(
    'code_annotations.find_django.DjangoSearch',
    get_models_requiring_annotations=DEFAULT,
)
@pytest.mark.parametrize("local_model_ids,non_local_model_ids", [
    (
        [
            MagicMock(_meta=MagicMock(app_label='fake_app_1', object_name='FakeModelA')),
            MagicMock(_meta=MagicMock(app_label='fake_app_2', object_name='FakeModelB')),
        ],
        [
            MagicMock(_meta=MagicMock(app_label='fake_app_3', object_name='FakeModelC')),
            MagicMock(_meta=MagicMock(app_label='fake_app_4', object_name='FakeModelD')),
        ],
    ),
    (
        [
            MagicMock(_meta=MagicMock(app_label='fake_app_1', object_name='FakeModelA')),
            MagicMock(_meta=MagicMock(app_label='fake_app_2', object_name='FakeModelB')),
        ],
        [],  # No non-local models to add to the safelist.
    ),
])
def test_seeding_safelist(local_model_ids, non_local_model_ids, **kwargs):
    """
    Test the success case for seeding the safelist.
    """
    mock_get_models_requiring_annotations = kwargs['get_models_requiring_annotations']
    mock_get_models_requiring_annotations.return_value = (
        local_model_ids,
        non_local_model_ids,
    )

    def test_safelist_callback():
        assert os.path.exists(DEFAULT_FAKE_SAFELIST_PATH)
        with open(DEFAULT_FAKE_SAFELIST_PATH, 'r') as fake_safelist_file:
            fake_safelist = fake_safelist_file.read()
        for model in non_local_model_ids:
            assert DjangoSearch.get_model_id(model) in fake_safelist
        for model in local_model_ids:
            assert DjangoSearch.get_model_id(model) not in fake_safelist

    result = call_script_isolated(
        ['django_find_annotations', '--config_file', 'test_config.yml', '--seed_safelist'],
        test_filesystem_cb=test_safelist_callback,
        fake_safelist_data=None
    )
    assert result.exit_code == EXIT_CODE_SUCCESS
    assert 'Successfully created safelist file' in result.output


@patch.multiple(
    'code_annotations.find_django.DjangoSearch',
    get_models_requiring_annotations=DEFAULT,
)
def test_safelist_exists(**kwargs):
    """
    Test the success case for seeding the safelist.
    """
    mock_get_models_requiring_annotations = kwargs['get_models_requiring_annotations']
    mock_get_models_requiring_annotations.return_value = ([], [])

    result = call_script_isolated(
        ['django_find_annotations', '--config_file', 'test_config.yml', '--seed_safelist']
    )
    assert result.exit_code == EXIT_CODE_FAILURE
    assert 'already exists, not overwriting.' in result.output
