# {} -> RootNode(body={})
# {"key": "value"} -> RootNode(body={"key": "value"})
# {"key_1": "value_1", "key_2": value_2} -> RootNode(body={"key_1": "value_1", "key_2": value_2})

import re
import sys
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])
RootNode = namedtuple("RootNode", ["body"])


def tokenise(inp: str) -> list[Token]:
    OPEN_BRACE = r"(?P<OPEN_BRACE>{)"
    CLOSE_BRACE = r"(?P<CLOSE_BRACE>})"
    WS = r"(?P<WS>\s+)"
    pattern = re.compile("|".join([OPEN_BRACE, CLOSE_BRACE, WS]))

    def generate_tokens(pat, text):
        scanner = pat.scanner(text)
        for m in iter(scanner.match, None):
            yield Token(m.lastgroup, m.group())

    return list(generate_tokens(pat=pattern, text=inp))


def parse(tokens: list[Token]) -> RootNode:
    def consume(expected_type: str):
        next_token = tokens.pop(0)
        if next_token.type != expected_type:
            raise Exception(f"Parse error at {next_token}")
        return next_token

    consume("OPEN_BRACE")
    node = RootNode(body={})
    consume("CLOSE_BRACE")
    return node


def main():
    file = sys.argv[1]
    with open(file) as f:
        tokens = tokenise(f.read())
        print(parse(tokens))


if __name__ == "__main__":
    main()
