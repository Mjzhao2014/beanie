import ast

def get_method_body(file_path, class_name, method_name):
    """
    Extracts the body of a method from a Python file using AST.

    Args:
        file_path (str): Path to the Python file.
        class_name (str): Name of the class containing the method.
        method_name (str): Name of the method to extract.

    Returns:
        list: A list of AST nodes representing the method's body, or None if not found.
    """
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for body_node in node.body:
                if (isinstance(body_node, ast.FunctionDef) or isinstance(body_node, ast.AsyncFunctionDef) ) and body_node.name == method_name:
                    return body_node.body
    return None

def test_new_registry_helper_uses_registry_attr():
    from beanie.odm.registry import DocsRegistry

    new_method_use_registry_pvt_attr = False

    old_public_methods = ['register', 'get', 'evaluate_fr']

    for method in DocsRegistry.__dict__.keys():
        if not method.startswith('_') and method not in old_public_methods:

            file_path = '/root/repo/beanie/beanie/odm/registry.py'
            class_name = 'DocsRegistry'
            method_name = method

            method_body = get_method_body(file_path, class_name, method_name)

            function_definition = ""

            if method_body:
                for node in method_body:
                    function_definition += str(ast.unparse(node))

            if "._registry" in function_definition:
                new_method_use_registry_pvt_attr = True
                break

    assert new_method_use_registry_pvt_attr