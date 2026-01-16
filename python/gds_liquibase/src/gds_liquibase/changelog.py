"""Changelog file management and generation."""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from gds_liquibase.exceptions import ChangelogNotFoundError


class ChangelogManager:
    """Manage Liquibase changelog files.

    This class provides utilities for creating, parsing, and managing
    Liquibase changelog files.
    """

    def __init__(self, changelog_path: Path):
        """Initialize the changelog manager.

        Args:
            changelog_path: Path to the changelog file or directory
        """
        self.changelog_path = Path(changelog_path)

    def create_changelog(
        self,
        author: str,
        description: str,
        output_file: Optional[Path] = None,
    ) -> Path:
        """Create a new changelog file with proper XML structure.

        Args:
            author: Author email or name
            description: Description for the changelog
            output_file: Output file path (optional)

        Returns:
            Path to created changelog file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = self.changelog_path / f"db.changelog-{timestamp}.xml"

        # Create XML structure
        root = ET.Element(
            "databaseChangeLog",
            {
                "xmlns": "http://www.liquibase.org/xml/ns/dbchangelog",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": (
                    "http://www.liquibase.org/xml/ns/dbchangelog "
                    "http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd"
                ),
            },
        )

        # Add comment
        comment = ET.Comment(f" {description} ")
        root.append(comment)

        # Create tree and write
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")

        output_file.parent.mkdir(parents=True, exist_ok=True)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)

        return output_file

    def add_changeset(
        self,
        changelog_file: Path,
        changeset_id: str,
        author: str,
        comment: str,
        changes: List[ET.Element],
    ) -> None:
        """Add a changeset to an existing changelog file.

        Args:
            changelog_file: Path to changelog file
            changeset_id: Unique changeset ID
            author: Author email or name
            comment: Description of changes
            changes: List of change elements to add

        Raises:
            ChangelogNotFoundError: If changelog file doesn't exist
        """
        if not changelog_file.exists():
            raise ChangelogNotFoundError(f"Changelog not found: {changelog_file}")

        tree = ET.parse(changelog_file)
        root = tree.getroot()

        # Create changeset element
        changeset = ET.SubElement(root, "changeSet", {"id": changeset_id, "author": author})

        # Add comment
        comment_elem = ET.SubElement(changeset, "comment")
        comment_elem.text = comment

        # Add changes
        for change in changes:
            changeset.append(change)

        # Write back
        ET.indent(tree, space="    ")
        tree.write(changelog_file, encoding="utf-8", xml_declaration=True)

    def parse_changelog(self, changelog_file: Path) -> ET.Element:
        """Parse a changelog file and return the root element.

        Args:
            changelog_file: Path to changelog file

        Returns:
            Root XML element

        Raises:
            ChangelogNotFoundError: If changelog file doesn't exist
        """
        if not changelog_file.exists():
            raise ChangelogNotFoundError(f"Changelog not found: {changelog_file}")

        tree = ET.parse(changelog_file)
        return tree.getroot()

    def list_changesets(self, changelog_file: Path) -> List[dict]:
        """List all changesets in a changelog file.

        Args:
            changelog_file: Path to changelog file

        Returns:
            List of changeset dictionaries with id, author, and comment
        """
        root = self.parse_changelog(changelog_file)
        changesets = []

        for changeset in root.findall("{http://www.liquibase.org/xml/ns/dbchangelog}changeSet"):
            changeset_data = {
                "id": changeset.get("id"),
                "author": changeset.get("author"),
                "comment": None,
            }

            comment_elem = changeset.find("{http://www.liquibase.org/xml/ns/dbchangelog}comment")
            if comment_elem is not None and comment_elem.text:
                changeset_data["comment"] = comment_elem.text

            changesets.append(changeset_data)

        return changesets
