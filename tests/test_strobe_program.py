from __future__ import annotations

import pytest

from tools.strobe_program import parse_program, value_at


def test_parse_constants_interpolation_and_off() -> None:
    segments = parse_program(
        "s(0,1.5,z,z);s(1.5,5,c(7.5),l(0.01,0.2));s(5,6,l(7.5,8.5),c(0.2))"
    )

    assert len(segments) == 3
    assert segments[0].frequency.is_off
    assert segments[1].frequency.is_constant
    assert value_at(segments[1].duty, 0.5) == pytest.approx(0.105)
    assert value_at(segments[2].frequency, 0.5) == pytest.approx(8.0)


def test_rejects_timeline_gap() -> None:
    with pytest.raises(ValueError, match="gap or overlap"):
        parse_program("s(0,1,z,z);s(2,3,c(8),c(0.5))")


def test_rejects_unparsed_text() -> None:
    with pytest.raises(ValueError, match="unparsed"):
        parse_program("garbage;s(0,1,z,z)")
