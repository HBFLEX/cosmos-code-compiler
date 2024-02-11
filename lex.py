import sys
import enum


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


class Token:
    def __init__(self, token_text, token_kind) -> None:
        self.text = token_text
        self.kind = token_kind

    @staticmethod
    def checkIfKeyword(token_text):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == token_text and kind.value >= 100 and kind.value <= 200:
                return kind
        return None


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.cur_char = '' # Current character in the string
        self.cur_pos = -1 # Current position in the string
        self.next_char()

    # process the next character
    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = '\0' # EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    # return the lookahead character
    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return '\0' # EOF
        return self.source[self.cur_pos + 1]

    # invalid token found, print error message and abort
    def abort(self, message:str) -> str:
        sys.exit(f'Lexing error: {message}')

    # skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skip_whitespace(self):
        while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()

    # skip comments in the code
    def skip_comment(self):
        if self.cur_char == '#':
            while self.cur_char != '\n':
                self.next_char()

    # return the next token
    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()
        token = None
        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        
        if self.cur_char == '+':
            token = Token(self.cur_char, TokenType.PLUS)                   # Plus token.
        elif self.cur_char == '-':
            token = Token(self.cur_char, TokenType.MINUS)                  # Minus token.
        elif self.cur_char == '*':
            token = Token(self.cur_char, TokenType.ASTERISK)               # Asterik token.
        elif self.cur_char == '/':
            token = Token(self.cur_char, TokenType.SLASH)                  # Slash token.
        elif self.cur_char == '\n':
            token = Token(self.cur_char, TokenType.NEWLINE)                # New line token
        elif self.cur_char == '=':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.EQEQ)    # Double eQuals token
            else:
                token = Token(self.cur_char, TokenType.EQ)                  # eQuals token
        elif self.cur_char == '>':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.GTEQ)    # Greater than eQual token
            else:
                token = Token(self.cur_char, TokenType.GT)                  # Greater than token
        elif self.cur_char == '<':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.LTEQ)    # Less than eQual token
            else:
                token = Token(self.cur_char, TokenType.LT)                  # Less than token
        elif self.cur_char == '!':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.NOTEQ)   # Not eQual to token
            else:
                self.abort(f'Expected != got !{self.peek()}')
        elif self.cur_char == '\"':
            self.next_char()
            start_pos = self.cur_pos

            while self.cur_char != '\"':
                if self.cur_char == '\r' or self.cur_char == '\t' or self.cur_char == '\\' or self.cur_char == '%':
                    self.abort('Illegal characters in string')
                self.next_char()
            tok_text = self.source[start_pos:self.cur_pos]
            token = Token(tok_text, TokenType.STRING)                       # String token
        elif self.cur_char.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            start_pos = self.cur_pos
            
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.': # Decimal!
                self.next_char()
                # Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    self.abort('Illegal characters in number')
                while self.peek().isdigit():
                    self.next_char() 
            tok_num = self.source[start_pos:self.cur_pos + 1] # Get the substring.
            token = Token(tok_num, TokenType.NUMBER)                       # Number token
        elif self.cur_char.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            start_pos = self.cur_pos
            while self.peek().isalnum():
                self.next_char()
            # Check if the token is in the list of keywords.
            tok_text = self.source[start_pos:self.cur_pos + 1] # Get the substring
            keyword = Token.checkIfKeyword(tok_text)

            if keyword == None: # Identifier
                token = Token(tok_text, TokenType.IDENT)                   # Identifier token
            else:
                token = Token(tok_text, keyword)                           # Keyword token

        elif self.cur_char == '\0':
            token = Token(self.cur_char, TokenType.EOF)                    # EOF token
        else:
            # Unknown token
            self.abort(f'Unknown token {self.cur_char}')
        self.next_char()
        return token
