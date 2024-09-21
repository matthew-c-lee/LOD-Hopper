# Lod Hopper

Utility for loading a wide area in Minecraft via teleporting around in creative mode. 
Created for the purpose of generating "LODs" for the "Distant Horizons" mod on servers, since Chunky can't do this.

### Installation

1. Install the virtual environment with poetry.

    `poetry install --no-dev`

2. Activate the virtual environment.

    `poetry shell`

3. Run with `lod_hopper` in the terminal.

### Usage

After typing in a valid command (ex: `lod_hopper -r 3000`), 

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
