## Cosmos Code Compiler (CCC)
A simple compiler of my own programming language called cosmos

### Features
- supports print functionality
- supports input functionality
- supports numeric variable declarations
- supports while loops and if conditions
- supports label definition
- supports goto

### How it works
- it converts the source code to tokens through a lexer class.
- the tokens then are matched against the language grammar and form the program tree. This happens thorugh the parse class.
- Finally the emitter compiles the code to C code. Through the emit class.

😁 This project was for me to challenge myself how compilers work under the hood and boi i have learned ton of stuff. It may not look clean but it surely works flawlessly. I hope i keep adding new features.