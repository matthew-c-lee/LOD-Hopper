Script for loading a wide area in Minecraft via teleporting around in creative mode. 
Created for the purpose of generating "LODs" for the "Distant Horizons" mod on servers, since Chunky can't do this.

options:
  -h, --help            show this help message and exit
  -r DESIRED_RADIUS, --desired-radius DESIRED_RADIUS
                        Desired radius to be loaded (required)
  -e EXCLUDE, --exclude EXCLUDE
                        Exclude any inner radius already completed (default: 0)
  -s SECONDS_PER_TP, --seconds-per-tp SECONDS_PER_TP
                        Seconds to wait per teleport - shorter if you have a faster PC (default: 3)
  -b BLOCKS_PER_TP, --blocks-per-tp BLOCKS_PER_TP
                        Radius of blocks loaded per teleport jump (default: 100)
  -y HEIGHT, --height HEIGHT
                        Your Y axis coordinate each time you teleport (default: 180)