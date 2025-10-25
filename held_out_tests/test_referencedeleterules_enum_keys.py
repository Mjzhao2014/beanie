def test_referencedeleterules_enum_keys():
    from beanie.odm.fields import ReferenceDeleteRules

    keys = list(ReferenceDeleteRules.__members__.keys())

    expected_set = {"CASCADE", "SET_NULL", "DENY", "DO_NOTHING", "PULL_FROM_LIST"}
    assert set(keys) == expected_set
