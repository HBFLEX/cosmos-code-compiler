import sys
from lex import *
from emit import *


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter) -> None:
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set() # Variables declared so far.
        self.labelsDeclared = set() # Labels declared so far.
        self.labelsGotoed = set()

        self.cur_token = None
        self.peek_token = None
        self.next_token()
        self.next_token() # Call this twice to initialize current and peek

    # Return true if the current token matches.
    def check_token(self, kind: TokenType) -> bool:
        return kind == self.cur_token.kind

    # Return true if the next token matches.
    def check_peek(self, kind: TokenType) -> bool:
        return kind == self.peek_token.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind: TokenType):
        if not self.check_token(kind):
            self.abort(f'Expected {kind.name}, got {self.cur_token.kind.name}')
        self.next_token()

    # Advances the current token.
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message):
        sys.exit(f'Error Parsing: {message}')

    # Production rules.
    # program ::= { statement }
    def program(self):
        self.emitter.header_line('#include <stdio.h>')
        self.emitter.header_line('int main(void){')
        # Since some newlines are required in our grammar, need to skip the excess.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
        # Parse all the statements in the program
        while not self.check_token(TokenType.EOF):
            self.statement()
        # Wrap things up.
        self.emitter.emit_line('return 0;')
        self.emitter.emit_line('}')
        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort(f'Attempting to go to undeclared label: {label}')

    def statement(self):
        # "PRINT" (expression | string)
        if self.check_token(TokenType.PRINT):
            self.next_token()

            if self.check_token(TokenType.STRING):
                # Simple string, so print it.
                self.emitter.emit_line("printf(\"" + self.cur_token.text + "\\n\");")
                self.next_token()
            else:
                # Expect an expression and print the result as a float.
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emit_line('));')
        # "IF" comparison "THEN" { statements } "ENDIF"
        elif self.check_token(TokenType.IF):
            self.next_token()
            self.emitter.emit('if(')
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emit('){')
            # Zero or more statements in the body
            while not self.check_token(TokenType.ENDIF):
                self.statement()
            self.match(TokenType.ENDIF)
            self.emitter.emit_line('}')
        # "WHILE" comparison "REPEAT" { statement } "ENDWHILE"
        elif self.check_token(TokenType.WHILE):
            self.next_token()
            self.emitter.emit('while(')
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emit('){')
            # Zero or more statements in the loop body.
            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emit('}')
        # "LABEL" ident
        elif self.check_token(TokenType.LABEL):
            self.next_token()
            # Make sure this label doesn't already exist.
            if self.cur_token.text in self.labelsDeclared:
                self.abort(f'Label already exists: {self.cur_token.text}')
            self.labelsDeclared.add(self.cur_token.text)
            self.emitter.emit(f'{self.cur_token.text}:')
            self.match(TokenType.IDENT)

        # "GOTO" ident
        elif self.check_token(TokenType.GOTO):
            self.next_token()
            self.labelsGotoed.add(self.cur_token.text)
            self.emitter.emit_line(f'goto {self.cur_token.text};')
            self.match(TokenType.IDENT)

        # "LET" ident "=" expression
        elif self.check_token(TokenType.LET):
            self.next_token()
            #  Check if ident exists in symbol table. If not, declare it.
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line(f'float {self.cur_token.text};')
            self.emitter.emit(f'{self.cur_token.text} = ')
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emit_line(';')
        # "INPUT" ident
        elif self.check_token(TokenType.INPUT):
            self.next_token()
            #If variable doesn't already exist, declare it.
            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)
                self.emitter.header_line(f'float {self.cur_token.text};')

            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            self.emitter.emit_line(f'if(0 == scanf("%f", &{self.cur_token.text}))' + '{')
            self.emitter.emit_line(f'{self.cur_token.text} = 0;')
            self.emitter.emit('scanf("%')
            self.emitter.emit_line('*s");')
            self.emitter.emit_line('}')
            self.match(TokenType.IDENT)

        # This is not a valid statement. Error!
        else:
            self.abort(f'Invalid statement at {self.cur_token.text} ({self.cur_token.kind.name})')

        # newline
        self.nl()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()
        # Must be at least one comparison operator and another expression
        if self.isComparisonOperator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()
        else:
            self.abort(f'Expected comparison operator at {self.cur_token.text}')

        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.expression()
        
    # Return true if the current token is a comparison operator.
    def isComparisonOperator(self) -> bool:
        return self.check_token(TokenType.GT) or self.check_token(TokenType.GTEQ) or self.check_token(TokenType.LT) or self.check_token(TokenType.LTEQ) or self.check_token(TokenType.EQEQ) or self.check_token(TokenType.NOTEQ)

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()
        # Can have 0 or more +/- and expressions.
        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self): 
       self.unary()
       # Can have 0 or more *// and expressions.
       while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
           self.emitter.emit(self.cur_token.text)
           self.next_token()
           self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.cur_token.text not in self.symbols:
                self.abort(f'Referencing variable before assignment: {self.cur_token.text}')
            self.emitter.emit(self.cur_token.text)
            self.next_token()
        else:
            # Error!
            self.abort(f'Unexpected token at {self.cur_token.text}')

    # nl ::= '\n'+
    def nl(self):
        # reyuires atleast one line
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

