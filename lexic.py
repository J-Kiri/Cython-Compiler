from ttoken import TOKEN


class Lexic:
    def __init__(self, code_file):
        self.codeFile = code_file
        self.code = self.codeFile.read()
        self.fileSize = len(self.code)
        self.indexCode = 0
        self.readToken = None
        self.line = 1
        self.column = 0

    def end_of_file(self):
        return self.indexCode >= self.fileSize

    def get_char(self):
        if self.end_of_file():
            return '\0'

        car = self.code[self.indexCode]
        self.indexCode += 1
        if car == '\n' or (car == '\r' and self.peek_char() != '\n'):
            self.line += 1
            self.column = 0
        else:
            self.column += 1
        return car

    def peek_char(self):
        if self.indexCode >= self.fileSize:
            return '\0'
        return self.code[self.indexCode]

    def unget_char(self, symbol):
        if symbol == '\n':
            self.line -= 1

        if self.indexCode > 0:
            self.indexCode -= 1

        self.column -= 1

    @staticmethod
    def print_token(running_token):
        (token, lexeme, line, column) = running_token
        msg = TOKEN.message(token)
        print(f'(tk = {msg}, lex = {lexeme}, line = {line}, column = {column})')

    def get_token(self):
        state = 1
        symbol = self.get_char()
        lexeme = ''

        # Ignorar espaços, tabs, newlines e comentários
        while symbol in [' ', '\t', '\n', '\r', '#']:
            if symbol == '#':  # Comentários
                while symbol != '\n' and not self.end_of_file():
                    symbol = self.get_char()
            symbol = self.get_char()

        if symbol == '\0':
            return TOKEN.EOF, "EOF", self.line, self.column

        lin = self.line
        col = self.column

        while True:
            if state == 1:
                if symbol == '\0':
                    return TOKEN.EOF, "EOF", lin, col
                elif symbol.isalpha():
                    state = 2  # Identificadores/palavras reservadas
                elif symbol.isdigit():
                    state = 3  # Números inteiros
                elif symbol == '"':
                    state = 4  # Strings
                    symbol = self.get_char()
                elif symbol == "(":
                    return TOKEN.openParenthesis, "(", lin, col
                elif symbol == ")":
                    return TOKEN.closeParenthesis, ")", lin, col
                elif symbol == ",":
                    return TOKEN.comma, ",", lin, col
                elif symbol == "[":
                    return TOKEN.openBracket, "[", lin, col
                elif symbol == "]":
                    return TOKEN.closeBracket, "]", lin, col
                elif symbol == "{":
                    return TOKEN.openBraces, "{", lin, col
                elif symbol == "}":
                    return TOKEN.closeBraces, "}", lin, col
                elif symbol == ";":
                    return TOKEN.semiColon, ";", lin, col
                elif symbol == ":":
                    return TOKEN.colon, ":", lin, col
                elif symbol == "+":
                    return TOKEN.plus, "+", lin, col
                elif symbol == "-":
                    return TOKEN.minus, "-", lin, col
                elif symbol == "*":
                    return TOKEN.star, "*", lin, col
                elif symbol == "/":
                    return TOKEN.slash, "/", lin, col
                elif symbol == "=":
                    next_char = self.peek_char()
                    if next_char == "=":
                        self.get_char()
                        return TOKEN.equalEqual, "==", lin, col
                    else:
                        return TOKEN.equal, "=", lin, col
                elif symbol == "!":
                    if self.peek_char() == "=":
                        self.get_char()
                        return TOKEN.notEqual, "!=", lin, col
                    else:
                        return TOKEN.ERROR, "!", lin, col
                elif symbol == ">":
                    if self.peek_char() == "=":
                        self.get_char()
                        return TOKEN.greaterThanOrEqual, ">=", lin, col
                    else:
                        return TOKEN.greaterThan, ">", lin, col
                elif symbol == "<":
                    if self.peek_char() == "=":
                        self.get_char()
                        return TOKEN.lessThanOrEqual, "<=", lin, col
                    else:
                        return TOKEN.lessThan, "<", lin, col
                else:
                    return TOKEN.ERROR, symbol, lin, col

            elif state == 2:  # Identificadores e palavras reservadas
                lexeme += symbol
                symbol = self.get_char()
                while symbol.isalnum():
                    lexeme += symbol
                    symbol = self.get_char()
                self.unget_char(symbol)
                return TOKEN.is_terminal(lexeme), lexeme, lin, col

            elif state == 3:  # Números inteiros
                lexeme += symbol
                symbol = self.get_char()
                while symbol.isdigit():
                    lexeme += symbol
                    symbol = self.get_char()

                if symbol == '.':
                    lexeme += symbol
                    symbol = self.get_char()
                    if not symbol.isdigit():
                        self.unget_char(symbol)
                        return TOKEN.ERROR, lexeme, lin, col
                    state = 31
                else:
                    self.unget_char(symbol)
                    return TOKEN.valInt, lexeme, lin, col

            elif state == 31:  # Parte decimal após o ponto
                lexeme += symbol
                symbol = self.get_char()
                while symbol.isdigit():
                    lexeme += symbol
                    symbol = self.get_char()
                self.unget_char(symbol)
                return TOKEN.valFloat, lexeme, lin, col

            elif state == 4:  # Strings
                while True:
                    if symbol == '"':
                        return TOKEN.valString, lexeme, lin, col

                    if symbol in ['\n', '\0']:
                        return TOKEN.ERROR, lexeme, lin, col

                    if symbol == '\\':  # Caracteres de escape
                        lexeme += symbol
                        symbol = self.get_char()
                        if symbol in ['\n', '\0']:
                            return TOKEN.ERROR, lexeme, lin, col

                    lexeme += symbol
                    symbol = self.get_char()

    @classmethod
    def is_terminal(cls, lexeme):
        reserved = {
            'void': TOKEN.VOID,
            'int': TOKEN.INT,
            'float': TOKEN.FLOAT,
            'string': TOKEN.STRING,
            'if': TOKEN.IF,
            'else': TOKEN.ELSE,
            'elif': TOKEN.ELIF,
            'while': TOKEN.WHILE,
            'for': TOKEN.FOR,
            'foreach': TOKEN.FOREACH,
            'continue': TOKEN.CONTINUE,
            'break': TOKEN.BREAK,
            'return': TOKEN.RETURN,
            'read': TOKEN.READ,
            'write': TOKEN.WRITE,
            'mod': TOKEN.MOD,
            'div': TOKEN.DIV,
            'not': TOKEN.NOT,
            'and': TOKEN.AND,
            'or': TOKEN.OR
        }
        return reserved.get(lexeme, TOKEN.ident)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            lexer = Lexic(f)
            token = lexer.get_token()
            while token[0] != TOKEN.EOF:
                Lexic.print_token(token)
                token = lexer.get_token()