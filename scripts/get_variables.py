"""\
scripts / get_variables.py

--------------------------------------------------------------------------------

Author - Aditya Marathe
Email  - aditya.marathe.20@ucl.ac.uk

--------------------------------------------------------------------------------
"""

import os
import sys

import platform
from pathlib import Path

import dotenv
import uproot


def _apply_wsl_prefix(dir_: str) -> Path:
    """\
    [ Internal ]

    Apply the Windows Subsystem for Linux (WSL) prefix to the directory path.

    Parameters
    ----------
    dir_ : str
        The directory path.
    
    Returns
    -------
    Path
        The directory path with the WSL prefix.

    Notes
    -----
    This was added to make it convienent to work on WSL or Windows.

    --> This was a lazy copy-paste from Oscana's "utils.py"!
    """

    # Note: Only change the prefix from "C://" to "/mnt/" if the platform is
    #       Linux. This is done so that I can easily switch between WSL and
    #       Windows without needing to move files around.
    #
    #       This feature was only added for my convienence, and can be disabled.

    if platform.system() == "Linux" and dir_.startswith("C:"):
        dir_split = dir_.split("://")

        path = Path(
            "/mnt/" + dir_split[0][0].lower() + "/" + dir_split[1]
        ).resolve()

        return path

    return Path(dir_).resolve()


def main(
    example_file: str,
    root_variable: str,
    output_file: str | Path,
    overwrite: bool = False,
) -> None:
    """\
    Extracts the variable names from a ROOT file and updates the "database".

    Parameters
    ----------
    example_file : str
        The path to the example ROOT file.

    root_variable : str
        The root variable in the ROOT file.

    output_file : str | Path
        The path to the output text file. E.g., "sntp_std.txt" for the standard 
        record in MINOS SNTP files.
    """
    # (1) Prepare the output file.
    output_file = Path(output_file).expanduser().resolve()

    if output_file.is_file() and (not overwrite):
        print(
            f"Error: The output file '{output_file}' already exists."
            " Use the 'overwrite' option to overwrite it."
        )
        sys.exit(1)

    if output_file.suffix != ".txt":
        print(
            "Error: The output file must be a text file with a '.txt' suffix!"
        )
        sys.exit(1)

    # (2) Load environment variables from ".env" file.
    dotenv.load_dotenv()

    example_file_path = _apply_wsl_prefix(os.environ[example_file])

    if not example_file_path.is_file():
        print(f"Error: The file path '{example_file_path}' does not exist.")
        sys.exit(1)

    # (3) Keep track of the good variables.
    good_variables = []

    # (4) Open the example file.
    with uproot.open(example_file_path) as file:
        print(output_file.name, "\n" + "-" * len(output_file.name))

        for key in file[root_variable].keys():
            # (4.1) Check if there's any data to extract...
            try:
                data = file[root_variable][key].array(library="np")
            except Exception as _:
                continue

            if (data is None) or (len(data) < 1):
                continue

            del data

            variable_name = key.split("/")[-1]

            # (4.2) Print the variable name and add it to the list.
            print(variable_name)
            good_variables.append(variable_name)

        # (5) Write the good variables to a text file.
        with open(output_file, "w") as f:
            for var in good_variables:
                f.write(var + "\n")


if __name__ == "__main__":
    user_args = sys.argv[1:]

    if len(user_args) != 4:
        print(
            "Usage: `python get_variables.py <example_file> <root> <file_type>"
            " <overwrite>`"
        )
        sys.exit(1)

    main(
        example_file=user_args[0],
        root_variable=user_args[1],
        output_file=user_args[2],
        overwrite=user_args[3] == "True",
    )
