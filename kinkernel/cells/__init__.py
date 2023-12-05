"""
This module initializes the `cells` folder, which includes the definitions of cell-related classes.

The `cells` folder provides the foundational abstract classes and concrete implementations
required for creating and managing cells, which are autonomous agents within the system.

Classes:
    BaseCell (class): Abstract base class for a Cell, defining the required interface and common behavior.
    Cell (class): A concrete implementation of BaseCell, intended to be subclassed for specific cell behaviors.
    ResponseModel (class): A Pydantic model representing the standard response format for a cell's execution.

The `__all__` list in this module specifies the public classes that are available for import
when the package is imported using the `from package import *` syntax.

See Also:
    `kinkernel.cells.base`
    `kinkernel.cells.cell`
"""
from kinkernel.cells.base import BaseCell, ResponseModel
from kinkernel.cells.cell import Cell


__all__ = ["Cell", "BaseCell", "ResponseModel"]
