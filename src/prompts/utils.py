from textwrap import dedent


def prompt(text: str) -> str:
    return dedent(text).strip()
