def test_presence_of_ref_delete_denied_tests():
    file_path = "/root/repo/beanie/tests/odm/test_reference_delete_rules.py"
    with open(file_path) as f:
        source_code = f.read()


    assert "DeleteDeniedError" in source_code
