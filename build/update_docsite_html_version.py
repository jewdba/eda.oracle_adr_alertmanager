"""
Script to update the version placeholder in HTML files under docs/docsite.
Pass the version directly as a parameter.
"""

import sys
from pathlib import Path

HTML_DIR = "docs/docsite"
PLACEHOLDER = "[version]"


def update_html_version(new_version: str) -> None:
    """
    Replace the placeholder version in all HTML files under docs/docsite.

    Args:
        new_version (str): Version string to replace the placeholder with.
    """
    html_dir_path = Path(HTML_DIR)
    if not html_dir_path.exists():
        print(f"Error: HTML directory '{HTML_DIR}' does not exist")
        sys.exit(1)

    for html_file in html_dir_path.rglob("*.html"):
        try:
            text_content = html_file.read_text(encoding="utf-8")
            updated_content = text_content.replace(PLACEHOLDER, new_version)
            html_file.write_text(updated_content, encoding="utf-8")
            print(f"Updated {html_file} version to {new_version}")
        except (OSError, UnicodeDecodeError) as e:
            print(f"Failed to update {html_file}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build/update_docsite_html_version.py <version>")
        sys.exit(1)

    version_arg = sys.argv[1]
    update_html_version(version_arg)
