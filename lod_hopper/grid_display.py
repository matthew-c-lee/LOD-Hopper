import numpy as np
from typing import Tuple, Dict
from dataclasses import dataclass
from lod_hopper.types import Coordinate, Blocks
import math

# Constants to represent the states in the grid
EMPTY = 0
LIT = 1
UNLIT = 2

@dataclass
class GridData:
    grid: np.ndarray  # NumPy array for storing grid states
    order: Tuple[Coordinate]  # The order of coordinates for updating
    coord_to_index: Dict[Coordinate, Tuple[int, int]]  # Map from Coordinate to (row, col) in NumPy array

    min_x: Blocks
    max_x: Blocks

    min_z: Blocks
    max_z: Blocks

    # Used for testing
    def __eq__(self, other):
        if not isinstance(other, GridData):
            return False
        
        grids_equal = np.array_equal(self.grid, other.grid)
        
        # Compare other attributes as well
        orders_equal = self.order == other.order
        coord_to_index_equal = self.coord_to_index == other.coord_to_index
        bounds_equal = (
            self.min_x == other.min_x and 
            self.max_x == other.max_x and 
            self.min_z == other.min_z and 
            self.max_z == other.max_z
        )
        
        return grids_equal and orders_equal and coord_to_index_equal and bounds_equal

def get_grid_data(coordinates: Tuple[Coordinate, ...], blocks_per_tp: Blocks) -> GridData:
    min_x = min(coord.x for coord in coordinates)
    max_x = max(coord.x for coord in coordinates)
    min_z = min(coord.z for coord in coordinates)
    max_z = max(coord.z for coord in coordinates)

    # Create the NumPy array initialized to EMPTY (0)
    grid_width = math.ceil((max_x - min_x + 1) / blocks_per_tp)
    grid_height = math.ceil((max_z - min_z + 1) / blocks_per_tp)
    grid = np.full((grid_width, grid_height), EMPTY, dtype=int)

    # Mapping from Coordinate to index in the NumPy array
    coord_to_index = {}

    # Populate the grid and coord_to_index map with UNLIT cells
    for coord in coordinates:
        # Calculate the corresponding position in the grid based on min_x and min_z offsets
        row = math.ceil((coord.z - min_z) / blocks_per_tp)
        col = math.ceil((coord.x - min_x) / blocks_per_tp)
        grid[row, col] = UNLIT  # Mark initial positions as UNLIT
        coord_to_index[coord] = (row, col)  # Store the index in the mapping


    return GridData(
        grid=grid,
        order=coordinates,
        coord_to_index=coord_to_index,
        min_x=min_x,
        max_x=max_x,
        min_z=min_z,
        max_z=max_z,
    )

def update_grid_state(grid_data: GridData, current_index: int) -> None:
    """Updates a single cell in the NumPy array to mark it as LIT based on current_index."""
    if current_index >= len(grid_data.order):
        return  # Prevent out-of-bounds updates

    # Get the coordinate and its corresponding position in the grid
    coord = grid_data.order[current_index]
    row, col = grid_data.coord_to_index[coord]

    # Update the grid at the specified position to LIT
    grid_data.grid[row, col] = LIT

def grid_to_string(grid_data: GridData) -> str:
    """Converts the NumPy array grid to a string for display."""
    return "\n".join(
        "".join(
            "  " if cell == EMPTY else "⬜" if cell == LIT else "⬛"
            for cell in row
        )
        for row in grid_data.grid
    )

