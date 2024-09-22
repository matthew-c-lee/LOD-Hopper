import pyautogui
from time import sleep
from typing import Iterator
import numpy
from datetime import timedelta
from pynput import keyboard
import threading
import os
import argparse
from progress.bar import Bar
from threading import Event
from queue import Queue
from dataclasses import dataclass
from lod_hopper.schemas import (
    Coordinate,
    SideInfo,
    Blocks,
    Direction,
    Side,
    TeleporationRing,
)
from lod_hopper.grid_display import (
    GridData,
    get_grid_data,
    grid_to_string,
    update_grid_state,
)

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# New type for blocks, representing Minecraft block coordinates

screen_update_queue = Queue()
screen_update_event = Event()

teleportation_active = False


@dataclass(frozen=True)
class ScreenUpdate:
    time_estimate: timedelta
    estimate_string: str
    ring_index: int
    side_index: int
    coordinate_index: int

    total_rings: int
    coordinates_in_side: int
    coordinate: Coordinate

    side_info: SideInfo
    grid_data: GridData

    times_teleported: int
    is_visualization_on: bool


def update_screen(num_coordinates: int):
    screen_update = None
    shift_amount = 5
    total_progress = Bar(
        f"{'Total':<{shift_amount}}",
        fill="◼",
        empty_fill="▭",
        suffix="",
        width=20,
        max=num_coordinates,
    )

    while True:
        # Wait for the screen update event to be triggered
        screen_update_event.wait()
        screen_update_event.clear()

        if not screen_update_queue.empty():
            screen_update: ScreenUpdate = screen_update_queue.get()

        os.system("cls") if os.name == "nt" else os.system("clear")

        print("\033[1mLOD Hopper - CTRL+P to Pause\033[0m")

        if not screen_update:
            print("Loading...")
            continue


        status = "RUNNING" if teleportation_active else "PAUSED"
        print(f"\n\033[1mProgress\033[0m{f'({status})':>20}")
        print("-" * 28)
        print(
            f"Time Remaining: {screen_update.time_estimate} ({screen_update.estimate_string})"
        )
        total_progress.goto(screen_update.times_teleported + 1)

        print("\n")

        ring_progress = Bar(
            f"{'Ring':<{shift_amount}}",
            fill="◼",
            empty_fill="▭",
            suffix="",
            width=screen_update.total_rings,
            max=screen_update.total_rings,
        )
        ring_progress.goto(screen_update.ring_index + 1)
        ring_progress.finish()

        side_progress = Bar(
            f"{'Side':<{shift_amount}}",
            fill="◼",
            empty_fill="▭",
            suffix="",
            width=4,
            max=4,
        )
        side_progress.goto(screen_update.side_index + 1)
        side_progress.finish()

        coordinates_progress = Bar(
            f"{'Coord':<{shift_amount}}",
            fill="◼",
            empty_fill="▭",
            suffix="",
            width=screen_update.coordinates_in_side,
            max=screen_update.coordinates_in_side,
        )
        coordinates_progress.goto(screen_update.coordinate_index + 1)
        coordinates_progress.finish()

        print("\n\033[1mLocation\033[0m")
        print("-" * 28)

        print(
            f"Teleporting to (x: {screen_update.coordinate.x}, z: {screen_update.coordinate.z})"
        )

        side_info = screen_update.side_info

        sign = "+" if side_info.direction == Direction.positive else "-"

        print(
            f"Side: {side_info.name.capitalize()} | Direction: "
            f"{side_info.clockwise_moving.capitalize()} ({sign}{side_info.dimension_moving_in.name})"
        )

        update_grid_state(
            screen_update.grid_data,
            current_index=screen_update.times_teleported,
        )

        if screen_update.is_visualization_on:
            print("\n\033[1mVisualization\033[0m")
            print("-" * 28)
            print(grid_to_string(screen_update.grid_data))

            print("\nThe visualization can be pretty big. Pause (CTRL+P) and scroll up for more info!")
            print("It can also be turned off with -nov")



ctrl_pressed = False

def on_press(key):
    global ctrl_pressed
    global teleportation_active
    if key == keyboard.Key.ctrl_l:
        ctrl_pressed = True

    if ctrl_pressed and hasattr(key, "char") and key.char == "p":
        screen_update_event.set()
        teleportation_active = not teleportation_active


def on_release(key):
    global ctrl_pressed

    if key == keyboard.Key.ctrl_l:
        ctrl_pressed = False


def listen_for_key():
    with keyboard.Listener(
        on_press=on_press, on_release=on_release
    ) as listener:
        listener.join()


def main():
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

    parser.add_argument(
        "-nov",
        "--no-visualization",
        action="store_true",
        help="Will turn off map visualization, which is enabled by default.",
    )

    args = parser.parse_args()

    desired_radius = Blocks(args.desired_radius)
    radius_done = Blocks(args.exclude)
    seconds_per_teleport = args.seconds_per_tp
    blocks_per_tp = args.blocks_per_tp
    teleportation_height = args.height
    is_visualization_on = not args.no_visualization

    listener_thread = threading.Thread(target=listen_for_key, daemon=True)
    listener_thread.start()

    os.system("cls") if os.name == "nt" else os.system("clear")
    print("Make sure your world is open with no GUIs up.")
    print('Press "CTRL+P" to start and stop!')

    ring_list = tuple(
        get_all_teleporation_rings(desired_radius, radius_done, blocks_per_tp)
    )

    coordinates_list = tuple(
        coordinates
        for ring in ring_list
        for side in ring
        for coordinates in side.coordinates
    )

    grid_data = get_grid_data(coordinates_list, blocks_per_tp)

    num_coordinates = len(coordinates_list)

    total_seconds = num_coordinates * seconds_per_teleport
    original_time_estimate = timedelta(seconds=total_seconds)

    print(f"\nTime to Complete: {original_time_estimate}")

    time_estimate = original_time_estimate

    screen_thread = threading.Thread(
        target=update_screen,
        args=(num_coordinates,),
        daemon=True,
    )
    screen_thread.start()

    times_teleported = 0

    for ring_i, ring in enumerate(ring_list):
        for side_i, side in enumerate(ring):
            for coordinate_i, coordinate in enumerate(side.coordinates):
                # Wait for the chunks to render.
                sleep(seconds_per_teleport)

                time_estimate -= timedelta(seconds=seconds_per_teleport)

                hours, minutes, seconds = (
                    float(num) for num in (str(time_estimate).split(":"))
                )
                estimate_string = (
                    f"{hours + minutes / 60:.1f} hours"
                    if hours != 0
                    else f"{minutes + seconds / 60:.0f} minutes"
                    if minutes != 0
                    else f"{seconds:.0f} seconds left"
                )

                while not teleportation_active:
                    sleep(1)

                screen_update = ScreenUpdate(
                    time_estimate=time_estimate,
                    estimate_string=estimate_string,
                    ring_index=ring_i,
                    side_index=side_i,
                    coordinate_index=coordinate_i,
                    total_rings=len(ring_list),
                    coordinates_in_side=len(side.coordinates),
                    coordinate=coordinate,
                    side_info=side.side_info,
                    grid_data=grid_data,
                    times_teleported=times_teleported,
                    is_visualization_on=is_visualization_on,
                )
                times_teleported += 1

                screen_update_queue.put(screen_update)
                screen_update_event.set()

                teleport(x=coordinate.x, y=teleportation_height, z=coordinate.z)


def get_all_teleporation_rings(
    desired_radius: Blocks,
    radius_done: Blocks,
    blocks_per_tp: int,
) -> Iterator[TeleporationRing]:
    current_ring_radius = desired_radius

    while current_ring_radius + blocks_per_tp > radius_done:
        # Negative to positive x
        coordinate_intervals = load_line(
            start_coord=-current_ring_radius,
            end_coord=current_ring_radius,
            teleport_jump_amount=blocks_per_tp,
        )

        yield TeleporationRing(
            north=Side(
                side_info=SideInfo.north,
                coordinates=tuple(
                    Coordinate(x=coord, z=current_ring_radius)
                    for coord in coordinate_intervals
                ),
            ),
            west=Side(
                side_info=SideInfo.west,
                coordinates=tuple(
                    Coordinate(x=current_ring_radius, z=coord)
                    for coord in coordinate_intervals
                )[::-1],
            ),
            south=Side(
                side_info=SideInfo.south,
                coordinates=tuple(
                    Coordinate(x=coord, z=-current_ring_radius)
                    for coord in coordinate_intervals
                )[::-1],
            ),
            east=Side(
                side_info=SideInfo.east,
                coordinates=tuple(
                    Coordinate(x=-current_ring_radius, z=coord)
                    for coord in coordinate_intervals
                ),
            ),
        )

        current_ring_radius -= blocks_per_tp


def write_chat_message(message: str):
    pyautogui.press("t")
    sleep(0.1)

    pyautogui.typewrite(message)
    sleep(0.1)

    pyautogui.press("enter")


def teleport(x: Blocks, y: Blocks, z: Blocks):
    write_chat_message(message=f"/tp {x} {y} {z}")


def load_line(
    start_coord: Blocks,
    end_coord: Blocks,
    teleport_jump_amount: Blocks,
) -> tuple[Blocks, ...]:
    total_distance = abs(end_coord - start_coord)

    num_steps = total_distance // teleport_jump_amount + 1

    coordinate_values = numpy.linspace(start_coord, end_coord, num_steps)

    return tuple(map(int, coordinate_values))


if __name__ == "__main__":
    main()
