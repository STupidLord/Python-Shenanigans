from pathlib import Path
import shutil
import re
import hashlib
import argparse

# Move files from A to B, along with returning a coolio list of what said files were and their status.
# This ain't on the CLI yet because... lazy + it's not complete :<
def copy_map_files(src_dir, dst_dir, /, file_pattern=r".", nav_required=False, file_status=False, motd=r"") -> list[dict]:
    """Docstring soon, probably."""
    src_list_of_maps = get_list_of_maps(src_dir, file_pattern, nav_required)
    list_of_maps = []
    
    # Convert src_dir and dst_dir into paths because it makes us angry if it isn't.
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    # Also make motd_dir in the case it is provided.
    if motd != r"":
        motd_dir = Path(motd) # Doesn't fully work yet, still debating how to integrate this :p

    for dict in src_list_of_maps:
        stem = "" # I don't think I technically need to define all
        name = "" # of these vars as emptry strings, however I
        path = "" # think it makes sense as this means they will
        dst_path = Path() # always end up as empty strings. No
        status = "" # worrying about if a string will accidently
        nav_name = "" # have the wrong value by virtue of being
        nav_path = "" # set previously.
        dst_nav_path = Path()
        nav_status = ""

        for key, value in dict.items():
            if key == "stem":
                stem = value
            elif key == "name":
                name = value
                dst_path = dst_dir.joinpath(value) # Hint: don't fucking try `dst_path = dst_path.joinpath(value)`
                                                   # Guess fucking what? That doesn't work! You know why? You're
                                                   # trying to create a Path() from `value` and an empty `dst_path`
                                                   # 😲. Crazy right??? If you actually fucking use `dst_dir` you
                                                   # can get the expected result, instead of constructing a stupid
                                                   # path that just puts the file in this dir (where it doesn'
                                                   # belong!!!)
            elif key == "path":
                path = Path(value)
            elif key == "nav_name":
                nav_name = value
                dst_nav_path = dst_dir.joinpath(value)
            elif key == "nav_path":
                nav_path = Path(value)

        if file_status and dst_path.exists():
            map_file_hash_old = get_file_hash(dst_path)
        elif file_status:
            status = "CREATED"
        if file_status and dst_nav_path.exists():
            nav_file_hash_old = get_file_hash(dst_nav_path)
        elif file_status:
            nav_status = "CREATED"

        try:
            shutil.copyfile(path, dst_path)
        except FileNotFoundError:
            pass
        try:
            shutil.copyfile(nav_path, dst_nav_path)
        except FileNotFoundError:
            pass
        
        if file_status and status != "CREATED":
            map_file_hash_new = get_file_hash(dst_path)
            if map_file_hash_old == map_file_hash_new:
                status = "IDENTICAL"
            else:
                status = "UPDATED"
        if file_status and nav_status != "CREATED":
            nav_file_hash_new = get_file_hash(dst_nav_path)
            if nav_file_hash_old == nav_file_hash_new:
                nav_status = "IDENTICAL"
            else:
                nav_status = "UPDATED"

        if file_status:
            if dst_nav_path.exists():
                list_of_maps.append({ # Create nice little dict containing this map's properties.
                    'stem': stem,
                    'name': name,
                    'status': status,
                    'nav_name': nav_name,
                    'nav_status': nav_status
                })
            else:
                list_of_maps.append({ # We don't have a .nav though... :(
                    'stem': stem,
                    'name': name,
                    'status': status
                })
        else:
            if dst_nav_path.exists():
                list_of_maps.append({ # We don't care what happened with the files, only their names and the stem.
                    'stem': stem,
                    'name': name,
                    'nav_name': nav_name
                })
            else:
                list_of_maps.append({ # No .nav again? Seriously?
                    'stem': stem,
                    'name': name
                })

    return list_of_maps # Return the map list incase it's needed, I guess?

# Generate a list of dicts of maps and their properties.
def get_list_of_maps(src_dir, /, file_pattern=r".", nav_required=False) -> list[dict]: # Optional pattern definition.
    """
    Return a list of dictionaries of the maps (and their properties) located in the source directory.

    :param src_dir: Source directory to gather files from.
    :type src_dir: str
    :param file_pattern: Regex pattern to match file names to.
    :type file_pattern: str
    :param nav_required: If navigation mesh should be required or not.
    :type nav_required: bool

    <br>

    :returns: List of dictionaries that...

       Contain:
       - ``'stem'``: Stem of the map. (Example: ``ctf_turbine``)
       - ``'name'``: Name of the map. (Example: ``ctf_turbine.bsp``)
       - ``'path'``: File path of the map. (Example: ``.../tf/maps/ctf_turbine.bsp``)

       If a nav mesh exists, will also contain:
       - ``'nav_name'``: Name of the nav mesh. (Example: ``ctf_turbine.nav``)
       - ``'nav_path'``: File path of the nav mesh. (Example: ``.../tf/maps/ctf_turbine.nav``)
    :rtype: list[dict]
    """
    list_of_maps = [] # Create the empty list.

    src_dir = Path(src_dir)

    for file in src_dir.glob(r"*.bsp"): # For file in src_dir that is a .bsp.
        file_path = src_dir.joinpath(file.name)
        nav_mesh, nav_name = get_nav_mesh(src_dir, file.stem)
        if re.match(file_pattern, file.stem) and nav_mesh is not None: # Check that the file matches the pattern and has an accompanying .nav.
            list_of_maps.append({
                'stem': file.stem,
                'name': file.name,
                'path': file_path,
                'nav_name': nav_name,
                'nav_path': nav_mesh
            }) # Append said file to the list and repeat until no more files left.
        elif re.match(file_pattern, file.stem) and not nav_required: # If file doesn't have an accompantying .nav, add only the map file itself.
                                                                     # But don't add files if nav is required!
            list_of_maps.append({
                'stem': file.stem,
                'name': file.name,
                'path': file_path
            })

    return list_of_maps # Return the list.

# Generate a list of nav meshes.
    # Is there even a perpose to having this?
    # I honestly couldn't tell you why I originally
    # added it. So far I see no reasl use case
    # for it because get_list_of_maps() already
    # does both .bsp's and .nav's. My only guess
    # is that there was some plan to handle .nav
    # separately from .bsp (for some reason), but
    # I had gained the smarts to realize how dumb
    # of an idea it was.
def get_list_of_nav_meshes(src_dir, file_pattern=r"."):
    """Populate a list of the nav meshes located in the source directory."""
    list_of_nav_meshes = []
    
    for file in Path(src_dir).glob(r"*.nav"):
        if re.match(file_pattern, file.stem):
            list_of_nav_meshes.append(file.name)

    return list_of_nav_meshes

# Find nav mesh for specific map.
def get_nav_mesh(src_dir, file_stem) -> tuple[Path, str]:
    """Returns path and name of a nav mesh."""
    nav_name = file_stem + r".nav" # Construct nav name.
    nav_mesh = Path(src_dir).joinpath(nav_name) # Construct .nav file path.
    if nav_mesh.exists():
        return nav_mesh, nav_name # Return .nav file path and name if it exists.
                                  # Technically nav_name could be constructed
                                  # in get_list_of_maps(), but defining it here
                                  # is cooler because it means I get to return a
                                  # tuple.
    return None, None # If you can't find a nav mesh... return nothing :D

# File hashing, used for determining if a file was identical or updated.
def get_file_hash(filepath):
    """Return the hash of a file's content."""
    hasher = hashlib.new("sha256")
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError: # Just be smart enough to *not*
                              # parse non-existing files smh.
        return None

# CLI setup and other centralized code stuffs. (Listen, I'm too sleepy for real explanation shit)
def main():
    # Main parser for all your parsing needs.
    parser = argparse.ArgumentParser(description="Quickly move .bsp and .nav files from one location to another.")
    # Subparers for all your subparsing needs.
    subparsers = parser.add_subparsers(dest="function", required=True)
    
    # Individual parsers.
    ## get_list_of_maps()
    list_of_maps_parser = subparsers.add_parser("get_list_of_maps",
                                                help="Returns a list of dicts of the maps (and their properties) in the source dir.")
    list_of_maps_parser.add_argument("-d", "--dir",
                                     type=str,
                                     required=True,
                                     help="Source directory to serach for map files in.")
    list_of_maps_parser.add_argument("-p", "--pattern",
                                     type=str,
                                     required=False,
                                     default=r".",
                                     help="Regex pattern to serach for.")
    list_of_maps_parser.add_argument("-r", "--nav-required",
                                     type=bool,
                                     required=False,
                                     default=False,
                                     help="If nav mesh should be required. Defaults to false.")
    ## get_nav_mesh()
    nav_mesh_parser = subparsers.add_parser("get_nav_mesh", help="Returns path and name of a nav mesh.")
    nav_mesh_parser.add_argument("-d", "--dir",
                                 type=str,
                                 required=True,
                                 help="Source directory to locate nav files in.")
    nav_mesh_parser.add_argument("-f", "--file",
                                 type=str,
                                 required=True,
                                 help="File name to find nav mesh for.")
    
    # Parse the args into the parse. :thumbsup:
    args = parser.parse_args()
    
    # Handle commands.
    if args.function == "get_list_of_maps":
        list_of_maps = get_list_of_maps(args.dir, args.pattern, args.nav_required)
        for item in list_of_maps:
            print(f" - {item['name']} - {item['path']}\n    - {item['nav_name']} - {item['nav_path']}") if "nav_path" in item else print(f" - {item['name']} - {item['path']}")
    elif args.function == "get_nav_mesh":
        nav_mesh, nav_name = get_nav_mesh(args.dir, args.file)
        if nav_mesh is not None:
            print(f"Found a nav mesh named \"{nav_name}\" at \"{nav_mesh}\".")
        else:
            print(f"Could not find a nav mesh named \"{args.file}.nav\" in \"{args.dir}\".")
    

if __name__ == "__main__":
    main()