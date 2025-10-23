from pathlib import Path
import re
import argparse

# Generate a list of maps.
def get_list_of_maps(src_dir, file_pattern=r".", /, nav_required=False): # Optional pattern definition.
    """Populate a list of dictionaries of the maps (and properties) located in the source directory."""
    list_of_maps = [] # Create the empty list.
    
    src_dir = Path(src_dir)

    for file in src_dir.glob(r"*.bsp"): # For file in src_dir that is a .bsp.
        file_path = src_dir.joinpath(file.name)
        nav_mesh, nav_name = get_nav_mesh(src_dir, file.stem)
        if re.match(file_pattern, file.stem) and nav_mesh is not None: # Check that the file matches the pattern and has an accompanying .nav.
            list_of_maps.append({
                'name': file.name,
                'path': file_path,
                'nav_name': nav_name,
                'nav_path': nav_mesh
            }) # Append said file to the list and repeat until no more files left.
        elif re.match(file_pattern, file.stem) and not nav_required: # If file doesn't have an accompantying .nav, add only the map file itself.
                                                                     # But don't add files if nav is required!
            list_of_maps.append({
                'name': file.name,
                'path': file_path
            })

    return list_of_maps # Return the list.

# Generate a list of nav meshes.
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

# CLI setup and other centralized code stuffs. (Listen, I'm too sleepy for real explanation shit)
def main():
    # Main parser for all your parsing needs.
    parser = argparse.ArgumentParser(description="Quickly move .bsp and .nav files from one location to another.")
    # Subparers for all your subparsing needs.
    subparsers = parser.add_subparsers(dest="function", required=True)
    
    # Individual parsers.
    ## get_list_of_maps()
    list_of_maps_parser = subparsers.add_parser("get_list_of_maps",
                                                help="Returns a list of dicts of the maps (and properties) in the source dir.")
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