# Scans a C File and return a list of tokens

import re
from .tokentype import TokenType

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value 
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def tokenize(text):
    tokens = []
    pattern = "|".join([
        r"\{", # LEFT_BRACE
        r"\}", # RIGHT_BRACE
        r"\(", # LEFT_PAREN 
        r"\)", # RIGHT_PAREN 
        r";", # SEMICOLON
        r"\bint\b", # INT
        r"\breturn\b", # RETURN
        r"\b[a-zA-Z]\w*\b", # IDENTIFIER 
        r"\b[0-9]+\b", # NUMBER
        r"\s+", # WHITESPACE
        r"-", # MINUS 
        r"~", # BITWISE_COMPLEMENT 
        r"\+", # PLUS 
        r"\*", # STAR 
        r"/", # SLASH
        r"&&", # AND
        r"\|\|", # OR 
        r"==", # EQUAL 
        r"!=", # NOT_EQUAL
        r"<=", # LESS_THAN_OR_EQUAL
        r">=", # GREATER_THAN_OR_EQUAL
        r"%", # PERCENT 
        r"&", # BITWISE_AND
        r"\|", # BITWISE_OR
        r"^", # BITWISE_XOR 
        r"<<", # BITWISE_SHIFT_LEFT
        r">>", # BITWISE_SHIFT_RIGHT
        r"=", # ASSIGN
        r"!", # LOGICAL_NEGATION
        r"<", # LESS_THAN 
        r">", # GREATER_THAN
        r"\bif\b", # IF 
        r"\belse\b", # ELSE 
        r":", # COLON 
        r"\?", # QUESTION
        f"\bfor\b", # FOR 
        f"\bwhile\b", # WHILE 
        f"\bdo\b", # DO 
        f"\bbreak\b", # BREAK 
        f"\bcontinue\b", # CONTINUE
        f",", # COMMA
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
        elif value == "&&":         token_type = TokenType.AND 
        elif value == "||":         token_type = TokenType.OR 
        elif value == "==":         token_type = TokenType.EQUAL 
        elif value == "!=":         token_type = TokenType.NOT_EQUAL 
        elif value == "<":          token_type = TokenType.LESS_THAN 
        elif value == "<=":         token_type = TokenType.LESS_THAN_OR_EQUAL 
        elif value == ">":          token_type = TokenType.GREATER_THAN 
        elif value == ">=":         token_type = TokenType.GREATER_THAN_OR_EQUAL
        elif value == "%":          token_type = TokenType.PERCENT 
        elif value == "&":          token_type = TokenType.BITWISE_AND 
        elif value == "|":          token_type = TokenType.BITWISE_OR 
        elif value == "^":          token_type = TokenType.BITWISE_XOR 
        elif value == "<<":         token_type = TokenType.BITWISE_SHIFT_LEFT 
        elif value == ">>":         token_type = TokenType.BITWISE_SHIFT_RIGHT
        elif value == "=":          token_type = TokenType.ASSIGN
        elif value == "if":         token_type = TokenType.IF 
        elif value == "else":       token_type = TokenType.ELSE 
        elif value == ":":          token_type = TokenType.COLON 
        elif value == "?":          token_type = TokenType.QUESTION
        elif value == "for":        token_type = TokenType.FOR 
        elif value == "while":      token_type = TokenType.WHILE 
        elif value == "do":         token_type = TokenType.DO 
        elif value == "break":      token_type = TokenType.BREAK 
        elif value == "continue":   token_type = TokenType.CONTINUE
        elif value == ",":          token_type = TokenType.COMMA
        elif value.isdigit():       token_type = TokenType.NUMBER
        elif value.isspace():       token_type = TokenType.WHITESPACE 
        elif re.match(r"\b[a-zA-Z]\w*\b", value):       token_type = TokenType.IDENTIFIER 
        else:                       raise ValueError(f"Unexpected Token: {value}")

        if token_type != TokenType.WHITESPACE:
            tokens.append(Token(token_type, value))
    
    tokens.append(Token(TokenType.EOF, "EOF"))
    return tokens
