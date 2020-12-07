from dags.tempus_challenge import get_sources, get_headlines


def test_get_sources():
    """
    Integration test.
    """
    # Act
    source_ids = get_sources()
    # Assert
    assert isinstance(source_ids, list)
    assert len(source_ids) > 0
    assert isinstance(source_ids[0], str)


def test_get_headlines():
    """
    Transform test. Basic dimensionality testing.
    """
    # Act
    record_counts = get_headlines(manual_ids=get_sources())
    # Assert
    assert isinstance(record_counts['expected_results'], int)
    assert isinstance(record_counts['actual_results'], int)
    assert record_counts['expected_results'] > 0
    assert record_counts['actual_results'] > 0
    assert record_counts['expected_results'] == record_counts['actual_results']
