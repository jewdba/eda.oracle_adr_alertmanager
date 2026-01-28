"""
Script to update the version in galaxy.yml using Commitizen.
"""

import subprocess
import os
import sys

import yaml

# Get the new version from Commitizen
try:
    version = subprocess.check_output(["cz", "version", "--short"], text=True).strip()
except subprocess.CalledProcessError as e:
    print("Error getting version from Commitizen:", e)
    sys.exit(1)

print(f"Updating galaxy.yml version to {version}")

# Check if galaxy.yml exists
if not os.path.exists("galaxy.yml"):
    print("galaxy.yml not found!")
    sys.exit(1)

# Load galaxy.yml
with open("galaxy.yml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# Update version
data["version"] = version

# Save galaxy.yml
with open("galaxy.yml", "w", encoding="utf-8") as f:
    yaml.safe_dump(data, f, sort_keys=False)

print("galaxy.yml updated successfully!")
