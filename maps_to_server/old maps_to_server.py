from pathlib import Path
import shutil
import re
import hashlib

# Indev version for better handling, at least that's the goal. (The og version will NEVER see the light of day)
# The organization of this is so bad right now, god I hate it so much.

# I love commenting, esepcially so when I add zero context and just type random shit.

def get_file_hash(filepath, algorithm='sha256'):
    """Calculates the hash of a file's content."""
    hasher = hashlib.new(algorithm)
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        return None

def update_list_of_maps_moved(name, status, nav=""): # TODO: Make this suck less, this also applies to all other code :/
    """Appends information of moved map to map list-dir."""
    list_of_maps_moved.append({
        'name': name,
        'status': status,
        'nav_mesh': nav
    })

# Take BSPs and NAVs directly from TF2 maps folder.
map_source = Path(r"C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2/tf/maps")
map_name_format = r"^ctf_open_turbine_"

list_of_maps_moved = [] # List of dicts to store maps moved, and their statuses (Created, Updated, Identical).
                        # Used to be a single array, but decided to add a status logging feature which needed a list of dicts.

# Put them in server maps folder.
server_location = Path(r"D:/SRCDS/tf/maps")
server_cfg_location = Path(r"D:/SRCDS/tf/cfg") # Update MotD and mapcycle, would be unwise to leave them outdated.
server_motd_base = server_cfg_location.joinpath("motd_base.txt") # Bases for motd and motd_text so I only have to append the map names to the end of the file.
server_motd_text_base = server_cfg_location.joinpath("motd_text_base.txt")

# Basic hold because... I can add it ig.
print(f"Settings:\n- Map Source: {map_source}\n- Map File Format: {map_name_format}\n- Server Location: {server_location}")
print("\n\nWill update `motd.txt` and `motd_text.txt` using `motd_base.txt` and `motd_text_base.txt` respectively.\nWill also update 'mapcycle.txt'.")
input("\nPress enter to continue.")

# Updated file transfer and cacher (is cache the right word here?) to handle *both* .bsp and .nav at once instead of two separate files.
# This change is so that `update_list_of_maps_moved` can include the status of the nav of a map much easier. 

    # There's supposed to be something here, I just haven't added it yet :D

# The actual important part of the code. (to be removed/reworked)
for file in map_source.iterdir():
    if file.is_file():
        file_name = file.name
        file_stem = file.stem
        file_suffix = file.suffix
                
        if re.match(map_name_format, file_name):
            constructed_source = map_source.joinpath(file_name) # shutil.copyfile needs full paths as both src and dst, construct them here.
            constructed_destination = server_location.joinpath(file_name)
            
            print(file_suffix)

            map_file_already_exists = constructed_destination.exists() # Check if file already exists.
            map_file_hash_before = get_file_hash(constructed_destination) if map_file_already_exists and file_suffix == ".bsp" else None # Grab hash if the file already exists and is a .bsp.

            shutil.copyfile(constructed_source, constructed_destination) # Copy the files to the server. (duh)
            
            if file_suffix == ".bsp": # Append map+status to list-dir.
                if map_source.joinpath(file_stem + r".nav").exists():
                    print(f"Nav mesh exists for {file_name}")
                    pass

                if not map_file_already_exists:
                    update_list_of_maps_moved(file_stem, "CREATED")
                    continue # Skip to next file, don't waste time generating hash for completely new map file.

                map_file_hash_after = get_file_hash(constructed_destination) # Get new hash.
                if map_file_hash_before == map_file_hash_after:
                    update_list_of_maps_moved(file_stem, "IDENTICAL")
                else:
                    update_list_of_maps_moved(file_stem, "UPDATED")

# Print maps that were moved. (duh)
print("\nMaps that were copied to server:")
for item in list_of_maps_moved:
    print(f" - {item['name']} => {item['status']}{item['nav_mesh']}")

# Update mapcycle
new_mapcycle = server_cfg_location.joinpath("mapcycle.txt")
mapcycle = open(new_mapcycle, "w")
for item in list_of_maps_moved:
    mapcycle.write(item['name'])
mapcycle.close()
print("\n'mapcycle.txt' updated.")

# Update MotD map list
## Generate a list of the maps.
map_names_only = [i['name'] for i in list_of_maps_moved]
map_name_list = "\n - " + "\n - ".join(map_names_only) # Generate a map list. The first `"\n - "` is for the first entry, the `"\n - ".join()` part only gets added for successive entries.

## MotD
new_motd = server_cfg_location.joinpath("motd.txt") # Create MotD
with open(server_motd_base, "r") as file:
    motd_content = file.read() # The base file content.


new_motd_content = re.sub(r"---MAPSPLACEMENTAREA---", map_name_list, motd_content) # Sew map list into content string.

motd = open(new_motd, "w") # Open new MotD.
motd.write(new_motd_content) # Add content string.
motd.close()
print("'motd.txt' updated.")

## MotD Text # More or less just a copy of aboved. It's incase that motd actually has HTML code.
new_motd_text = server_cfg_location.joinpath("motd_text.txt") # Create MotD
with open(server_motd_text_base, "r") as file:
    motd_text_content = file.read() # The base file content.
new_motd_text_content = re.sub(r"---MAPSPLACEMENTAREA---", map_name_list, motd_text_content) # Sew map list into content string.
motd_text = open(new_motd_text, "w") # Open new MotD.
motd_text.write(new_motd_text_content) # Add content string.
motd_text.close()
print("'motd_text.txt' updated.")

# Tell user it's all done, wait for input to close.
input("\nProcess complete, press enter to exit.")

if __name__ == "__main__":
    pass