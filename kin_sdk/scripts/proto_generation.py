"""
This script generates the protobuf and gRPC files from the proto files.
"""

import os
import subprocess
from typing import List


def create_init_files(directory: str) -> None:
    """
    Create __init__.py files in all subdirectories of the given directory to make them Python packages.
    Additionally, create an __init__.py in the root directory itself.

    Args:
        directory (str): The directory to create __init__.py files in.
    """
    for root, dirs, _ in os.walk(directory):
        # Ensure __init__.py exists in each subdirectory
        for dir in dirs:
            init_file_path = os.path.join(root, dir, "__init__.py")
            open(init_file_path, "a", encoding="utf-8").close()

        # Create __init__.py in the current root if it doesn't exist
        root_init_file = os.path.join(root, "__init__.py")
        open(root_init_file, "a", encoding="utf-8").close()


def add_import_prefix(
    directory: str, prefix: str, startswith: str = "digitalkin"
) -> None:
    """
    Add a prefix to import statements in all Python files within the directory.

    Args:
        directory (str): The directory containing Python files to update.
        prefix (str): The prefix to add to import statements.
        startswith (str): The import line start to check before adding the prefix.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".py", ".pyi")):
                file_path = os.path.join(root, file)
                with open(file_path, "r+", encoding="utf-8") as f:
                    content = f.readlines()
                    f.seek(0)
                    f.truncate()
                    for line in content:
                        if line.strip().startswith(f"from {startswith}"):
                            line = f"from {prefix}.{line.lstrip('from ')}"
                        f.write(line)


def main():
    """
    Generate the protobuf and gRPC files from the proto files.
    """
    proto_dir = "service-apis/proto"
    buf_file = "buf.gen.py.yaml"
    output_dir = "proto/"

    proto_paths: List[str] = [f"{proto_dir}/digitalkin/service", f"{proto_dir}/google"]
    paths_option = " ".join(f"--path {path}" for path in proto_paths)
    command = f"buf generate {proto_dir} --template {proto_dir}/{buf_file} --include-imports -o {output_dir} {paths_option}"

    print(command)

    # Use subprocess.run to execute the command
    result = subprocess.run(
        command, shell=True, text=True, capture_output=True, check=True
    )

    # Check if the command was successful
    if result.returncode == 0:
        print("Command executed successfully!")
        print("Output:")
        print(result.stdout)
        # Create __init__.py files after successful generation
        create_init_files(output_dir)
        print(f"Initialized Python package structure in {output_dir}")

        # Add import prefix
        import_prefix = "proto"  # Define the prefix here
        add_import_prefix(output_dir, import_prefix, "digitalkin")
        add_import_prefix(output_dir, import_prefix, "validate")
        print(
            f"Added import prefix '{import_prefix}' to all Python files in {output_dir}"
        )
    else:
        print("Command failed with the following error:")
        print(result.stderr)


if __name__ == "__main__":
    main()
