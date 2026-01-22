"""Integration tests for the Oracle ADR Alertmanager event source plugin.

Tests include:
- Basic tailing of ADR XML log messages.
- Handling of file rotations.
- Regex-based filtering of messages.
"""

import asyncio
from asyncio import Queue, Task
from pathlib import Path

import aiofiles
import pytest

from plugins.event_source.oracle_adr_alertmanager import tail_adr_xml_logfile


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def adr_dir(tmp_path: Path) -> Path:
    """Create a temporary ADR home directory with 'alert' folder.

    Args:
        adr_dir: Path
            pytest temporary path fixture.

    Returns:
        Path:
            The ADR home path with 'alert' subfolder.

    """
    alert_dir = tmp_path / "alert"
    alert_dir.mkdir()
    return tmp_path


@pytest.fixture
def xml_msg() -> str:
    """Sample ADR XML <msg> for testing.

    Returns:
        str: XML string with ORA-29999 error.

    """
    return """<msg time="2024-01-01T00:00:00"
        org_id="oracle"
        comp_id="rdbms"
        type="ERROR"
        level="1"
        host_id="db01"
        host_addr="127.0.0.1"
        pid="12345">
        <txt>ORA-29999: user defined error code</txt>
    </msg>
    """


@pytest.fixture
def first_sample_xml_msg() -> str:
    """Sample ADR XML <msg> for testing.

    Returns:
        str: XML string with ORA-00600 error.

    """
    return """<msg time="2024-01-01T00:00:00"
        org_id="oracle"
        comp_id="rdbms"
        type="ERROR"
        level="1"
        host_id="db01"
        host_addr="127.0.0.1"
        pid="12345">
        <txt>ORA-00600: internal error code</txt>
    </msg>
    """


@pytest.fixture
def second_sample_xml_msg() -> str:
    """Another ADR XML <msg> for testing rotation.

    Returns:
        str:
            XML string with ORA-07445 error.

    """
    return """<msg time="2024-01-01T00:01:00"
        org_id="oracle"
        comp_id="rdbms"
        type="ERROR"
        level="2"
        host_id="db01"
        host_addr="127.0.0.1"
        pid="12346">
        <txt>ORA-07445: error after rotation</txt>
    </msg>
    """


# -----------------------------
# Integration Tests
# -----------------------------
@pytest.mark.asyncio
async def test_tail_adr_xml_logfile_basic(
    adr_dir: Path,
    xml_msg: str,
) -> None:
    """Test that tail_adr_xml_logfile reads matching messages from ADR XML logfile.

    Steps:
    - Writes a sample XML message to the log file.
    - Verifies the event is pushed to the async queue.
    - Ignores non-matching messages.
    - Cancels the tail task cleanly.

    Args:
        adr_dir: Path
            Temporary ADR home directory fixture.
        xml_msg: str
            Sample XML <msg> string fixture.

    """
    log_file: Path = adr_dir / "alert" / "log.xml"
    log_file.write_text("")  # create empty file

    queue: Queue[dict[str, str]] = asyncio.Queue(maxsize=10)

    # Start tailer
    tail_task: Task[None] = asyncio.create_task(
        tail_adr_xml_logfile(
            adr_home=str(adr_dir),
            queue=queue,
            pattern=r"ORA-\d+",
            delay=0.05,
        ),
    )

    await asyncio.sleep(0.05)  # wait for tailer to start

    # Append a matching event
    async with aiofiles.open(log_file, mode="a") as f:
        await f.write(xml_msg)

    await asyncio.sleep(0.1)

    # Verify event is in queue
    event: dict[str, str] = await asyncio.wait_for(queue.get(), timeout=1)
    assert event["adr_home"] == str(adr_dir)
    assert event["msg_type"] == "ERROR"
    assert "ORA-29999" in event["message"]

    # Append a non-matching event
    async with aiofiles.open(log_file, mode="a") as f:
        await f.write("<msg><txt>No match here</txt></msg>\n")

    await asyncio.sleep(0.1)
    assert queue.empty()  # should ignore non-matching

    # Cancel tail task
    tail_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await tail_task


@pytest.mark.asyncio
async def test_tail_detects_file_rotation(
    adr_dir: Path,
    first_sample_xml_msg: str,
    second_sample_xml_msg: str,
) -> None:
    """Test that tail_adr_xml_logfile correctly detects file rotation.

    Steps:
    - Write initial event.
    - Rotate (truncate) log file.
    - Write new event.
    - Verify both events are read correctly from the queue.

    Args:
        adr_dir: Path
            Temporary ADR home directory fixture.
        first_sample_xml_msg: str
            Sample XML <msg> string fixture.
        second_sample_xml_msg: str
            Another sample XML <msg> string fixture.

    """
    log_file: Path = adr_dir / "alert" / "log.xml"
    log_file.write_text("")  # create empty file

    queue: Queue[dict[str, str]] = asyncio.Queue(maxsize=10)

    # Start tailer
    tail_task: Task[None] = asyncio.create_task(
        tail_adr_xml_logfile(
            adr_home=str(adr_dir),
            queue=queue,
            pattern=r"ORA-\d+",
            delay=0.05,
        ),
    )

    await asyncio.sleep(0.05)

    # Append first event
    async with aiofiles.open(log_file, mode="a") as f:
        await f.write(first_sample_xml_msg)

    await asyncio.sleep(0.1)
    event1: dict[str, str] = await asyncio.wait_for(queue.get(), timeout=1)
    assert "ORA-00600" in event1["message"]

    # Simulate file rotation
    log_file.write_text("")

    await asyncio.sleep(0.05)

    # Append new event after rotation
    async with aiofiles.open(log_file, mode="a") as f:
        await f.write(second_sample_xml_msg)

    await asyncio.sleep(0.1)
    event2: dict[str, str] = await asyncio.wait_for(queue.get(), timeout=1)
    assert "ORA-07445" in event2["message"]

    # Cancel tail task
    tail_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await tail_task
