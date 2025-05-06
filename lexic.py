from ttoken import TOKEN

class Lexic:
    def __init__ (self, code_file):
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
            return TOKEN.EOF, "EOF", self.line, self.column
        
        car = self.code[self.indexCode]
        self.indexCode += 1
        if car == '\n'or (car == '\r' and self.code[self.indexCode:self.indexCode+1] != '\n'):
            self.line += 1
            self.column = 0
        else:
            self.column += 1
        return car
        
    def unget_char(self, symbol):
        if symbol == '\n':
            self.line -= 1
            
        if self.indexCode > 0:
            self.indexCode -= 1
            
        self.column -= 1
        
    @staticmethod
    def print_token(running_token):
        (token, lexeme, line, column) = running_token
        
        msg = TOKEN.msg(token)
        print(f'(tk = {msg}, lex = {lexeme}, line = {line}, column = {column})')
        
    def get_token(self):
        state = 1
        symbol = self.get_char()
        lexeme = ''
        
        while symbol in ['#', ' ', '\t', '\n', '\r']:
            if symbol == '#':   # Comments
                symbol = self.get_char()
                
                while symbol != '\n':
                    symbol = self.get_char()
                    
            while symbol in [' ', '\t', '\n', '\r']:    # Whitespace
                symbol = self.get_char()
                
        lin = self.line
        col = self.column
        
        while True:
            if state == 1:
                if symbol.isalpha():
                    state = 2 # Identifiers, Reserved Words
                elif symbol.isdigit():
                    state = 3 # Integers
                elif symbol == '"':
                    state = 4 # Strings
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
                elif symbol == "=":
                    return TOKEN.equal, "=", lin, col
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
                    if self.get_char() == "=":
                        return TOKEN.equalEqual, "==", lin, col
                    else:
                        self.unget_char(symbol)
                        return TOKEN.equal, "=", lin, col
                elif symbol == "!":
                    if self.get_char() == "=":
                        return TOKEN.notEqual, "!=", lin, col
                    else:
                        self.unget_char(symbol)
                        return TOKEN.ERROR, "!", lin, col
                elif symbol == ">":
                    if self.get_char() == "=":
                        return TOKEN.greaterThanOrEqual, ">=", lin, col
                    else:
                        self.unget_char(symbol)
                        return TOKEN.greaterThan, ">", lin, col
                elif symbol == "<":
                    if self.get_char() == "=":
                        return TOKEN.lessThanOrEqual, "<=", lin, col
                    else:
                        self.unget_char(symbol)
                        return TOKEN.lessThan, "<", lin, col
                elif symbol == "eof":
                    return TOKEN.EOF, "eof", lin, col
                else:
                    lexeme += symbol
                    return TOKEN.ERROR, lexeme, lin, col
                
            elif state == 2:
                while symbol.isalnum():
                    lexeme += symbol
                    symbol = self.get_char()
                self.unget_char(symbol)
                token = TOKEN.is_terminal(lexeme)
                return token, lexeme, lin, col
                
            elif state == 3:    # Number
                if symbol.isdigit():
                    lexeme += symbol
                    state = 3
                elif symbol == '.':
                    lexeme += symbol
                    state = 31
                elif symbol.isalpha():
                    lexeme += symbol
                    return TOKEN.ERROR, lexeme, lin, col
                else:
                    self.unget_char(symbol)
                    return TOKEN.valInt, lexeme, lin, col
            elif state == 31:   # Real part of the number
                if symbol.isdigit():
                    lexeme += symbol
                    state = 32
                else:
                    self.unget_char(symbol)
                    return TOKEN.ERROR, lexeme, lin, col
            elif state == 32:
                if symbol.isdigit():
                    lexeme += symbol
                    state = 32
                elif symbol.isalpha():
                    lexeme += symbol
                    return TOKEN.ERROR, lexeme, lin, col
                else:
                    self.unget_char(symbol)
                    return TOKEN.valFloat, lexeme, lin, col
                
            elif state == 4:    # Strings
                while True:
                    if symbol == '"':
                        return TOKEN.valString, lexeme, lin, col
                    
                    if symbol in ['\n', '\0']:
                        return TOKEN.ERROR, lexeme, lin, col
                    
                    if symbol == '\\':
                        lexeme += symbol
                        symbol = self.get_char()
                        
                        if symbol in ['\n', '\0']:
                            return TOKEN.ERROR, lexeme, lin, col

                    lexeme += symbol
                    symbol = self.get_char()
                    
            elif state == 5:
                if symbol == '=':
                    lexeme += symbol
                    return TOKEN.lessThanOrEqual, lexeme, lin, col
                else:
                    self.unget_char(symbol)
                    return TOKEN.lessThan, lexeme, lin, col
                
            elif state == 6:
                if symbol == '=':
                    lexeme += symbol
                    return TOKEN.greaterThanOrEqual, lexeme, lin, col
                else:
                    self.unget_char(symbol)
                    return TOKEN.greaterThan, lexeme, lin, col
                
            elif state == 7:
                if symbol == '=':
                    lexeme += symbol
                    return TOKEN.equal, lexeme, lin, col
                else:
                    self.unget_char(symbol)
                    return TOKEN.commandAtribution, lexeme, lin, col
                
            elif state == 8:
                if symbol == '=':
                    lexeme += symbol
                    return TOKEN.notEqual, lexeme, lin, col
                else:   # If the next symbol is not an "=", then there is a "!" loose on the code
                    self.unget_char(symbol)
                    return TOKEN.ERROR, lexeme, lin, col
            else:
                print('BUG FOUND!')
            
            lexeme += symbol
            symbol = self.get_char()
            
if __name__ =='__main__':
    fileName = "test.cy"
    file = open(fileName, "r")
    lexer = LEXIC(file)
    
    read = lexer.get_token()
    while not lexer.end_of_file():
        lexer.print_token(read)
        read = lexer.get_token()
        
    file.close()