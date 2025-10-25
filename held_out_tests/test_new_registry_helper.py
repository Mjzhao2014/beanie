def test_registry_helper():
    from beanie.odm.registry import DocsRegistry

    new_methods_found = False

    old_public_methods = ['register', 'get', 'evaluate_fr']

    for method in DocsRegistry.__dict__.keys():
        if not method.startswith('_') and method not in old_public_methods:
            new_methods_found = True

    assert new_methods_found