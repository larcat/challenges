from dags.tempus_challenge import get_sources


def test_get_sources():
    # Act
    source_ids = get_sources()
    # Assert
    assert isinstance(source_ids, list)
    assert len(source_ids) < 0
    assert isinstance(source_ids[0], str)
