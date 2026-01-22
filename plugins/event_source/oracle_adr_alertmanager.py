"""Oracle Automatic Diagnostic Repository (ADR) alertmanager EDA source plugin

This plugin tails Oracle Automatic Diagnostic Repository (ADR) XML logfile
and emits events matching a specified pattern.
"""

import asyncio
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from re import Pattern
from typing import Any

if sys.version_info < (3, 12):
    raise RuntimeError("This plugin requires Python >= 3.12")

logger = logging.getLogger(__name__)

DOCUMENTATION = r"""
---
short_description: Receive events from Oracle Diagnostic Repository XML logfile based on a search pattern
description:
  - An ansible-rulebook event source module for getting events from Oracle Diagnostic Repository XML logfile.
  - Regex-based pattern matching
options:
  adr_home:
    description:
      - Oracle ADR home path.
    type: str
    required: true
  pattern:
    description:
      - Optional: Regex used to match message text.
    type: str
    default: "(TNS|ORA)-[0-9]{5}"
  delay:
    description:
      - The number of seconds to wait between polling.
    type: int
    default: 1
"""

EXAMPLES = r"""
- jewdba.eda.oracle_adr_alertmanager:
    adr_home: "/u01/app/oracle/diag/rdbms/mydb"
    pattern: "ORA-[0-9]{5}"
    delay: 1
"""


def _compile_pattern(pattern_arg: str | Pattern[str]) -> Pattern[str]:
    """Compile a string to a regex pattern or return a Pattern as-is.

    Raises:
        TypeError: If pattern_arg is not a str or Pattern[str].

    """
    if isinstance(pattern_arg, str):
        return re.compile(pattern_arg, re.IGNORECASE)

    if not isinstance(pattern_arg, Pattern):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = f"compile_pattern expects str or Pattern[str], got {type(pattern_arg).__name__!r}"
        raise TypeError(msg)

    return pattern_arg


def _extract_msgs_from_buffer(buffer: str) -> tuple[list[str], str]:
    """Extract complete <msg>...</msg> entries from the buffer.

    Args:
        buffer: str
            Incoming message buffer.

    Returns:
        - List of complete <msg> strings
        - Remaining buffer with incomplete data

    """
    msgs: list[str] = []

    while (end := buffer.find("</msg>")) != -1:
        msg_str = buffer[: end + len("</msg>")]
        msgs.append(msg_str)
        buffer = buffer[end + len("</msg>") :]
    return msgs, buffer


def _process_buffer(buffer: str, pattern_regex: Pattern[str], path: str, adr_xml_logfile: str) -> tuple[list[dict[str, Any]], str]:
    """Process an XML message buffer and extract matching <msg> events.

    The function:
    - Extracts complete <msg>...</msg> XML messages from the buffer
    - Parses each message as XML
    - Filters messages whose <txt> content matches the given regex
    - Returns structured event dictionaries for matched messages

    Args:
        buffer: str
            Incoming XML message buffer.
        pattern_regex: Pattern[str]
            Regex applied to the <txt> element content.
        path: str
            Oracle adr_home path.
        adr_xml_logfile: str
            Oracle ADR XML logfile (absolute path).

    Returns:
        tuple[list[dict[str, Any]], str]:
            - A list of event dictionaries built from matching <msg> elements.
            - The remaining buffer containing any incomplete message data.

    """
    events: list[dict[str, Any]] = []
    msgs, buffer = _extract_msgs_from_buffer(buffer)

    for xml_str in msgs:
        try:
            elem = ET.fromstring(xml_str)  # noqa: S314 (disable recommedation to use additional lib defusedxml)
            if elem.tag != "msg":
                continue
            txt_content = (elem.findtext("txt") or "").strip()
            if not pattern_regex.search(txt_content):
                continue

            event: dict[str, Any] = {
                "adr_home": path,
                "pattern": pattern_regex.pattern,
                "time": elem.attrib.get("time"),
                "org_id": elem.attrib.get("org_id"),
                "comp_id": elem.attrib.get("comp_id"),
                "msg_type": elem.attrib.get("type"),
                "level": elem.attrib.get("level"),
                "host_id": elem.attrib.get("host_id"),
                "host_addr": elem.attrib.get("host_addr"),
                "pid": elem.attrib.get("pid"),
                "message": txt_content,
            }
            events.append(event)
        except ET.ParseError:
            logger.warning("Failed to parse XML in %s", adr_xml_logfile)
            continue

    return events, buffer


async def tail_adr_xml_logfile(
    adr_home: str,
    queue: asyncio.Queue[dict[str, Any]],
    pattern: str | Pattern[str],
    delay: float,
) -> None:
    """Tail Oracle ADR XML logfile and push matching events to the queue."""
    pattern_regex = _compile_pattern(pattern)
    buffer = ""

    adr_xml_logfile = str(Path(adr_home) / "alert" / "log.xml")

    while True:
        try:
            # Open file in blocking thread
            fh = await asyncio.to_thread(open, adr_xml_logfile, "r", encoding="utf-8", errors="ignore")
            try:
                # Get initial inode
                stat = await asyncio.to_thread(os.stat, adr_xml_logfile)
                inode = stat.st_ino

                # Move to EOF
                await asyncio.to_thread(fh.seek, 0, os.SEEK_END)

                while True:
                    # Read next line (blocking in thread)
                    line = await asyncio.to_thread(fh.readline)
                    if line:
                        buffer += line
                        events, buffer = _process_buffer(buffer, pattern_regex, adr_home, adr_xml_logfile)
                        for event in events:
                            await queue.put(event)
                    else:
                        # Sleep between polls
                        await asyncio.sleep(delay)
                        try:
                            stat = await asyncio.to_thread(os.stat, adr_xml_logfile)
                            pos = await asyncio.to_thread(fh.tell)
                            # Detect rotation / truncation
                            if stat.st_ino != inode or stat.st_size < pos:
                                logger.info("File rotation detected, reopening %s", adr_xml_logfile)
                                break
                        except FileNotFoundError:
                            logger.warning("File %s missing, retrying...", adr_xml_logfile)
                            break
            finally:
                fh.close()
        except FileNotFoundError:
            logger.warning("File %s not found, retrying in %.1f sec", adr_xml_logfile, delay)
            await asyncio.sleep(delay)


async def main(event_queue: asyncio.Queue[dict[str, Any]], args: dict[str, Any]) -> None:
    """Ansible EDA event source plugin entrypoint.

    Starts tailing the ADR XML log file and submits matching events
    to the provided asyncio queue.

    Args:
        event_queue:  asyncio.Queue[dict[str, Any]]
            Event submission queue.
        args: dict[str, Any]
            Plugin arguments.
        Required keys:
            - adr_home : str
                Oracle ADR home path.
        Optional keys:
            - pattern: str
                Regex used to match message text.
            - delay: int | float
                Polling delay in seconds.

    """
    await tail_adr_xml_logfile(
        adr_home=str(args.get("adr_home")),
        queue=event_queue,
        pattern=args.get("pattern", r"(TNS|ORA)-[0-9]{5}"),
        delay=args.get("delay", 1),
    )


if __name__ == "__main__":

    class MockQueue(asyncio.Queue[dict[str, Any]]):
        """Mock asyncio.Queue for testing ADR XML event source."""

        async def put(self, item: dict[str, Any]) -> None:
            """Print the event (mock queue)."""
            print(item)  # noqa: T201

    # Create queue with proper max size
    mock_queue = MockQueue(maxsize=100)

    test_args = {
        "adr_home": "/tmp",  # noqa: S108
    }

    try:
        asyncio.run(main(mock_queue, test_args))
    except KeyboardInterrupt:
        logger.fatal("Execution interrupted by user")
