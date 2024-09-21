from lod_hopper.grid_display import (
    get_grid_data,
    GridData,
    update_grid_state,
    grid_to_string,
)
from lod_hopper.schemas import Coordinate
import pytest
import numpy as np
from lod_hopper.lod_hopper import get_all_teleporation_rings

@pytest.fixture()
def mock_grid_data():
    return GridData(
        grid=np.array(
            [
                [2, 2, 2, 2, 2],
                [2, 2, 2, 2, 2],
                [2, 2, 0, 2, 2],
                [2, 0, 2, 2, 2],
                [2, 2, 2, 2, 2],
            ]
        ),
        order=(
            Coordinate(x=10, z=10),
            Coordinate(x=10, z=11),
            Coordinate(x=10, z=12),
            Coordinate(x=10, z=13),
            Coordinate(x=10, z=14),
            Coordinate(x=11, z=10),
            Coordinate(x=11, z=11),
            Coordinate(x=11, z=12),
            Coordinate(x=11, z=14),
            Coordinate(x=12, z=10),
            Coordinate(x=12, z=11),
            Coordinate(x=12, z=13),
            Coordinate(x=12, z=14),
            Coordinate(x=13, z=10),
            Coordinate(x=13, z=11),
            Coordinate(x=13, z=12),
            Coordinate(x=13, z=13),
            Coordinate(x=13, z=14),
            Coordinate(x=14, z=10),
            Coordinate(x=14, z=11),
            Coordinate(x=14, z=12),
            Coordinate(x=14, z=13),
            Coordinate(x=14, z=14),
        ),
        coord_to_index={
            Coordinate(x=10, z=10): (0, 0),
            Coordinate(x=10, z=11): (1, 0),
            Coordinate(x=10, z=12): (2, 0),
            Coordinate(x=10, z=13): (3, 0),
            Coordinate(x=10, z=14): (4, 0),
            Coordinate(x=11, z=10): (0, 1),
            Coordinate(x=11, z=11): (1, 1),
            Coordinate(x=11, z=12): (2, 1),
            Coordinate(x=11, z=14): (4, 1),
            Coordinate(x=12, z=10): (0, 2),
            Coordinate(x=12, z=11): (1, 2),
            Coordinate(x=12, z=13): (3, 2),
            Coordinate(x=12, z=14): (4, 2),
            Coordinate(x=13, z=10): (0, 3),
            Coordinate(x=13, z=11): (1, 3),
            Coordinate(x=13, z=12): (2, 3),
            Coordinate(x=13, z=13): (3, 3),
            Coordinate(x=13, z=14): (4, 3),
            Coordinate(x=14, z=10): (0, 4),
            Coordinate(x=14, z=11): (1, 4),
            Coordinate(x=14, z=12): (2, 4),
            Coordinate(x=14, z=13): (3, 4),
            Coordinate(x=14, z=14): (4, 4),
        },
        min_x=10,
        max_x=14,
        min_z=10,
        max_z=14,
    )


# def test_get_grid_data(mock_grid_data):
#     coordinates = tuple(
#         Coordinate(x=x, z=z)
#         for x in range(10, 15)
#         for z in range(10, 15)
#         if not (x == 12 and z == 12) and not (x == 11 and z == 13)
#     )

#     grid_data = get_grid_data(coordinates)

#     assert grid_data == mock_grid_data


def test_grid_to_string(mock_grid_data):
    for i in range(5):
        update_grid_state(mock_grid_data, i)
    
    display_grid = grid_to_string(mock_grid_data)

    assert display_grid == '\n'.join([
        '⬜⬛⬛⬛⬛',
        '⬜⬛⬛⬛⬛',
        '⬜⬛  ⬛⬛',
        '⬜  ⬛⬛⬛',
        '⬜⬛⬛⬛⬛'
    ])


# def test_idk():
#     ring_list = tuple(
#         get_all_teleporation_rings(
#             desired_radius=15,
#             radius_done=12,
#             blocks_per_tp=3
#         )
#     )

#     coordinates_list = tuple(
#         coordinates
#         for ring in ring_list
#         for side in ring
#         for coordinates in side.coordinates
#     )
#     grid_data = get_grid_data(coordinates_list, blocks_per_tp=3)

#     print(grid_to_string(grid_data))

#     assert False
