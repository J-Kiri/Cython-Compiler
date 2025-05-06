from ttoken import TOKEN


def semantic_error(current_token, message):
    (token, lexeme, lin, col) = current_token

    print(f'Error on line {lin}, column {col}: {message}')
    raise Exception


class Semantic:
    def __init__(self, target_name):
        self.symbolsTable = dict()
        self.target = open(target_name, "wt")

    def finish(self):
        self.target.close()

    def generate(self, code):
        self.target.write(code + "\n")

    def declare(self, token):
        if token[1] in self.symbolsTable:
            message = f'Variable {token[1]} redeclared'
            semantic_error(token, message)
        else:
            self.symbolsTable[token[1]] = token[0]