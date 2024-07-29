# Scans a C File and return a list of tokens

from enum import Enum, auto 
import re


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value 
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class TokenType(Enum):
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    SEMICOLON = auto()
    INT = auto()
    RETURN = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    WHITESPACE = auto()
    EOF = auto()
    MINUS = auto()
    BITWISE_COMPLEMENT = auto()
    LOGICAL_NEGATION = auto()
    PLUS = auto()
    STAR = auto()
    SLASH = auto()

def tokenize(text):
    tokens = []
    pattern = "|".join([
        r"\{", # LEFT_BRACE
        r"\}", # RIGHT_BRACE
        r"\(", # LEFT_PAREN 
        r"\)", # RIGHT_PAREN 
        r";", # SEMICOLON
        r"\bint\b", # INT
        r"\b[a-zA-Z]\w*\b", # IDENTIFIER 
        r"\b[0-9]+\b", # NUMBER
        r"\s+", # WHITESPACE
        r"-", # MINUS 
        r"~", # BITWISE_COMPLEMENT 
        r"!", # LOGICAL_NEGATION
        r"\+", # PLUS 
        r"\*", # STAR 
        r"/", # SLASH
    ])
    
    for match in re.finditer(pattern, text):
        value = match.group()
        if value == "{":            token_type = TokenType.LEFT_BRACE 
        elif value == "}":          token_type = TokenType.RIGHT_BRACE 
        elif value == "(":          token_type = TokenType.LEFT_PAREN 
        elif value == ")":          token_type = TokenType.RIGHT_PAREN 
        elif value == ";":          token_type = TokenType.SEMICOLON 
        elif value == "int":        token_type = TokenType.INT 
        elif value == "return":     token_type = TokenType.RETURN 
        elif value == "-":          token_type = TokenType.MINUS
        elif value == "~":          token_type = TokenType.BITWISE_COMPLEMENT 
        elif value == "!":          token_type = TokenType.LOGICAL_NEGATION 
        elif value == "+":          token_type = TokenType.PLUS 
        elif value == "*":          token_type = TokenType.STAR 
        elif value == "/":          token_type = TokenType.SLASH
        elif value.isdigit():       token_type = TokenType.NUMBER
        elif value.isidentifier():  token_type = TokenType.IDENTIFIER 
        elif value.isspace():       token_type = TokenType.WHITESPACE 
        else:                       raise ValueError(f"Unexpected Token: {value}")

        if token_type != TokenType.WHITESPACE:
            tokens.append(Token(token_type, value))
    
    tokens.append(Token(TokenType.EOF, "EOF"))
    return tokens
