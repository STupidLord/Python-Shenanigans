from pathlib import Path
import shutil
import re
import hashlib
import argparse

# MapItem object simply for the fact that I want to make my code a bit
# better and have an overall eaiser workflow compared to what I was
# doing before. Turns out that using a list of dictionsaries is a tad
# annoying to do, so this is the solution.
class MapItem:
    __slots__ = ("stem", "name", "path", "status",
                 "nav_name", "nav_path", "nav_status")

    def __init__(self, stem, name, path: Path, /, nav_name=None,
                 nav_path: Path=None, status=None, nav_status=None):
        self.stem = stem
        self.name = name
        self.path = path
        self.status = status
        self.nav_name = nav_name
        self.nav_path = nav_path
        self.nav_status = nav_status

# Move files from A to B, along with returning a coolio list of what
# said files were and their status.
# This ain't on the CLI yet because... lazy + it's not complete :<
def copy_map_files(
        src_dir, dst_dir, /, file_pattern=r".", nav_required=False,
        file_status=False, motd="") -> list[MapItem]:
    """Copies map files from source directory to destination directory.

    Args:
        src_dir (str): Source directory to gather files from.
        dst_dir (str): Destination directory to copy files to.
        file_pattern (regexp, optional): Regex pattern to match file
            names to. Defaultsto ".", which matches every file.
        nav_required (bool, optional): If navigation mesh should be
            required or not. Defaults to False.
        file_status (bool, optional): If the status of copied map files
            should be stored. (CREATED, UPDATED, IDENTICAL) Defaults to
            False.
        motd (str, optional): Updates the `motd.txt` and `motd_text.txt`
            for a server, inserting text via a replace string in a base
            file. `motd_base.txt` and `motd_text_base.txt`. Also
            generates a new `mapcycle.txt`. Expects path string similar
            to **src_dir** or **dst_dir**.

    Returns:
        list[MapItem]: A list of :class:MapItems that each contain
            information relating to a specific `.bsp` file, including
            it's `.nav` if it has one.
    """
    list_of_maps = get_list_of_maps(src_dir, file_pattern, nav_required)
    
    # Convert src_dir and dst_dir into paths
    # because it makes us angry if it isn't.
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    # Make sure file paths actually exist smh.
    if not src_dir.exists():
        raise FileNotFoundError(
            f"Source directory: '{src_dir} is not "
            f"a valid file path, path must fully exist."
        )
    if not dst_dir.exists():
        raise FileNotFoundError(
            f"Destination directory: '{dst_dir}' is not "
            f"a valid file path, path must fully exist."
            )

    # Also make motd_dir in the case it is provided.
    if motd != r"":
        # Doesn't work yet, still debating how to integrate this :p
        motd_dir = Path(motd)

    for item in list_of_maps:
        dst_path = dst_dir.joinpath(item.name)
        if file_status and dst_path.exists():
            map_file_hash_old = get_file_hash(dst_path)
        elif file_status:
            item.status = "CREATED"

        shutil.copyfile(item.path, dst_path)

        if file_status and item.status is None:
            map_file_hash_new = get_file_hash(dst_path)
            if map_file_hash_old == map_file_hash_new:
                item.status = "IDENTICAL"
            else:
                item.status = "UPDATED"

        # Stop throwing errors pls
        if item.nav_path is not None:
            dst_nav_path = dst_dir.joinpath(item.nav_name)
            if file_status and dst_nav_path.exists():
                nav_file_hash_old = get_file_hash(dst_nav_path)
            elif file_status:
                item.nav_status = "CREATED"

            shutil.copyfile(item.nav_path, dst_nav_path)

            if file_status and item.nav_status is None:
                nav_file_hash_new = get_file_hash(dst_nav_path)
                if nav_file_hash_old == nav_file_hash_new:
                    item.nav_status = "IDENTICAL"
                else:
                    item.nav_status = "UPDATED"

    return list_of_maps

# Generate a list of MapItem objects and their properties.
    # Docstring to be reformatted similar to the
    # copy_map_files() one soon.
def get_list_of_maps(
        src_dir, /, file_pattern=r".", nav_required=False
    ) -> list[MapItem]:
    """
    Return a list of 'MapItem' objects containing info about the maps
    (and their properties) located in the source directory.

    :param src_dir: Source directory to gather files from.
    :type src_dir: str
    :param file_pattern: Regex pattern to match file names to. Defaults
    to ".", which matches every file.
    :type file_pattern: str
    :param nav_required: If navigation mesh should be required or not.
    Defaults to False.
    :type nav_required: bool

    <br>

    :returns: List of MapItem objects
    :rtype: list[MapItem]
    """
    list_of_maps = [] # Create the empty list.

    src_dir = Path(src_dir)

    # For file in src_dir that is a .bsp.
    for file in src_dir.glob(r"*.bsp"):
        file_path = src_dir.joinpath(file.name)
        nav_mesh, nav_name = get_nav_mesh(src_dir, file.stem)
        if re.match(file_pattern, file.stem) and nav_mesh is not None:
            # Check that the file matches the pattern and has an
            # accompanying .nav.
            list_of_maps.append(
                MapItem(file.stem, file.name, file_path, nav_name, nav_mesh)
            )
        elif re.match(file_pattern, file.stem) and not nav_required: 
            # If file doesn't have an accompantying .nav, add only the
            # map file itself. But don't add files if nav is required!
            list_of_maps.append(MapItem(file.stem, file.name, file_path))

    return list_of_maps # Return the list.

def read_list_of_maps(list_of_maps):
    for item in list_of_maps:
        if item.status is not None and item.nav_path is not None:
            print(
                f"{item.stem}:\n - {item.path} => ({item.status})"
                f"\n - {item.nav_path} => ({item.nav_status})"
            )
        elif item.status is not None:
            print(f"{item.stem}:\n - {item.path} ({item.status})")
        elif item.nav_path is not None:
            print(f"{item.stem}:\n - {item.path}\n - {item.nav_path}")
        else:
            print(f"{item.stem}:\n - {item.path}")

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

# CLI setup and other centralized code stuffs.
# (Listen, I'm too sleepy for real explanation shit)
def main():
    # Main parser for all your parsing needs.
    parser = argparse.ArgumentParser(
        description="Quickly move .bsp and .nav files from one location to another."
        )
    # Subparers for all your subparsing needs.
    subparsers = parser.add_subparsers(dest="function", required=True)
    
    # Individual parsers.
    ## get_list_of_maps()
    list_of_maps_parser = subparsers.add_parser(
        "get_list_of_maps",
        help="Returns a list of dicts of the maps (and their properties) in the source dir.",
        )
    list_of_maps_parser.add_argument(
        "-d",
        "--dir",
        type=str,
        required=True,
        help="Source directory to serach for map files in.",
        )
    list_of_maps_parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        required=False,
        default=r".",
        help="Regex pattern to serach for.",
        )
    list_of_maps_parser.add_argument(
        "-r",
        "--nav-required",
        type=bool,
        required=False,
        default=False,
        help="If nav mesh should be required. Defaults to false.",
        )
    ## get_nav_mesh()
    nav_mesh_parser = subparsers.add_parser(
        "get_nav_mesh",
        help="Returns path and name of a nav mesh.",
        )
    nav_mesh_parser.add_argument(
        "-d",
        "--dir",
        type=str,
        required=True,
        help="Source directory to locate nav files in.",
        )
    nav_mesh_parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="File name to find nav mesh for.",
        )
    
    # Parse the args into the parse. :thumbsup:
    args = parser.parse_args()
    
    # Handle commands.
    if args.function == "get_list_of_maps":
        list_of_maps = get_list_of_maps(args.dir, args.pattern, args.nav_required)

        read_list_of_maps(list_of_maps)
    elif args.function == "get_nav_mesh":
        nav_mesh, nav_name = get_nav_mesh(args.dir, args.file)
        if nav_mesh is not None:
            print(
                f"Found a nav mesh named '{nav_name}' at '{nav_mesh}'."
                )
        else:
            print(
                f"Could not find a nav mesh named '{args.file}.nav' in '{args.dir}'."
                )

if __name__ == "__main__":
    main()