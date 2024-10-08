import re
import sys
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])
RootNode = namedtuple("RootNode", "body")
KeyValueNode = namedtuple("KeyValueNode", ["key", "value"])
StringNode = namedtuple("StringNode", "value")
NumericNode = namedtuple("NumericNode", "value")
BooleanNode = namedtuple("BooleanNode", "value")
NullNode = namedtuple("NullNode", "value")


def tokenise(inp: str) -> list[Token]:
    OPEN_BRACE = r"(?P<OPEN_BRACE>{)"
    CLOSE_BRACE = r"(?P<CLOSE_BRACE>})"
    STRING = r'(?P<STRING>"\w+")'
    NUMERIC = r"(?P<NUMERIC>[-]?\d+\.?\d+)"
    COLON = r"(?P<COLON>:)"
    BOOLEAN = r"(?P<BOOLEAN>true|false)"
    COMMA = r"(?P<COMMA>,)"
    NULL = r"(?P<NULL>null)"
    WS = r"(?P<WS>\s+)"
    pattern = re.compile(
        "|".join(
            [OPEN_BRACE, NULL, BOOLEAN, CLOSE_BRACE, NUMERIC, STRING, WS, COLON, COMMA]
        )
    )

    def generate_tokens(pat, text):
        scanner = pat.scanner(text)
        for m in iter(scanner.match, None):
            match m.lastgroup:
                case "WS":
                    continue
                case "STRING":
                    # remove the surrounding quotes
                    yield Token(m.lastgroup, m.group()[1:-1])
                case _:
                    yield Token(m.lastgroup, m.group())

    return list(generate_tokens(pat=pattern, text=inp))


def parse(tokens: list[Token]) -> RootNode:
    def consume(expected_type: str):
        next_token = tokens.pop(0)
        if next_token.type != expected_type:
            raise RuntimeError(f"Parse error at {next_token}")
        return next_token.value

    def peek(expected_type: str):
        return tokens[0].type == expected_type

    def parse_numeric() -> NumericNode:
        return NumericNode(value=float(consume("NUMERIC")))

    def parse_boolean() -> BooleanNode:
        return BooleanNode(value=bool(consume("BOOLEAN")))

    def parse_value() -> StringNode | NumericNode | BooleanNode:
        if peek("STRING"):
            return StringNode(consume("STRING"))
        elif peek("NUMERIC"):
            return parse_numeric()
        elif peek("BOOLEAN"):
            return parse_boolean()
        elif peek("NULL"):
            return NullNode(consume("NULL"))
        else:
            raise RuntimeError(
                "Could not parse value, ensure it is of type (number, string, boolean, null)"
            )

    def parse_key_value_pair() -> KeyValueNode:
        key = StringNode(value=consume("STRING"))
        consume("COLON")
        value = parse_value()
        return KeyValueNode(key, value)

    def parse_body() -> list[KeyValueNode]:
        body = []
        body.append(parse_key_value_pair())
        while peek("COMMA"):
            consume("COMMA")
            body.append(parse_key_value_pair())
        return body

    consume("OPEN_BRACE")
    ast = RootNode(body=parse_body())
    consume("CLOSE_BRACE")
    return ast


def pprint_ast(ast: RootNode):
    print("RootNode(")
    for node in ast.body:
        print(f"  KeyValueNode({node.key}: {node.value})")
    print(")")


def main():
    file = sys.argv[1]
    with open(file) as f:
        pprint_ast(parse(tokenise(f.read())))


if __name__ == "__main__":
    main()
