"""
Script to update the version placeholder in HTML files under a given directory.
It fetches the version from Commitizen by default, or you can provide it manually.
"""

import sys
from pathlib import Path
import subprocess


def get_version() -> str:
    """
    Get the current version from Commitizen.

    Returns:
        str: The current version string.
    """
    try:
        # Use universal_newlines for type checker compatibility
        version_bytes = subprocess.check_output(
            ["cz", "version"],
            universal_newlines=True,
        )
        version: str = version_bytes.strip()
        return version
    except subprocess.CalledProcessError as e:
        print("Error getting version from Commitizen:", e)
        sys.exit(1)


def update_html_version_directory(directory: str, new_version: str, placeholder: str = "[version]") -> None:
    """
    Replace the placeholder version in all HTML files under the given directory.

    Args:
        directory (str): Path to the HTML directory.
        new_version (str): Version string to replace the placeholder with.
        placeholder (str, optional): Placeholder text in HTML files. Defaults to "[version]".
    """
    html_dir_path = Path(directory)
    if not html_dir_path.exists():
        print(f"Error: HTML directory '{directory}' does not exist")
        sys.exit(1)

    for html_file in html_dir_path.rglob("*.html"):
        try:
            text_content = html_file.read_text(encoding="utf-8")
            updated_content = text_content.replace(placeholder, new_version)
            html_file.write_text(updated_content, encoding="utf-8")
            print(f"Updated {html_file} version to {new_version}")
        except (OSError, UnicodeDecodeError) as e:
            print(f"Failed to update {html_file}: {e}")


def main() -> None:
    """
    Main entry point for CLI usage.
    """
    # CLI usage: python update_docsite_html_version.py <html_dir> [version] [placeholder_version]
    if len(sys.argv) < 2:
        print("Usage: python update_docsite_html_version.py <html_dir> [version] [placeholder_version]")
        sys.exit(1)

    html_dir_cli: str = sys.argv[1]
    version_cli: str
    if len(sys.argv) > 2 and sys.argv[2]:
        version_cli = sys.argv[2]
    else:
        version_cli = get_version()

    placeholder_cli: str = sys.argv[3] if len(sys.argv) > 3 else "[version]"

    update_html_version_directory(html_dir_cli, version_cli, placeholder_cli)


if __name__ == "__main__":
    main()
