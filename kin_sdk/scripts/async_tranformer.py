"""
This module contains the AsyncTransformer class which is used to transform
"""

import ast
import astor


class AsyncTransformer(ast.NodeTransformer):
    """
    A class to transform methods to async methods.

    Attributes
    ----------
    methods_to_transform : List[str]
        A list of method names to transform to async methods.

    Methods
    -------
    visit_FunctionDef(node: ast.FunctionDef) -> ast.AsyncFunctionDef
        Transforms the method to an async method.
    """

    def __init__(self, methods_to_transform):
        self.methods_to_transform = methods_to_transform

    def visit_FunctionDef(self, node):  # pylint: disable=invalid-name
        """
        Transforms the method to an async method.

        Parameters
        ----------
        node : ast.FunctionDef
            The method to transform.
        """
        if node.name in self.methods_to_transform:
            node = ast.AsyncFunctionDef(
                name=node.name,
                args=node.args,
                body=node.body,
                decorator_list=node.decorator_list,
                returns=node.returns,
                type_comment=node.type_comment,
            )
        return node


def add_async_to_methods(file_methods_dict):
    """
    Adds async to the specified methods in the specified files.

    Parameters
    ----------
    file_methods_dict : Dict[str, List[str]]
        A dictionary where the keys are file paths and the values are lists of
        method names to transform to async methods.
    """
    for file, methods in file_methods_dict.items():
        with open(file, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        transformer = AsyncTransformer(methods)
        transformed_tree = transformer.visit(tree)

        with open(file, "w", encoding="utf-8") as f:
            f.write(astor.to_source(transformed_tree))
