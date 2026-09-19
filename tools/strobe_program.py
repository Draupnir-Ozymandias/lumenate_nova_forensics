#!/usr/bin/env python3
"""Parse the compact Lumenate strobe-session declaration language."""

from __future__ import annotations

from dataclasses import dataclass
import re


_SEGMENT_RE = re.compile(
    r"s\((?P<start>\d+(?:\.\d+)?),(?P<end>\d+(?:\.\d+)?),"
    r"(?P<frequency>z|[cl]\([^)]*\)),(?P<duty>z|[cl]\([^)]*\))\)"
)
_EXPRESSION_RE = re.compile(r"(?P<kind>[cl])\((?P<values>[^)]*)\)")


@dataclass(frozen=True)
class Expression:
    kind: str
    start: float | None = None
    end: float | None = None

    @property
    def is_off(self) -> bool:
        return self.kind == "zero"

    @property
    def is_constant(self) -> bool:
        return self.kind == "constant"


@dataclass(frozen=True)
class Segment:
    start_s: float
    end_s: float
    frequency: Expression
    duty: Expression


def parse_expression(text: str) -> Expression:
    if text == "z":
        return Expression("zero")
    match = _EXPRESSION_RE.fullmatch(text)
    if match is None:
        raise ValueError(f"invalid expression: {text!r}")
    values = tuple(float(value) for value in match.group("values").split(","))
    if match.group("kind") == "c" and len(values) == 1:
        return Expression("constant", values[0], values[0])
    if match.group("kind") == "l" and len(values) == 2:
        return Expression("linear", values[0], values[1])
    raise ValueError(f"invalid expression arity: {text!r}")


def parse_program(program: str) -> list[Segment]:
    """Parse a complete semicolon-delimited declaration and reject gaps."""
    segments: list[Segment] = []
    cursor = 0
    for match in _SEGMENT_RE.finditer(program):
        if match.start() != cursor:
            raise ValueError(f"unparsed program text at offset {cursor}")
        start_s = float(match.group("start"))
        end_s = float(match.group("end"))
        if end_s <= start_s:
            raise ValueError(f"non-positive segment {start_s}..{end_s}")
        if segments and start_s != segments[-1].end_s:
            raise ValueError(f"timeline gap or overlap at {start_s}")
        segments.append(
            Segment(
                start_s,
                end_s,
                parse_expression(match.group("frequency")),
                parse_expression(match.group("duty")),
            )
        )
        cursor = match.end()
        if cursor < len(program) and program[cursor] == ";":
            cursor += 1
    if cursor != len(program):
        raise ValueError(f"unparsed program text at offset {cursor}")
    if not segments:
        raise ValueError("empty strobe program")
    return segments


def value_at(expression: Expression, fraction: float) -> float | None:
    if expression.is_off:
        return None
    assert expression.start is not None and expression.end is not None
    return expression.start + (expression.end - expression.start) * fraction
