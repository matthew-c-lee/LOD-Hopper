# LOD Hopper

Utility for loading a wide area in Minecraft via teleporting around in creative mode. 
Created for the purpose of generating "LODs" for the "Distant Horizons" mod on servers, since [Chunky](https://github.com/pop4959/Chunky) is unable to.

![demonstration2](https://github.com/user-attachments/assets/bc0001bb-14c8-4ab8-a7fd-b91f24818d57)

This is likely about to be [completely obselete](https://gitlab.com/jeseibel/distant-horizons/-/issues/19) — not to mention you could just download your server's world and run Chunky on it in singleplayer — but this was a fun project. And if anyone ever needs to load a ton of chunks in vanilla minecraft for some reason, this would certainly come in handy.

### Installation

1. Install the virtual environment with [poetry](https://python-poetry.org/docs/).

    `poetry install --no-dev`

2. Activate the virtual environment.

    `poetry shell`

3. Run with `lod_hopper` in the terminal.

### Basic Usage

- Type in a valid command, like `lod_hopper -r 3000`

- Open up a minecraft world or server. Ensure you are flying in creative mode.

- With the Minecraft window focused with no GUIs up, press `CTRL+P` to begin processing.

### Exclusion

If you have already loaded a region - radius of 1000, for example, then you can specify that region to be excluded.

    lod_hopper -r 3000 --exclude 1000

That will make the mapper only load the chunks from radius 1000 to 3000, excluding them like so:

![image](https://github.com/user-attachments/assets/8486900f-4da6-49ca-b1af-f39e02699218)

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
  - Turn off map visualization, which is enabled by default
