# Lod Hopper

Utility for loading a wide area in Minecraft via teleporting around in creative mode. 
Created for the purpose of generating "LODs" for the "Distant Horizons" mod on servers, since Chunky isn't able to.

### Installation

1. Install the virtual environment with poetry.

    `poetry install --no-dev`

2. Activate the virtual environment.

    `poetry shell`

3. Run with `lod_hopper` in the terminal.

### Usage

- Type in a valid command, like `lod_hopper -r 3000`

- Open up a minecraft world or server. Ensure you are flying in creative mode.

- With the Minecraft window focused with no GUIs up, press `CTRL+P` to begin processing.

### Command Options

- **`--desired-radius` or `-r`**
  - Desired radius to be loaded (**required**)

- **`--exclude` or `-e`**
  - Exclude any inner radius already completed (default: 0)

- **`--seconds-per-tp` or `-s`**
  - Seconds to wait per teleport (default: 3)
  - Modify this depending on how long it takes to render chunks

- **`--blocks-per-tp` or `-b`**
  - Radius of blocks loaded per teleport jump (default: 100)

- **`--height` or `-y`**
  - Y-axis coordinate each time you teleport (default: 180)

- **`--no-visualization` or `-nov`**
  - Will turn off map visualization, which is enabled by default
