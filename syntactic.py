from lexic import TOKEN, Lexic
from semantic import Semantic

class Syntactic:
    def __init__(self):
        self.read_token = None
        self.lexic = Lexic
        self.target_name = 'target.out'

        self.semantic = Semantic(self.target_name)

    def translate(self):
        self.read_token = self.lexic.get_token()
        try:
            self.prog()
            print('Success on translation!')
        except:
            pass
        self.semantic.finish()

    def consume(self, current_token):
        (token, lexeme, lin, col) = self.read_token

        if current_token == token:
            self.read_token = self.lexic.get_token()
        else:
            message_read_token = TOKEN.message(token)
            message_current_token = TOKEN.message(current_token)

            print(f'Error on line {lin} and column {col}:')
            if token == TOKEN.ERROR:
                message = lexeme
            else:
                message = message_read_token

            print(f'Expected: {message_current_token} but got {message} instead')
            raise Exception

    def lexic_tester(self):
        self.read_token = self.lexic.get_token()
        (token, lexeme, lin, col) = self.read_token

        while token != TOKEN.EOF:
            self.lexic.print_token(self.read_token)
            self.read_token = self.lexic.get_token()
            (token, lexeme, lin, col) = self.read_token

    #Prog -> empty | Func Prog
    def prog(self):
        token = self.read_token[0]

        if token == TOKEN.VOID:
            self.func()
            self.prog()
        elif token == TOKEN.openBracket:
            self.func()
            self.prog()
        elif token == TOKEN.INT:
            self.func()
            self.prog()
        elif token == TOKEN.FLOAT:
            self.func()
            self.prog()
        elif token == TOKEN.STRING:
            self.func()
            self.prog()
        else:
            pass

    #Func -> TipoRent ident ( ListParams ) Corpo
    def func(self):
        self.tipo_ret()
        self.consume(TOKEN.ident)
        self.consume(TOKEN.openParenthesis)
        self.list_params()
        self.consume(TOKEN.closeParenthesis)
        self.corpo()

    #TipoRet --> void | Tipo
    def tipo_ret(self):
        token = self.read_token[0]

        if token == TOKEN.VOID:
            self.consume(TOKEN.VOID)
        else:
            self.tipo()

    #Tipo --> Primitivo | [Primitivo]
    def tipo(self):
    token = self.read_token[0]

    if token == TOKEN.openBracket:
        self.consume(TOKEN.openBracket)
        self.primitivo()
        self.consume(TOKEN.closeBracket)
    else:
        self.primitivo()

    #Primitivo --> int | float | string
    def primitivo(self):
        token = self.read_token[0]
    
        if token == TOKEN.INT:
            self.consume(TOKEN.INT)
        elif token == TOKEN.FLOAT:
            self.consume(TOKEN.FLOAT)
        elif token == TOKEN.STRING:
            self.consume(TOKEN.STRING)
        else:
            self.erro('Tipo primitivo esperado')

    #ListaParam --> lambda | Param OpcParam
    def lista_params(self):
        token = self.read_token[0]
    
        if token in (TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.VOID, TOKEN.openBracket):
            self.param()
            self.opc_params()
        else:
            # ε (empty), nada a fazer
            pass

