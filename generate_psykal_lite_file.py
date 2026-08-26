#!/usr/bin/env python
"""
Script to go through the current repositories to check for PSyKAl-lite
code and record it. The script will save the data it scraped to either
a .txt and/or .json file. These can all be customised.
"""

import os
import json

# Set extensions of files to be checked for invoke calls
PARSE_EXT = tuple([".x90", ".F90", ".f90", ".X90"])
# Home directory and code directory
CODE_PATH = os.path.dirname(os.path.realpath(__file__))
# Input directory and path
LFRIC_APPS_DIR = ""

# Option to exclude certain paths
EXCLUDE_DIR = "/working/"

# Output directory and path
INPUT_APPS_PATH = os.path.join(CODE_PATH, LFRIC_APPS_DIR)


def get_source_files(trunk_path: str) -> list:
    """
    Function to return a list of addresses to all source files within
    a directory
    """
    # First find directories which contains source code
    # The first of 3-tuple members is directory,
    # the second contains list of sub-directories,
    # and the third list of files within them
    sourcedirs = []
    try:
        sourcedirs += [dirs for dirs in os.walk(trunk_path)]
    except FileNotFoundError:
        print(f'Could not find the path for the input path: {trunk_path}')
        return None
    # Now create list of full paths of source files
    source_files = []
    for root, dirs, files in sourcedirs:
        for filename in files:
            if filename.endswith(PARSE_EXT) and EXCLUDE_DIR not in root:
                source_files.append(os.path.join(root, filename))

    # print(source_files)
    return source_files


def find_psykal_subroutines(psykal_files: list,
                            psykal_invokes: dict = None) -> dict:
    """
    Searches through a list of PSyKAl-lite routines and
    identifies the specific PSyKAl-lite subroutines. This gets
    returned as a dictionary. Can optionally add a psykal_invokes
    dictionary to add to
    """

    # Having empty dict as a default value is dangerous so manually create
    if not psykal_invokes:
        psykal_invokes = {}

    # Analyse files with PSyKAl-lite code to create list of
    # subroutines within them
    for filename in psykal_files:
        with open(filename, encoding="utf-8") as psyfile:
            text = psyfile.readlines()
        for line in text:
            # Find lines with the appropriate keywords
            if all(item in line.lower() for item in
                   ["subroutine", "invoke_", "("]):
                # Note: including the end bracket misses multi-line subroutine
                # arguments
                ist = line.find("invoke_")
                iend = line.find("(")
                psyname = line[ist:iend]
                if psyname[7].isnumeric():
                    # If the name of the routine starts with a number (after
                    # the invoke_ and is a default generated subroutine)
                    # ignore it
                    continue
                psykal_invokes[psyname] = {}
                psykal_invokes[psyname]["psyfile"] = filename
    return psykal_invokes


def save_psykal_to_json(psykal_invokes: dict,
                        path: str = os.path.dirname(
                            os.path.realpath(__file__)),
                        filename: str = "PSyKAl.json") -> None:
    '''
    Saves the PSyKAl-lite information to a .JSON
    '''
    psykal_list = list(psykal_invokes.keys())
    json_object = json.dumps(psykal_list, indent=4, sort_keys=True)
    with open(path + "/" + filename, "w", encoding="utf-8") as outfile:
        outfile.write(json_object)
        print(path + "/" + filename + " generated")


def save_psykal_to_txt(psykal_invokes: dict,
                       path: str = os.path.dirname(os.path.realpath(__file__)),
                       filename: str = "PSyKAl.txt") -> None:
    psykal_list = list(psykal_invokes.keys())
    psykal_list.sort()
    try:
        f = open(path + "/" + filename, "x", encoding="utf-8")
    except FileExistsError:
        os.remove(path + "/" + filename)
    with open(path + "/" + filename, "a", encoding="utf-8") as f:
        for item in psykal_list:
            f.write(item + "\n")
        print(path + "/" + filename + " generated")


def run_psykal_check(path: str = "not_specified") -> None:
    """
    This function will check for PSyKAl-lite code in the repositories denoted
    by the inputs.
    """

    if path == "not_specified":
        # THrow an exception to say there's no path provided
        pass

    psykal_invokes = {}

    # Get all source files from directory
    print("Get all source files")
    source_files = get_source_files(path)
    # Create dictionary of all the PSyKAl-lite subroutines
    print("Find the PSyKAl-lite subroutines")
    psykal_invokes = find_psykal_subroutines(source_files, psykal_invokes)
    # Save the output
    save_psykal_to_txt(psykal_invokes,)
    save_psykal_to_json(psykal_invokes,)
    print(f"There are {len(psykal_invokes)} PSyKAl-lite subroutines")


if __name__ == "__main__":
    run_psykal_check(INPUT_APPS_PATH)
