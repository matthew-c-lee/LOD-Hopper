import pyautogui
from time import sleep
from typing import Iterator
import numpy
from datetime import timedelta
from pynput import keyboard
import threading
import os
import argparse
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
    grid_data_initialize,
    grid_data_to_string,
    grid_data_add_visited,
)

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# Global state
teleportation_paused = True
ctrl_pressed = False

screen_update_queue = Queue()
screen_update_event = Event()


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
    num_hyphens = 100
    shift_amount = 30  # Width for the name padding

    while True:
        # Wait for the screen update event to be triggered
        screen_update_event.wait()
        screen_update_event.clear()

        if not screen_update_queue.empty():
            screen_update: ScreenUpdate = screen_update_queue.get()

        clear_screen()

        if not screen_update:
            print("Loading...")
            continue

        status = "PAUSED" if teleportation_paused else "RUNNING"
        print(bold("Progress") + f'{f"({status})":>{num_hyphens - 8}}')
        print("-" * num_hyphens)

        # Total bar
        bar = create_progress_bar(width=num_hyphens - shift_amount - 2, max=num_coordinates, current_index=screen_update.times_teleported, shift_amount=shift_amount, num_hyphens=num_hyphens)
        print_wrapped(f"Total ({screen_update.time_estimate} left)", bar, shift_amount, num_hyphens)

        print()

        # Ring bar
        bar = create_progress_bar(width=screen_update.total_rings, max=screen_update.total_rings, current_index=screen_update.ring_index, shift_amount=shift_amount, num_hyphens=num_hyphens)
        print_wrapped("Ring", bar, shift_amount, num_hyphens)

        # Side bar
        side_info = screen_update.side_info
        bar = create_progress_bar(width=4, max=4, current_index=screen_update.side_index, shift_amount=shift_amount, num_hyphens=num_hyphens)
        sign = "+" if side_info.direction == Direction.positive else "-"
        print_wrapped(f"Side  ({side_info.name.capitalize()}, Moving {sign}{side_info.dimension_moving_in.name.upper()}/{side_info.clockwise_moving.capitalize()})", bar, shift_amount, num_hyphens)

        # Coordinate bar
        bar = create_progress_bar(
            width=screen_update.coordinates_in_side, max=screen_update.coordinates_in_side, current_index=screen_update.coordinate_index, shift_amount=shift_amount, num_hyphens=num_hyphens
        )
        print_wrapped(f"Coord (x: {screen_update.coordinate.x},  z: {screen_update.coordinate.z})", bar, shift_amount, num_hyphens)

        grid_data_add_visited(
            screen_update.grid_data,
            current_index=screen_update.times_teleported,
        )

        if screen_update.is_visualization_on:
            print()
            print(bold("Visualization"))
            print("-" * num_hyphens)
            print(grid_data_to_string(screen_update.grid_data))
            print()
            print("The visualization can be pretty big. Pause (CTRL+P) and scroll up for more info!")
            print("It can also be turned off with -nov")

        print()
        print(bold("CTRL+P to Pause"))


def create_progress_bar(width: int, max: int, current_index: int, shift_amount: int, num_hyphens: int) -> str:
    progress = current_index / max
    filled_length = int(width * progress)
    bar = '◼' * filled_length + '▭' * (width - filled_length)

    return f"|{bar}|"


def print_wrapped(name: str, bar: str, shift_amount: int, num_hyphens: int) -> None:
    """
    Prints the progress bar, wrapping to the next line if it's too long.
    Wrapped lines will be aligned with the start of the bar.
    The last line will include the ending delimiter '|' if the bar has delimiters.
    """
    # Check if the bar has delimiters like '|'
    has_delimiters = bar.startswith('|') and bar.endswith('|')

    # Extract the bar content without delimiters
    if has_delimiters:
        bar_content = bar[1:-1]
        start_delim = '|'
        end_delim = '|'
    else:
        bar_content = bar
        start_delim = ''
        end_delim = ''

    # Calculate available space for the bar content after the name and delimiters on the first line
    available_width_first_line = num_hyphens - shift_amount - len(start_delim) - len(end_delim)

    # Get the first part of the bar content that fits on the first line
    first_part = bar_content[:available_width_first_line]
    bar_content = bar_content[available_width_first_line:]  # Update bar_content after slicing

    # Determine if there is more bar content after the first line
    is_last_line = not bar_content

    # Add ending delimiter if it's the last line
    end_char = end_delim if is_last_line else ''
    print(f"{name:<{shift_amount}}{start_delim}{first_part}{end_char}")

    # For wrapped lines, align with the start of the bar
    bar_indent = shift_amount + len(start_delim)
    # Calculate available width for wrapped lines
    available_width_wrapped = num_hyphens - bar_indent - len(end_delim)

    # Continue printing wrapped lines
    while bar_content:
        # Get the next segment of the bar content
        chunk_to_print = bar_content[:available_width_wrapped]
        bar_content = bar_content[available_width_wrapped:]  # Update bar_content after slicing

        # Check if this is the last line
        is_last_line = not bar_content

        # Add ending delimiter if it's the last line
        end_char = end_delim if is_last_line else ''

        # Print the bar segment aligned with the bar start
        print(f"{'':<{bar_indent}}{chunk_to_print}{end_char}")


def bold(string):
    return f"\033[1m{string}\033[0m"


def on_press(key):
    global ctrl_pressed
    global teleportation_paused
    if key == keyboard.Key.ctrl_l:
        ctrl_pressed = True

    if ctrl_pressed and hasattr(key, "char") and key.char == "p":
        screen_update_event.set()
        teleportation_paused = not teleportation_paused


def on_release(key):
    global ctrl_pressed

    if key == keyboard.Key.ctrl_l:
        ctrl_pressed = False


def listen_for_key():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def clear_screen():
    return os.system("cls") if os.name == "nt" else os.system("clear")


def get_estimate_string(time_estimate: timedelta) -> str:
    hours, minutes, seconds = (float(num) for num in (str(time_estimate).split(":")))

    return (
        f"{hours + minutes / 60:.1f} {'hours' if hours > 1 else 'hour'}"
        if hours != 0
        else f"{minutes + seconds / 60:.0f} {'minutes' if minutes > 1 else 'minute'}"
        if minutes != 0
        else f"{seconds:.0f} {'seconds' if seconds > 1 else 'second'}"
    )


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
                coordinates=tuple(Coordinate(x=coord, z=current_ring_radius) for coord in coordinate_intervals),
            ),
            west=Side(
                side_info=SideInfo.west,
                coordinates=tuple(Coordinate(x=current_ring_radius, z=coord) for coord in coordinate_intervals)[::-1],
            ),
            south=Side(
                side_info=SideInfo.south,
                coordinates=tuple(Coordinate(x=coord, z=-current_ring_radius) for coord in coordinate_intervals)[::-1],
            ),
            east=Side(
                side_info=SideInfo.east,
                coordinates=tuple(Coordinate(x=-current_ring_radius, z=coord) for coord in coordinate_intervals),
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


def command_line_parsing():
    """Command line arguments"""
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

    return parser.parse_args()


def main():
    args = command_line_parsing()

    desired_radius = Blocks(args.desired_radius)
    radius_done = Blocks(args.exclude)
    seconds_per_teleport = args.seconds_per_tp
    blocks_per_tp = args.blocks_per_tp
    teleportation_height = args.height
    is_visualization_on = not args.no_visualization

    """Set things up"""
    keyboard_listener = threading.Thread(target=listen_for_key, daemon=True)
    keyboard_listener.start()

    clear_screen()
    print("Make sure your world is open with no GUIs up.")
    print('Press "CTRL+P" to start and stop!')

    ring_list = tuple(get_all_teleporation_rings(desired_radius, radius_done, blocks_per_tp))

    coordinates_list = tuple(coordinates for ring in ring_list for side in ring for coordinates in side.coordinates)

    grid_data = grid_data_initialize(coordinates_list, blocks_per_tp)
    num_coordinates = len(coordinates_list)

    screen_thread = threading.Thread(
        target=update_screen,
        args=(num_coordinates,),
        daemon=True,
    )
    screen_thread.start()

    """Timing estimate stuff"""
    total_seconds = num_coordinates * seconds_per_teleport
    original_time_estimate = timedelta(seconds=total_seconds)

    print(f"\nTime to Complete: {original_time_estimate}")

    time_estimate = original_time_estimate

    """Main process loop"""
    times_teleported = 0

    # Triple for loop so that we can track where we are in relation to each part
    # (so we can know which ring we're on, which side we're at, and which coordinate of the side we're at)
    for ring_i, ring in enumerate(ring_list):
        for side_i, side in enumerate(ring):
            for coordinate_i, coordinate in enumerate(side.coordinates):
                # Wait for the chunks to render.
                sleep(seconds_per_teleport)

                time_estimate -= timedelta(seconds=seconds_per_teleport)

                estimate_string = get_estimate_string(time_estimate)

                while teleportation_paused:
                    # If it's paused, we just chill here.
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

                # Send signal to the update_screen thread.
                screen_update_queue.put(screen_update)
                screen_update_event.set()

                teleport(x=coordinate.x, y=teleportation_height, z=coordinate.z)

                times_teleported += 1


if __name__ == "__main__":
    main()
