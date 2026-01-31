"""
Script to update the version in galaxy.yml using a provided tag.
"""

import yaml
import sys
import os

GALAXY_FILE = "galaxy.yml"


def update_galaxy_yml(version: str) -> None:
    """
    Update the version in galaxy.yml.

    Args:
        version (str): Version string to set.
    """
    if not os.path.exists(GALAXY_FILE):
        print(f"{GALAXY_FILE} not found!")
        sys.exit(1)

    print(f"Updating {GALAXY_FILE} version to {version}")

    # Load YAML
    with open(GALAXY_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Update version
    data["version"] = version

    # Save YAML
    with open(GALAXY_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    print(f"{GALAXY_FILE} updated successfully!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build/update_galaxy_version.py <version>")
        sys.exit(1)

    version_arg = sys.argv[1]
    update_galaxy_yml(version_arg)
