import re
import sys
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])
RootNode = namedtuple("RootNode", "body")
KeyValueNode = namedtuple("KeyValueNode", ["key", "value"])
StringNode = namedtuple("StringNode", "value")


def tokenise(inp: str) -> list[Token]:
    OPEN_BRACE = r"(?P<OPEN_BRACE>{)"
    CLOSE_BRACE = r"(?P<CLOSE_BRACE>})"
    STRING = r'(?P<STRING>"\w+")'
    COLON = r"(?P<COLON>:)"
    COMMA = r"(?P<COMMA>,)"
    WS = r"(?P<WS>\s+)"
    pattern = re.compile("|".join([OPEN_BRACE, CLOSE_BRACE, STRING, WS, COLON, COMMA]))

    def generate_tokens(pat, text):
        scanner = pat.scanner(text)
        for m in iter(scanner.match, None):
            match m.lastgroup:
                case "WS":
                    continue
                case "STRING":
                    yield Token(m.lastgroup, m.group()[1:-1])
                case _:
                    yield Token(m.lastgroup, m.group())

    return list(generate_tokens(pat=pattern, text=inp))


def parse(tokens: list[Token]) -> RootNode:
    def consume(expected_type: str):
        next_token = tokens.pop(0)
        if next_token.type != expected_type:
            raise Exception(f"Parse error at {next_token}")
        return next_token.value

    def parse_body():
        key = StringNode(value=consume("STRING"))
        consume("COLON")
        value = StringNode(value=consume("STRING"))
        return RootNode(body=[KeyValueNode(key, value)])

    consume("OPEN_BRACE")
    ast = parse_body()
    consume("CLOSE_BRACE")
    return ast


def main():
    file = sys.argv[1]
    with open(file) as f:
        tokens = tokenise(f.read())
        print(parse(tokens))


if __name__ == "__main__":
    main()
