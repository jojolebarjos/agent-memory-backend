import re
from enum import EnumType, StrEnum
from textwrap import dedent


def clean_prompt(prompt: str) -> str:
    """Dedent and simplify whitespace."""

    assert "\t" not in prompt
    prompt = dedent(prompt)
    prompt = re.sub(r"(?<!\n)\n(?!\n)", " ", prompt)
    prompt = re.sub(r" +", " ", prompt)
    prompt = prompt.replace("\r", "")
    prompt = prompt.strip()
    return prompt


def make_enum(name: str, values: list[str]) -> EnumType:
    """Create a string enumeration with the given name and values."""

    return _StrEnum(name, values)  # type: ignore


class _StrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name
