import pyautogui
from time import sleep
from enum import Enum, auto
from typing import NamedTuple, Iterator, NewType
import numpy
from datetime import timedelta
from pynput import keyboard
import threading
import os
import argparse

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# New type for blocks, representing Minecraft block coordinates
Blocks = NewType("Blocks", int)


class Coordinate(NamedTuple):
    x: Blocks
    y: Blocks
    z: Blocks


class Dimension(Enum):
    x = auto()
    y = auto()
    z = auto()


TELEPORATION_ACTIVE = False


def on_press(key):
    global TELEPORATION_ACTIVE
    if key == keyboard.Key.ctrl_l:
        TELEPORATION_ACTIVE = not TELEPORATION_ACTIVE
        print("Paused Processing.")


def listen_for_key():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


def main(
    desired_radius: Blocks,
    radius_done: Blocks,
    seconds_per_teleport: int,
    blocks_per_tp: int,
    teleportation_height: int,
):
    listener_thread = threading.Thread(target=listen_for_key, daemon=True)
    listener_thread.start()

    print("Make sure your world is open with no GUIs up.")
    print('Press "CTRL" to begin teleporting!')

    rings = tuple(
        get_all_teleporation_rings(
            desired_radius, radius_done, blocks_per_tp, teleportation_height
        )
    )

    coordinates = tuple(
        coordinates for ring in rings for side in ring for coordinates in side
    )

    time_estimate = timedelta(seconds=len(coordinates) * seconds_per_teleport)
    print(f"\nTime Remaining: {time_estimate}")

    for coordinate in coordinates:
        while not TELEPORATION_ACTIVE:
            sleep(1)

        teleport(coordinate)

        time_estimate -= timedelta(seconds=seconds_per_teleport)
        os.system("cls") if os.name == "nt" else os.system("clear")
        print(f"\nTime Estimate: {time_estimate}")

        # Wait for the chunks to render.
        sleep(seconds_per_teleport)


class TeleportationRing(NamedTuple):
    right_bottom_to_top: tuple[Coordinate, ...]
    top_right_to_left: tuple[Coordinate, ...]
    left_top_to_bottom: tuple[Coordinate, ...]
    bottom_left_to_right: tuple[Coordinate, ...]


def get_all_teleporation_rings(
    desired_radius: Blocks,
    radius_done: Blocks,
    blocks_per_tp: int,
    teleportation_height: int,
) -> Iterator[TeleportationRing]:
    current_ring_radius = desired_radius

    while current_ring_radius + blocks_per_tp > radius_done:
        # Negative to positive x
        coordinate_intervals = load_line(
            start_coord=-current_ring_radius,
            end_coord=current_ring_radius,
            teleport_jump_amount=blocks_per_tp,
        )

        yield TeleportationRing(
            right_bottom_to_top=tuple(  # bottom right - goes up
                Coordinate(
                    x=coord, y=teleportation_height, z=current_ring_radius
                )
                for coord in coordinate_intervals
            ),
            top_right_to_left=tuple(  # top right - goes left
                Coordinate(
                    x=current_ring_radius, y=teleportation_height, z=coord
                )
                for coord in coordinate_intervals
            )[::-1],
            left_top_to_bottom=tuple(  # left top - goes down
                Coordinate(
                    x=coord, y=teleportation_height, z=-current_ring_radius
                )
                for coord in coordinate_intervals
            )[::-1],
            bottom_left_to_right=tuple(  # bottom left - goes right
                Coordinate(
                    x=-current_ring_radius, y=teleportation_height, z=coord
                )
                for coord in coordinate_intervals
            ),
        )

        current_ring_radius -= blocks_per_tp


def write_chat_message(message: str):
    pyautogui.press("t")
    sleep(0.1)

    pyautogui.typewrite(message)
    sleep(0.1)

    pyautogui.press("enter")


def teleport(coordinates: Coordinate):
    write_chat_message(
        message=f"/tp {coordinates.x} {coordinates.y} {coordinates.z}"
    )


def load_line(
    start_coord: Blocks,
    end_coord: Blocks,
    teleport_jump_amount: Blocks,
) -> tuple[Blocks, ...]:
    total_distance = abs(end_coord - start_coord)

    num_steps = total_distance // teleport_jump_amount + 1

    return tuple(numpy.linspace(start_coord, end_coord, num_steps))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Script for loading a wide area in Minecraft. 
        Created for the purpose of generating "LODs" for the
        "Distant Horizons" mod on servers.
        """
    )

    parser.add_argument(
        "-r",
        "--desired-radius",
        type=int,
        required=True,
        help="Desired radius to be loaded (required)",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        type=int,
        default=0,
        help="Exclude any inner radius already completed (default: 0)",
    )

    parser.add_argument(
        "-s",
        "--seconds-per-tp",
        type=int,
        default=3,
        help="Seconds to wait per teleport - shorter if you have a faster PC (default: 3)",
    )

    parser.add_argument(
        "-b",
        "--blocks-per-tp",
        type=int,
        default=100,
        help="Radius of blocks loaded per teleport jump (default: 100)",
    )

    parser.add_argument(
        "-y",
        "--height",
        type=int,
        default=180,  # Just below the clouds
        help="Your Y axis coordinate each time you teleport (default: 180)",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Pass all the arguments to the main function
    main(
        desired_radius=Blocks(args.desired_radius),
        radius_done=Blocks(args.exclude),
        seconds_per_teleport=args.seconds_per_tp,
        blocks_per_tp=args.blocks_per_tp,
        teleportation_height=args.height,
    )
