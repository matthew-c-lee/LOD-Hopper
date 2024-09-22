import numpy as np
from typing import Tuple, Dict
from dataclasses import dataclass
from lod_hopper.schemas import Coordinate, Blocks
from typing import Iterator
import math

# Constants to represent the states in the grid
EXCLUDED = 0
VISITED = 1
UNVISITED = 2


@dataclass
class GridData:
    grid: np.ndarray
    order: Tuple[Coordinate, ...]
    coord_to_index: Dict[Coordinate, Tuple[int, int]]

    # Used for testing
    def __eq__(self, other):
        if not isinstance(other, GridData):
            return False

        # Compare the grid using np.array_equal, and other attributes directly
        return all([
            np.array_equal(self.grid, other.grid),
            self.order == other.order,
            self.coord_to_index == other.coord_to_index,
        ])

@dataclass
class Span:
    min: Blocks
    max: Blocks

def grid_data_initialize(coordinates: Tuple[Coordinate, ...], blocks_per_tp: Blocks) -> GridData:
    x_span = Span(min(coord.x for coord in coordinates), max(coord.x for coord in coordinates))
    z_span = Span(min(coord.z for coord in coordinates), max(coord.z for coord in coordinates))

    # Calculate grid dimensions
    grid_width = math.ceil((x_span.max - x_span.min + 1) / blocks_per_tp)
    grid_height = math.ceil((z_span.max - z_span.min + 1) / blocks_per_tp)

    # Initialize grid as EMPTY
    grid = np.full((grid_height, grid_width), EXCLUDED, dtype=int)

    coord_to_index = {}

    for coord in coordinates:
        col = (x_span.max - coord.x) // blocks_per_tp
        row = (z_span.max - coord.z) // blocks_per_tp

        grid[row, col] = UNVISITED
        coord_to_index[coord] = (row, col)

    return GridData(
        grid=grid,
        order=coordinates,
        coord_to_index=coord_to_index,
    )


def grid_data_add_visited(grid_data: GridData, current_index: int) -> None:
    """Updates a single cell in the to mark it as LIT based on current_index."""
    if current_index >= len(grid_data.order):
        return  # Prevent out-of-bounds updates

    coord = grid_data.order[current_index]
    row, col = grid_data.coord_to_index[coord]

    grid_data.grid[row, col] = VISITED


ascii_map = {
    EXCLUDED: "  ", 
    VISITED: "⬜", 
    UNVISITED: "⬛"
}


def grid_data_to_string(grid_data: GridData) -> str:
    """Converts the NumPy array grid to a string for display."""
    string_rows: Iterator[str] = ("".join(ascii_map[cell] for cell in row) for row in grid_data.grid)

    return "\n".join(string_rows)
