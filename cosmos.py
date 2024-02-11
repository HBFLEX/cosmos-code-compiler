from lex import *
from emit import *
from parse import *
import sys



def main():
    print('<----- CosmosCode Compiler -------->')

    if len(sys.argv) != 2:
        sys.exit('Error: Compiler needs source file as an argument')
    with open(sys.argv[1], 'r') as inputFile:
        source = inputFile.read()

    # Initialize lexer, emitter and parser
    lexer = Lexer(source=source)
    emitter = Emitter(full_path='out.c')
    parser = Parser(lexer=lexer, emitter=emitter)

    parser.program() # start the parser
    emitter.writeFile() # Write the output to file.
    print('Compiling completed.')

main()