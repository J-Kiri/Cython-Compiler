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

    # --- programa
    #Prog -> empty | Func Prog
    def prog(self):
        token = self.read_token[0]

        if token in (TOKEN.VOID, TOKEN.openBracket, TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING):
            self.func()
            self.prog()
        else:
            pass

    #Func -> TipoRent ident ( ListParams ) Corpo
    def func(self):
        self.tipo_ret()
        self.consume(TOKEN.ident)
        self.consume(TOKEN.openParenthesis)
        self.lista_params()
        self.consume(TOKEN.closeParenthesis)
        self.corpo()

    #TipoRet --> void | Tipo
    def tipo_ret(self):
        token = self.read_token[0]

        if token == TOKEN.VOID:
            self.consume(TOKEN.VOID)
        else:
            self.tipo()

    # ListaParam --> lambda | Param OpcParam
    def lista_params(self):
        token = self.read_token[0]

        if token in (TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.VOID, TOKEN.openBracket):
            self.param()
            self.opc_params()
        else:
            pass

    #OpcParams --> lambda |, Param OpcParams
    def opc_params(self):
        token = self.read_token[0]

        if token == TOKEN.comma:
            self.consume(TOKEN.comma)
            self.param()
            self.opc_params()
        else:
            pass

    #Param --> Tipo ident
    def param(self):
        self.tipo()
        self.consume(TOKEN.ident)

    #Corpo --> { ListaDeclara ListaComando }
    def corpo(self):
        self.consume(TOKEN.openBraces)
        self.lista_declara()
        self.lista_comando()
        self.consume(TOKEN.closeBraces)

    #ListaDeclara --> lambda | Declara ListaDeclara
    def lista_declara(self):
        token = self.read_token[0]

        if token in (TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.VOID, TOKEN.openBracket):
            self.declara()
            self.lista_declara()
        else:
            pass

    #ListaComando --> lambda | Comando ListaComando
    def lista_comando(self):
        token = self.read_token[0]

        if token in (
                TOKEN.ident, TOKEN.IF, TOKEN.WHILE, TOKEN.FOR, TOKEN.FOREACH,
                TOKEN.RETURN, TOKEN.CONTINUE, TOKEN.BREAK,
                TOKEN.READ, TOKEN.WRITE, TOKEN.openBraces
        ):
            self.comando()
            self.lista_comando()
        else:
            pass

    # --- declaracoes e tipos
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
        # else:
            # self.erro('Tipo primitivo esperado')

    #Declara --> Tipo ListaVar ;
    def declara(self):
        self.tipo()
        self.lista_var()
        self.consume(TOKEN.semiColon)

    #ListaVar --> Var RestoListaVar
    def lista_var(self):
        self.var()
        self.resto_lista_var()

    #RestoListaVar --> lambda | , ListaVar
    def resto_lista_var(self):
        token = self.read_token[0]

        if token == TOKEN.comma:
            self.consume(TOKEN.comma)
            self.lista_var()
        else:
            pass

    #Var --> ident OpcValor
    def var(self):
        self.consume(TOKEN.ident)
        self.opc_valor()

    #OpcValor --> lambda | = Exp
    def opc_valor(self):
        token = self.read_token[0]

        if token == TOKEN.equal:
            self.consume(TOKEN.equal)
            self.exp()
        else:
            pass

    #Comando --> ComAtrib | ComIf | ComFor | ComWhile | ComReturn | ComContinue | ComBreak | ComEntrada | ComSaida | ComBloco
    def comando(self):
        token = self.read_token[0]

        if token == TOKEN.ident:
            self.com_atrib()
        elif token == TOKEN.IF:
            self.com_if()
        elif token == TOKEN.FOR:
            self.com_for()
        elif token == TOKEN.FOREACH:
            self.com_for()
        elif token == TOKEN.WHILE:
            self.com_while()
        elif token == TOKEN.RETURN:
            self.com_return()
        elif token == TOKEN.CONTINUE:
            self.com_continue()
        elif token == TOKEN.BREAK:
            self.com_break()
        elif token == TOKEN.READ:
            self.com_entrada()
        elif token == TOKEN.WRITE:
            self.com_saida()
        elif token == TOKEN.openBraces:
            self.com_bloco()
        else:
            self.erro('Comando esperado')

    #ComAtrib --> ident = Exp ;
    def com_atrib(self):
        self.consume(TOKEN.ident)
        self.consume(TOKEN.equal)
        self.exp()
        self.consume(TOKEN.semiColon)

    #ComIf --> if ( Exp ) Comando OpcElse
    def com_if(self):
        self.consume(TOKEN.IF)
        self.consume(TOKEN.openParenthesis)
        self.exp()
        self.consume(TOKEN.closeParenthesis)
        self.comando()
        self.opc_else()

    #OpcElse --> lambda | else Comando | elif ( Exp ) Comando OpcElse
    def opc_else(self):
        token = self.read_token[0]

        if token == TOKEN.ELSE:
            self.consume(TOKEN.ELSE)
            self.comando()
        elif token == TOKEN.ELIF:
            self.consume(TOKEN.ELIF)
            self.consume(TOKEN.openParenthesis)
            self.exp()
            self.consume(TOKEN.closeParenthesis)
            self.comando()
            self.opc_else()
        else:
            pass

    #ComFor --> for ( ident = Exp ; Exp ; ident = Exp ) Comando | foreach ident = Exp : Comando
    def com_for(self):
        token = self.read_token[0]

        if token == TOKEN.FOR:
            self.consume(TOKEN.FOR)
            self.consume(TOKEN.openParenthesis)
            self.consume(TOKEN.ident)
            self.consume(TOKEN.equal)
            self.exp()
            self.consume(TOKEN.semiColon)
            self.exp()
            self.consume(TOKEN.semiColon)
            self.consume(TOKEN.ident)
            self.consume(TOKEN.equal)
            self.exp()
            self.consume(TOKEN.closeParenthesis)
            self.comando()
        elif token == TOKEN.FOREACH:
            self.consume(TOKEN.FOREACH)
            self.consume(TOKEN.ident)
            self.consume(TOKEN.equal)
            self.exp()
            self.consume(TOKEN.colon)
            self.comando()

    #ComWhile --> while ( Exp ) Comando
    def com_while(self):
        self.consume(TOKEN.WHILE)
        self.consume(TOKEN.openParenthesis)
        self.exp()
        self.consume(TOKEN.closeParenthesis)
        self.comando()

    #ComReturn --> return OpcRet ;
    def com_return(self):
        self.consume(TOKEN.RETURN)
        self.opc_ret()
        self.consume(TOKEN.semiColon)

    #OpcRet --> lambda | Exp
    def opc_ret(self):
        if self.read_token[0] in (
                TOKEN.NOT, TOKEN.plus, TOKEN.minus,
                TOKEN.ident, TOKEN.openParenthesis,
                TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
                TOKEN.openBracket
        ):
            self.exp()
        else:
            pass

    #ComContinue --> continue ;
    def com_continue(self):
        self.consume(TOKEN.CONTINUE)
        self.consume(TOKEN.semiColon)

    #ComBreak --> break ;
    def com_break(self):
        self.consume(TOKEN.BREAK)
        self.consume(TOKEN.semiColon)

    #ComEntrada --> read ( ident ) ;
    def com_entrada(self):
        self.consume(TOKEN.READ)
        self.consume(TOKEN.openParenthesis)
        self.consume(TOKEN.ident)
        self.consume(TOKEN.closeParenthesis)
        self.consume(TOKEN.semiColon)

    #ComSaida --> write ( ListaOut ) ;
    def com_saida(self):
        self.consume(TOKEN.WRITE)
        self.consume(TOKEN.openParenthesis)
        self.lista_out()
        self.consume(TOKEN.closeParenthesis)
        self.consume(TOKEN.semiColon)

    #ListaOut --> Exp RestoListaOut
    def lista_out(self):
        self.exp()
        self.resto_lista_out()

    #RestoListaOut --> lambda | , ListaOut
    def resto_lista_out(self):
        if self.read_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            self.lista_out()
        else:
            # λ
            pass

    #ComBloco --> { ListaComando }
    def com_bloco(self):
        self.consume(TOKEN.openBraces)
        self.lista_comando()
        self.consume(TOKEN.closeBraces)
