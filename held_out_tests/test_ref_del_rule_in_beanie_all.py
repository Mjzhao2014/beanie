def test_ref_del_rule_in_beanie_all():
    import beanie

    assert "ReferenceDeleteRules" in beanie.__all__
