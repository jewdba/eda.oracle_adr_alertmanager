"""
Script to update the version in galaxy.yml using Commitizen.
"""

import subprocess
import os
import sys
from typing import Optional

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with `pip install pyyaml`.")
    sys.exit(1)


def get_commitizen_version() -> str:
    """
    Get the current version from Commitizen.

    Returns:
        str: The current version string.

    Raises:
        SystemExit: If the cz command fails.
    """
    try:
        # Use -- separator for Commitizen to accept extra git args like --short
        version_bytes = subprocess.check_output(
            ["cz", "version"],
            text=True,
        )
        version = version_bytes.strip()
        return version
    except subprocess.CalledProcessError as e:
        print("Error getting version from Commitizen:", e)
        sys.exit(1)


def update_galaxy_yml(filename: str, version: Optional[str] = None) -> None:
    """
    Update the version in galaxy.yml.

    Args:
        filename (str): Path to the galaxy.yml file.
        version (Optional[str]): Version to set. If None, fetched from Commitizen.
    """
    if not os.path.exists(filename):
        print(f"{filename} not found!")
        sys.exit(1)

    if version is None:
        version = get_commitizen_version()

    print(f"Updating {filename} version to {version}")

    # Load YAML
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Update version
    data["version"] = version

    # Save YAML
    with open(filename, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    print(f"{filename} updated successfully!")


if __name__ == "__main__":
    # CLI: python build/update_galaxy_version.py [galaxy.yml] [version]
    yaml_file = sys.argv[1] if len(sys.argv) > 1 else "galaxy.yml"
    version_arg = sys.argv[2] if len(sys.argv) > 2 else None

    update_galaxy_yml(yaml_file, version_arg)
