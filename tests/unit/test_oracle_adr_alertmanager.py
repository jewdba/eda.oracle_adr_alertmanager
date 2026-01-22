"""Unit tests for the oracle_adr_alertmanager event source plugin.

These tests cover:
- Pattern compilation
- Buffer extraction
- Event building from ADR XML messages
"""

import re

import pytest

from plugins.event_source.oracle_adr_alertmanager import (
    _compile_pattern,  # pyright: ignore[reportPrivateUsage]
    _extract_msgs_from_buffer,  # pyright: ignore[reportPrivateUsage]
    _process_buffer,  # pyright: ignore[reportPrivateUsage]
)


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def sample_xml_msg() -> str:
    """Return a sample ADR XML <msg> string for testing."""
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
def multi_xml_msgs(sample_xml_msg: str) -> str:
    """Return two concatenated sample XML messages for testing multiple extraction."""
    return sample_xml_msg + sample_xml_msg


@pytest.fixture
def incomplete_msg() -> str:
    """Return an incomplete XML message (missing closing tags)."""
    return "<msg><txt>ORA-12345"


# -----------------------------
# Pattern compilation tests
# -----------------------------
def test_compile_pattern_from_string() -> None:
    """Verify _compile_pattern returns a compiled regex from a string."""
    pattern = _compile_pattern(r"ORA-\d+")
    assert isinstance(pattern, re.Pattern)
    assert pattern.pattern == r"ORA-\d+"


def test_compile_pattern_from_pattern() -> None:
    """Verify _compile_pattern returns the same pattern if already compiled."""
    regex = re.compile(r"ORA-\d+")
    result = _compile_pattern(regex)
    assert result is regex


def test_compile_pattern_invalid_type() -> None:
    """Verify _compile_pattern raises TypeError for invalid argument type."""
    with pytest.raises(TypeError):
        _compile_pattern(123)  # type: ignore[arg-type]


# -----------------------------
# Buffer extraction tests
# -----------------------------
def test_extract_single_msg(sample_xml_msg: str) -> None:
    """Test extracting a single complete <msg> from buffer.

    Args:
        sample_xml_msg: str
            Sample XML <msg> string.

    """
    msgs, remainder = _extract_msgs_from_buffer(sample_xml_msg)
    assert len(msgs) == 1
    assert "<msg" in msgs[0]
    assert remainder.strip() == ""


def test_extract_multiple_msgs(multi_xml_msgs: str) -> None:
    """Test extracting multiple <msg> entries from a buffer.

    Args:
        multi_xml_msgs: str
            Sample XML <msg> string.

    """
    msgs, remainder = _extract_msgs_from_buffer(multi_xml_msgs)
    assert len(msgs) == 2  # noqa: PLR2004
    assert remainder.strip() == ""


def test_extract_incomplete_msg(incomplete_msg: str) -> None:
    """Test that incomplete <msg> remains in buffer and is not extracted.

    Args:
        incomplete_msg: str
            Sample XML <msg> string.

    """
    msgs, remainder = _extract_msgs_from_buffer(incomplete_msg)
    assert not msgs
    assert remainder == incomplete_msg


# -----------------------------
# Event building tests
# -----------------------------
def test_matching_event(sample_xml_msg: str) -> None:
    """Test _process_buffer returns events matching the regex pattern.

    Args:
        sample_xml_msg: str
            Sample XML <msg> string.

    """
    events, remainder = _process_buffer(
        buffer=sample_xml_msg,
        pattern_regex=re.compile(r"ORA-\d+"),
        path="/adr/home",
        adr_xml_logfile="/adr/home/alert/log.xml",
    )

    assert len(events) == 1
    event = events[0]
    assert event["adr_home"] == "/adr/home"
    assert event["msg_type"] == "ERROR"
    assert "ORA-00600" in event["message"]
    assert remainder.strip() == ""


def test_non_matching_event(sample_xml_msg: str) -> None:
    """Test _process_buffer returns empty list for non-matching regex.

    Args:
        sample_xml_msg: str
            Sample XML <msg> string.

    """
    events, remainder = _process_buffer(
        buffer=sample_xml_msg,
        pattern_regex=re.compile(r"TNS-\d+"),
        path="/adr/home",
        adr_xml_logfile="/adr/home/alert/log.xml",
    )
    assert not events
    assert remainder.strip() == ""


def test_invalid_xml_is_ignored() -> None:
    """Test that malformed XML is ignored by _process_buffer."""
    buffer = "<msg><txt>ORA-12345</txt>"
    events, remainder = _process_buffer(
        buffer=buffer,
        pattern_regex=re.compile(r"ORA-\d+"),
        path="/adr",
        adr_xml_logfile="/adr/log.xml",
    )
    assert not events
    assert remainder == buffer


def test_partial_and_complete_msgs() -> None:
    """Test processing a buffer with one complete and one partial <msg>."""
    buffer = "<msg><txt>ORA-001</txt></msg><msg><txt>ORA-002"
    events, remainder = _process_buffer(
        buffer=buffer,
        pattern_regex=re.compile(r"ORA-\d+"),
        path="/adr",
        adr_xml_logfile="/adr/log.xml",
    )
    assert len(events) == 1
    assert "ORA-001" in events[0]["message"]
    assert remainder == "<msg><txt>ORA-002"


def test_event_fields_present(sample_xml_msg: str) -> None:
    """Test that all required fields are present in processed event.

    Args:
       sample_xml_msg: str
           Sample XML <msg> string.

    """
    events, remainder = _process_buffer(
        buffer=sample_xml_msg,
        pattern_regex=re.compile(r"ORA-\d+"),
        path="/adr",
        adr_xml_logfile="/adr/log.xml",
    )
    event = events[0]
    keys = [
        "adr_home",
        "pattern",
        "time",
        "org_id",
        "comp_id",
        "msg_type",
        "level",
        "host_id",
        "host_addr",
        "pid",
        "message",
    ]
    for key in keys:
        assert key in event


def test_regex_case_insensitive(sample_xml_msg: str) -> None:
    """Test that regex matching is case-insensitive.

    Args:
        sample_xml_msg: str
            Sample XML <msg> string.

    """
    events, remainder = _process_buffer(
        buffer=sample_xml_msg,
        pattern_regex=re.compile(r"ora-\d+", re.IGNORECASE),
        path="/adr",
        adr_xml_logfile="/adr/log.xml",
    )
    assert len(events) == 1
    assert "ORA-00600" in events[0]["message"]


def test_regex_no_match_returns_empty(sample_xml_msg: str) -> None:
    """Test that a regex with no matches returns an empty event list.

    Args:
        sample_xml_msg: str
            Sample XML <msg> string.

    """
    events, remainder = _process_buffer(
        buffer=sample_xml_msg,
        pattern_regex=re.compile(r"NON-EXISTENT"),
        path="/adr",
        adr_xml_logfile="/adr/log.xml",
    )
    assert not events
    assert remainder.strip() == ""
