# Emitter object keeps track of the generated code and outputs it.
class Emitter:
    def __init__(self, full_path) -> None:
        self.full_path = full_path
        self.header = ''
        self.code = ''

    def emit(self, code) -> None:
        self.code += code

    def emit_line(self, code) -> None:
        self.code += code + '\n'

    def header_line(self, code) -> None:
        self.header += code + '\n'

    def writeFile(self):
        with open(self.full_path, 'w') as output_file:
            output_file.write(self.header + self.code)
    