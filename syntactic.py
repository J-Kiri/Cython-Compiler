from lexic import TOKEN
from semantic import Semantic, semantic_error


class Syntactic:
    def __init__(self, lexic):
        self.read_token = None
        self.lexic = lexic
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
    #Prog -> lambda | Func Prog
    def prog(self):
        token = self.read_token[0]

        if token in (TOKEN.VOID, TOKEN.openBracket, TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING):
            self.func()
            self.prog()
        else:
            pass

    #Func -> TipoRent ident ( ListParams ) Corpo
    def func(self):
        ret_type = self.tipo_ret()
        func_token = self.read_token

        self.consume(TOKEN.ident)
        self.consume(TOKEN.openParenthesis)

        lista_params = self.lista_params()

        self.consume(TOKEN.closeParenthesis)

        self.semantic.declare_func(func_token, ret_type, lista_params)
        self.semantic.enter_function_scope(func_token[1])

        self.corpo()

    #TipoRet --> void | Tipo
    def tipo_ret(self):
        token = self.read_token[0]

        if token == TOKEN.VOID:
            self.consume(TOKEN.VOID)

            return "void", False  # Void, it's not a list
        else:
            return self.tipo()

    # ListaParam --> lambda | Param OpcParam
    def lista_params(self):
        token = self.read_token[0]

        if token in (TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.VOID, TOKEN.openBracket):
            param = self.param()
            others = self.opc_params()

            return [param] + others
        else:
            return []

    #OpcParams --> lambda |, Param OpcParams
    def opc_params(self):
        token = self.read_token[0]

        if token == TOKEN.comma:
            self.consume(TOKEN.comma)
            param = self.param()
            others = self.opc_params()

            return [param] + others
        else:
            return []

    #Param --> Tipo ident
    def param(self):
        def_type = self.tipo()
        token_id = self.read_token
        self.consume(TOKEN.ident)

        return token_id, def_type

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
            prim = self.primitivo()
            self.consume(TOKEN.closeBracket)

            return prim, True
        else:
            return self.primitivo(), False

    #Primitivo --> int | float | string
    def primitivo(self):
        token = self.read_token[0]
    
        if token == TOKEN.INT:
            self.consume(TOKEN.INT)
            return "int"
        elif token == TOKEN.FLOAT:
            self.consume(TOKEN.FLOAT)
            return "float"
        elif token == TOKEN.STRING:
            self.consume(TOKEN.STRING)
            return "string"
        else:
            semantic_error(token, token + " type undefined!")
        pass

    #Declara --> Tipo ListaVar ;
    def declara(self):
        def_type = self.tipo()
        self.lista_var(def_type)
        self.consume(TOKEN.semiColon)

    #ListaVar --> Var RestoListaVar
    def lista_var(self, def_type):
        self.var(def_type)
        self.resto_lista_var(def_type)

    #RestoListaVar --> lambda | , ListaVar
    def resto_lista_var(self, def_type):
        token = self.read_token[0]

        if token == TOKEN.comma:
            self.consume(TOKEN.comma)
            self.lista_var(def_type)
        else:
            pass

    #Var --> ident OpcValor
    def var(self, def_type):
        ident_token = self.read_token
        self.consume(TOKEN.ident)

        self.semantic.declare_var(ident_token, def_type)

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

    #ComAtrib --> ident PosicaoOpc = Exp ;
    def com_atrib(self):
        ident_token = self.read_token
        name = ident_token[1]
        self.consume(TOKEN.ident)

        is_list = False
        if self.read_token[0] == TOKEN.openBracket:
            self.posicao_opc()
            is_list = True

        self.consume(TOKEN.equal)
        expression_type = self.exp()

        var_type = self.semantic.get_var_info(name, ident_token)

        if var_type[0] != expression_type:
            semantic_error(ident_token, f"Cannot assign {expression_type} to variable '{name}' of type {var_type[0]}")

        self.consume(TOKEN.semiColon)

    #PosicaoOpc --> lambda | [ Exp ]ComIf --> if ( Exp ) Comando OpcElse
    def posicao_opc(self):
        token = self.read_token[0]

        if token == TOKEN.openBracket:
            self.consume(TOKEN.openBracket)
            self.exp()
            self.consume(TOKEN.closeBracket)
        else:
            pass

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
            pass

    #ComBloco --> { ListaComando }
    def com_bloco(self):
        self.consume(TOKEN.openBraces)
        self.lista_comando()
        self.consume(TOKEN.closeBraces)

    #### EXPRESSOES (etapas da construcao da gramatica )
    #Folha --> ValPrim | ident Recorte | ident ( ListaArgs ) | ( Exp ) | ValLista
    def folha(self):
        token = self.read_token[0]

        if token in (TOKEN.valInt, TOKEN.valFloat, TOKEN.valString):
            return self.val_prim()

        elif token == TOKEN.ident:
            ident_token = self.read_token
            name = ident_token[1]
            self.consume(TOKEN.ident)

            if self.read_token[0] == TOKEN.openBracket:
                tipo = self.semantic.get_var_info(name, ident_token)
                if not tipo[1]:  # tipo[1] indica se é lista
                    semantic_error(ident_token, f"Variable '{name}' is not a list")
                self.consume(TOKEN.openBracket)
                self.exp()
                self.consume(TOKEN.closeBracket)
                return tipo[0]  # retorno do tipo do conteúdo da lista

            elif self.read_token[0] == TOKEN.openParenthesis:
                self.consume(TOKEN.openParenthesis)
                arg_types = self.lista_args()
                self.consume(TOKEN.closeParenthesis)

                ret_type, param_list, _ = self.semantic.get_func_info(name, ident_token)

                if len(arg_types) != len(param_list):
                    semantic_error(ident_token,
                                   f"Function '{name}' expects {len(param_list)} args, got {len(arg_types)}")

                for i, ((_, (expected, _)), got) in enumerate(zip(param_list, arg_types)):
                    if expected != got:
                        semantic_error(ident_token, f"Arg {i + 1} of '{name}' expected {expected}, got {got}")

                return ret_type[0]

            else:
                tipo = self.semantic.get_var_info(name, ident_token)
                return tipo[0]

        elif token == TOKEN.openParenthesis:
            self.consume(TOKEN.openParenthesis)
            def_type = self.exp()
            self.consume(TOKEN.closeParenthesis)
            return def_type

        elif token == TOKEN.openBracket:
            return self.val_lista()

        else:
            semantic_error(self.read_token, "Invalid expression")

    #ValPrim --> valint | valfloat | valstring
    def val_prim(self):
        token = self.read_token[0]

        if token == TOKEN.valInt:
            self.consume(TOKEN.valInt)
            return "int"
        elif token == TOKEN.valFloat:
            self.consume(TOKEN.valFloat)
            return "float"
        elif token == TOKEN.valString:
            self.consume(TOKEN.valString)
            return "string"
        return None

    #ValLista --> [ ListaExp ]
    def val_lista(self):
        self.consume(TOKEN.openBracket)

        element_types = self.lista_exp()
        self.consume(TOKEN.closeBracket)

        if len(element_types) == 0:
            return "int"
        else:
            return element_types[0]

    #Recorte --> lambda | [ OpcInt Recorte2 ]
    def recorte(self):
        if self.read_token[0] == TOKEN.openBracket:
            self.consume(TOKEN.openBracket)
            self.opc_int()
            self.recorte2()
            self.consume(TOKEN.closeBracket)
            return "int"
        else:
            pass

    #Recorte2 --> lambda | : OpcInt
    def recorte2(self):
        if self.read_token[0] == TOKEN.colon:
            self.consume(TOKEN.colon)
            self.opc_int()
        else:
            pass

    #OpcInt --> lambda | Exp
    def opc_int(self):
        if self.read_token[0] in (
                TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
                TOKEN.ident, TOKEN.openParenthesis, TOKEN.openBracket,
                TOKEN.NOT, TOKEN.plus, TOKEN.minus
        ):
            return self.exp()
        else:
            pass

    #ListaArgs --> lambda | Exp RestoListaArgs
    def lista_args(self):
        types = []

        if self.read_token[0] in (
                TOKEN.NOT, TOKEN.plus, TOKEN.minus,
                TOKEN.ident, TOKEN.openParenthesis,
                TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
                TOKEN.openBracket
        ):
            def_type = self.exp()
            types.append(def_type)
            types += self.resto_lista_args()

            return types
        else:
            return []

    #RestoListaArgs --> lambda | , Exp RestoListaArgs
    def resto_lista_args(self):
        types = []

        if self.read_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            def_type = self.exp()
            types.append(def_type)
            types += self.resto_lista_args()

        return types

    #ListaExp --> LAMBDA | Exp OpcListaExp
    def lista_exp(self):
        types = []

        if self.read_token[0] in (
                TOKEN.NOT, TOKEN.plus, TOKEN.minus,
                TOKEN.ident, TOKEN.openParenthesis,
                TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
                TOKEN.openBracket
        ):
            first_type = self.exp()
            types.append(first_type)
            types += self.opc_lista_exp(first_type)

        return types

    #OpcListaExp --> LAMBDA | , Exp OpcListaExp
    def opc_lista_exp(self, expected_type):
        types = []

        if self.read_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            def_type = self.exp()

            if def_type != expected_type:
                semantic_error(self.read_token, f"List elements must have same type: Expected {expected_type}, got {def_type}")

            types.append(def_type)
            types += self.opc_lista_exp(expected_type)
        else:
            pass

        return types

    #Uno --> + Uno | - Uno | Folha
    def uno(self):
        token = self.read_token[0]

        if token == TOKEN.plus:
            self.consume(TOKEN.plus)
            return self.uno()
        elif token == TOKEN.minus:
            self.consume(TOKEN.minus)
            return self.uno()
        else:
            return self.folha()

    #Mult --> Uno RestoMult
    def mult(self):
        def_type = self.uno()
        return self.resto_mult(def_type)

    #RestoMult --> lambda | * Uno RestoMult | / Uno RestoMult | mod Uno RestoMult | div Uno RestoMult
    def resto_mult(self, left_type):
        token = self.read_token[0]

        if token in (TOKEN.star, TOKEN.slash, TOKEN.MOD, TOKEN.DIV):
            self.consume(token)
            right_type = self.uno()

            if left_type != right_type:
                semantic_error(self.read_token, f"Type mismatch in multiplication/division: {left_type} and {right_type}")

            return self.resto_mult(left_type)
        else:
            return left_type

    #Soma --> Mult RestoSoma
    def soma(self):
        def_type = self.mult()
        return self.resto_soma(def_type)

    #RestoSoma --> lambda | + Mult RestoSoma | - Mult RestoSoma
    def resto_soma(self, left_type):
        token = self.read_token[0]

        if token == TOKEN.plus or token == TOKEN.minus:
            self.consume(token)
            right_type = self.mult()

            if left_type != right_type:
                semantic_error(self.read_token, f"Type mismatch in addition/subtraction: {left_type} and {right_type}")

            return self.resto_soma(left_type)
        else:
            return left_type

    #Rel --> Soma RestoRel
    def rel(self):
        def_type = self.soma()
        return self.resto_rel(def_type)

    #RestoRel --> lambda | == Soma | != Soma | <= Soma | >= Soma | > Soma | < Soma
    def resto_rel(self, left_type):
        token = self.read_token[0]

        operadores = {
            TOKEN.equalEqual, TOKEN.notEqual, TOKEN.lessThanOrEqual,
            TOKEN.greaterThanOrEqual, TOKEN.lessThan, TOKEN.greaterThan
        }

        if token in operadores:
            self.consume(token)
            right_type = self.soma()

            if left_type != right_type:
                semantic_error(self.read_token,
                               f"Incompatible types in relational operation: {left_type} and {right_type}")

            return self.resto_rel("int")  # Comparações sempre retornam int (boolean)
        else:
            return left_type

    #Nao --> not Nao | Rel
    def nao(self):
        if self.read_token[0] == TOKEN.NOT:
            self.consume(TOKEN.NOT)
            def_type = self.nao()

            if type != "int":
                semantic_error(self.read_token, f"'not' operation requires boolean (int), got {def_type}")
                return None
        else:
            return self.rel()

        return None

    #Junc --> Nao RestoJunc
    def junc(self):
        tipo = self.nao()
        return self.resto_junc(tipo)

    #RestoJunc --> lambda | and Nao RestoJunc
    def resto_junc(self, left_type):
        if self.read_token[0] == TOKEN.AND:
            self.consume(TOKEN.AND)
            right_type = self.nao()

            if left_type != "int" or right_type != "int":
                semantic_error(self.read_token, f"Logical 'and' requires boolean (int) operands")

            return self.resto_junc("int")
        else:
            return left_type

    #Exp --> Junc RestoExp
    def exp(self):
        tipo = self.junc()
        return self.resto_exp(tipo)

    #RestoExp --> lambda | or Junc RestoExp
    def resto_exp(self, left_type):
        if self.read_token[0] == TOKEN.OR:
            self.consume(TOKEN.OR)
            right_type = self.junc()

            if left_type != "int" or right_type != "int":
                semantic_error(self.read_token, f"Logical 'or' requires boolean (int) operands")

            return self.resto_exp("int")
        else:
            return left_type