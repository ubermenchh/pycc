# Scans a C File and return a list of tokens

from enum import Enum 
import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value 
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class TokenType(Enum):
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    SEMICOLON = ";"
    INT = "int"
    RETURN = "return"
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    WHITESPACE = "WHITESPACE"

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
        r"\b[0-9]\b", # LITERAL 
        r"\s+" # WHITESPACE
        ])
    
    for match in re.finditer(pattern, text):
        value = match.group()
        if value in [e.value for e in TokenType if isinstance(e.value, str)]:
            token_type = TokenType(value)
        elif value.isdigit():
            token_type = TokenType.LITERAL 
        elif value.isidentifier():
            token_type = TokenType.IDENTIFIER 
        elif value.isspace():
            token_type = TokenType.WHITESPACE 
        else:
            raise ValueError(f"Unexpected Token: {value}")

        if token_type != TokenType.WHITESPACE:
            tokens.append(Token(token_type, value))
    
    return tokens


with open("main.c", "r") as f:
    text = f.read()

tokens = tokenize(text)
for token in tokens:
    print(token)
