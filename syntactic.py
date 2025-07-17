from lexic import TOKEN
from semantic import Semantic, semantic_error


class Syntactic:
    def __init__(self, lexic):
        self.lexic = lexic
        self.current_token = None
        self.semantic = Semantic('target.out')
        self.advance()

    def advance(self):
        self.current_token = self.lexic.get_token()

    def consume(self, expected_token):
        if self.current_token[0] == expected_token:
            self.advance()
        else:
            token, lexeme, line, col = self.current_token
            expected_msg = TOKEN.message(expected_token)
            actual_msg = lexeme if token == TOKEN.ERROR else TOKEN.message(token)
            print(f'Error at line {line}, column {col}: Expected {expected_msg}, got {actual_msg}')
            raise Exception("Syntax error")

    def parse(self):
        self.prog()
        print("Parsing completed successfully!")

    def peek_char(self):
        """Retorna o próximo caractere sem consumi-lo"""
        return self.lexic.peek_char()

    # Prog -> LAMBDA | Func Prog
    def prog(self):
        while self.current_token[0] != TOKEN.EOF:
            if self.current_token[0] in {TOKEN.VOID, TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.openBracket}:
                self.func()
            else:
                break

    # Func -> TipoRet ident ( ListaParam ) Corpo
    def func(self):
        ret_type = self.tipo_ret()
        func_token = self.current_token
        self.consume(TOKEN.ident)
        self.consume(TOKEN.openParenthesis)

        params = self.lista_param()

        self.consume(TOKEN.closeParenthesis)

        # Registrar função na tabela de símbolos
        self.semantic.declare_func(func_token, ret_type, params)
        self.semantic.enter_function_scope(func_token[1])

        self.corpo()

    # TipoRet -> void | Tipo
    def tipo_ret(self):
        if self.current_token[0] == TOKEN.VOID:
            self.consume(TOKEN.VOID)
            return ("void", False)
        else:
            return self.tipo()

    # ListaParam -> LAMBDA | Param OpcParams
    def lista_param(self):
        params = []
        if self.current_token[0] in {TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.openBracket}:
            params.append(self.param())
            params.extend(self.opc_params())
        return params

    # OpcParams -> LAMBDA | , Param OpcParams
    def opc_params(self):
        params = []
        if self.current_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            params.append(self.param())
            params.extend(self.opc_params())
        return params

    # Param -> Tipo ident
    def param(self):
        param_type = self.tipo()
        param_token = self.current_token
        self.consume(TOKEN.ident)
        return (param_token, param_type)

    # Corpo -> { ListaDeclara ListaComando }
    def corpo(self):
        self.consume(TOKEN.openBraces)
        self.lista_declara()
        self.lista_comando()
        self.consume(TOKEN.closeBraces)

    # ListaDeclara -> LAMBDA | Declara ListaDeclara
    def lista_declara(self):
        if self.current_token[0] in {TOKEN.INT, TOKEN.FLOAT, TOKEN.STRING, TOKEN.openBracket}:
            self.declara()
            self.lista_declara()

    # Declara -> Tipo ListaVar ;
    def declara(self):
        var_type = self.tipo()
        self.lista_var(var_type)
        self.consume(TOKEN.semiColon)

    # ListaVar -> Var RestoListaVar
    def lista_var(self, var_type):
        self.var(var_type)
        self.resto_lista_var(var_type)

    # RestoListaVar -> LAMBDA | , ListaVar
    def resto_lista_var(self, var_type):
        if self.current_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            self.lista_var(var_type)

    # Var -> ident OpcValor
    def var(self, var_type):
        ident_token = self.current_token
        self.consume(TOKEN.ident)
        self.semantic.declare_var(ident_token, var_type)

        # Opcional: inicialização na declaração
        if self.current_token[0] == TOKEN.equal:
            self.opc_valor(var_type)

    # OpcValor -> LAMBDA | = Exp
    def opc_valor(self, var_type):
        if self.current_token[0] == TOKEN.equal:
            self.consume(TOKEN.equal)
            expr_type = self.exp()

            # Verificar compatibilidade de tipos
            if expr_type != var_type:
                semantic_error(self.current_token,
                               f"Type mismatch in declaration: expected {var_type}, got {expr_type}")

    # Tipo -> Primitivo | [ Primitivo ]
    def tipo(self):
        if self.current_token[0] == TOKEN.openBracket:
            self.consume(TOKEN.openBracket)
            prim = self.primitivo()
            self.consume(TOKEN.closeBracket)
            return (prim, True)
        else:
            return (self.primitivo(), False)

    # Primitivo -> int | float | string
    def primitivo(self):
        if self.current_token[0] == TOKEN.INT:
            self.consume(TOKEN.INT)
            return "int"
        elif self.current_token[0] == TOKEN.FLOAT:
            self.consume(TOKEN.FLOAT)
            return "float"
        elif self.current_token[0] == TOKEN.STRING:
            self.consume(TOKEN.STRING)
            return "string"
        else:
            semantic_error(self.current_token, "Expected primitive type (int, float or string)")

    # ListaComando -> LAMBDA | Comando ListaComando
    def lista_comando(self):
        while self.current_token[0] in {
            TOKEN.ident, TOKEN.IF, TOKEN.FOR, TOKEN.FOREACH, TOKEN.WHILE,
            TOKEN.RETURN, TOKEN.CONTINUE, TOKEN.BREAK,
            TOKEN.READ, TOKEN.WRITE, TOKEN.openBraces
        }:
            self.comando()

    # Comando -> ComAtrib | ComIf | ComFor | ComWhile | ComReturn |
    #            ComContinue | ComBreak | ComEntrada | ComSaida | ComBloco
    def comando(self):
        token = self.current_token[0]

        if token == TOKEN.ident:
            self.com_atrib()
        elif token == TOKEN.IF:
            self.com_if()
        elif token == TOKEN.FOR or token == TOKEN.FOREACH:
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
            semantic_error(self.current_token, "Invalid command")

    # ComAtrib -> ident PosicaoOpc = Exp ;
    def com_atrib(self):
        ident_token = self.current_token
        ident_name = ident_token[1]
        self.consume(TOKEN.ident)

        is_list_access = False
        if self.current_token[0] == TOKEN.openBracket:
            self.consume(TOKEN.openBracket)
            tipo = self.semantic.get_var_info(ident_name, ident_token)

            if not tipo[1]:
                semantic_error(ident_token, f"Variable '{ident_name}' is not a list")

            # Consome o índice
            index_type = self.exp()
            if index_type != ("int", False):
                semantic_error(self.current_token, "List index must be integer")

            self.consume(TOKEN.closeBracket)
            is_list_access = True

        self.consume(TOKEN.equal)
        expr_type = self.exp()
        self.consume(TOKEN.semiColon)

        var_type = self.semantic.get_var_info(ident_name, ident_token)

        if is_list_access:
            # Verifica se o tipo do elemento é compatível
            if expr_type[0] != var_type[0] or expr_type[1]:
                semantic_error(ident_token,
                               f"Cannot assign {expr_type[0]}{'[]' if expr_type[1] else ''} " +
                               f"to element of list '{ident_name}' of type {var_type[0]}")
        else:
            # Verificação normal de atribuição
            if expr_type != var_type:
                semantic_error(ident_token,
                               f"Cannot assign {expr_type[0]}{'[]' if expr_type[1] else ''} " +
                               f"to variable '{ident_name}' of type " +
                               f"{var_type[0]}{'[]' if var_type[1] else ''}")

    # PosicaoOpc -> LAMBDA | [ Exp ]
    def posicao_opc(self):
        if self.current_token[0] == TOKEN.openBracket:
            self.consume(TOKEN.openBracket)
            self.exp()
            self.consume(TOKEN.closeBracket)

    # ComIf -> if ( Exp ) Comando OpcElse
    def com_if(self):
        self.consume(TOKEN.IF)
        self.consume(TOKEN.openParenthesis)
        expr_type = self.exp()

        # Verificar se a expressão é booleana
        if expr_type != ("int", False):
            semantic_error(self.current_token, "Condition in 'if' must be boolean (int)")

        self.consume(TOKEN.closeParenthesis)
        self.comando()
        self.opc_else()

    # OpcElse -> LAMBDA | else Comando | elif ( Exp ) Comando OpcElse
    def opc_else(self):
        if self.current_token[0] == TOKEN.ELSE:
            self.consume(TOKEN.ELSE)
            self.comando()
        elif self.current_token[0] == TOKEN.ELIF:
            self.consume(TOKEN.ELIF)
            self.consume(TOKEN.openParenthesis)
            expr_type = self.exp()

            if expr_type != ("int", False):
                semantic_error(self.current_token, "Condition in 'elif' must be boolean (int)")

            self.consume(TOKEN.closeParenthesis)
            self.comando()
            self.opc_else()

    # ComFor -> for ( ident = Exp ; Exp ; ident = Exp ) Comando | foreach ident = Exp : Comando
    def com_for(self):
        token = self.current_token[0]

        if token == TOKEN.FOREACH:
            # Implementação do foreach
            self.consume(TOKEN.FOREACH)

            # Consome o identificador (sem tipo declarado)
            ident_token = self.current_token
            self.consume(TOKEN.ident)

            # Declara a variável de iteração como int (assumindo listas de int)
            self.semantic.declare_var(ident_token, ("int", False))

            self.consume(TOKEN.equal)
            expr_type = self.exp()

            if not expr_type[1]:  # Verifica se é uma lista
                semantic_error(self.current_token, "Foreach loop requires a list expression")

            self.consume(TOKEN.colon)

            # Tratamento do corpo do foreach
            if self.current_token[0] == TOKEN.openBraces:
                self.com_bloco()  # Bloco com { }
            else:
                self.comando()  # Comando único

        elif token == TOKEN.FOR:
            # Implementação do for tradicional
            self.consume(TOKEN.FOR)
            self.consume(TOKEN.openParenthesis)

            # Inicialização
            if self.current_token[0] == TOKEN.ident:
                init_token = self.current_token
                self.consume(TOKEN.ident)
                self.consume(TOKEN.equal)
                init_expr_type = self.exp()

                # Verifica se a variável existe ou declara nova?
                if not self.semantic.is_var(init_token[1]):
                    self.semantic.declare_var(init_token, ("int", False))

            self.consume(TOKEN.semiColon)

            # Condição
            cond_type = self.exp()
            if cond_type != ("int", False):
                semantic_error(self.current_token, "For condition must be boolean (int)")

            self.consume(TOKEN.semiColon)

            # Incremento
            if self.current_token[0] == TOKEN.ident:
                inc_token = self.current_token
                self.consume(TOKEN.ident)
                self.consume(TOKEN.equal)
                inc_expr_type = self.exp()

                # Verifica tipo do incremento
                var_type = self.semantic.get_var_info(inc_token[1], inc_token)
                if inc_expr_type != var_type:
                    semantic_error(inc_token, f"Type mismatch in for increment")

            self.consume(TOKEN.closeParenthesis)

            # Corpo do for
            if self.current_token[0] == TOKEN.openBraces:
                self.com_bloco()
            else:
                self.comando()
        else:
            semantic_error(self.current_token, "Expected 'for' or 'foreach'")

    # ComWhile -> while ( Exp ) Comando
    def com_while(self):
        self.consume(TOKEN.WHILE)
        self.consume(TOKEN.openParenthesis)
        expr_type = self.exp()

        if expr_type != ("int", False):
            semantic_error(self.current_token, "While condition must be boolean (int)")

        self.consume(TOKEN.closeParenthesis)
        self.comando()

    # ComReturn -> return OpcRet ;
    def com_return(self):
        self.consume(TOKEN.RETURN)
        self.opc_ret()
        self.consume(TOKEN.semiColon)

    # OpcRet -> LAMBDA | Exp
    def opc_ret(self):
        if self.current_token[0] in {
            TOKEN.ident, TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
            TOKEN.openParenthesis, TOKEN.openBracket, TOKEN.NOT,
            TOKEN.plus, TOKEN.minus
        }:
            return self.exp()

    def opc_int(self):
        if self.current_token[0] in {
            TOKEN.valInt, TOKEN.ident,
            TOKEN.openParenthesis, TOKEN.NOT,
            TOKEN.plus, TOKEN.minus
        }:
            expr_type = self.exp()
            if expr_type != ("int", False):
                semantic_error(self.current_token, "Slice indices must be integers")
            return expr_type
        return None  # Para casos onde o índice é omitido (como [:] ou [inicio:])

    # ComContinue -> continue ;
    def com_continue(self):
        self.consume(TOKEN.CONTINUE)
        self.consume(TOKEN.semiColon)

    # ComBreak -> break ;
    def com_break(self):
        self.consume(TOKEN.BREAK)
        self.consume(TOKEN.semiColon)

    # ComEntrada -> read ( ident ) ;
    def com_entrada(self):
        self.consume(TOKEN.READ)
        self.consume(TOKEN.openParenthesis)
        ident_token = self.current_token
        self.consume(TOKEN.ident)
        self.consume(TOKEN.closeParenthesis)
        self.consume(TOKEN.semiColon)

        # Verificar se a variável existe
        self.semantic.get_var_info(ident_token[1], ident_token)

    # ComSaida -> write ( ListaOut ) ;
    def com_saida(self):
        self.consume(TOKEN.WRITE)
        self.consume(TOKEN.openParenthesis)
        self.lista_out()
        self.consume(TOKEN.closeParenthesis)
        self.consume(TOKEN.semiColon)

    # ListaOut -> Exp RestoListaOut
    def lista_out(self):
        self.exp()
        self.resto_lista_out()

    # RestoListaOut -> LAMBDA | , ListaOut
    def resto_lista_out(self):
        if self.current_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            self.lista_out()

    # ComBloco -> { ListaComando }
    def com_bloco(self):
        self.consume(TOKEN.openBraces)
        self.lista_comando()
        self.consume(TOKEN.closeBraces)

    # Expressões --------------------------------------------------

    # Exp -> Junc RestoExp
    def exp(self):
        left_type = self.junc()
        return self.resto_exp(left_type)

    # RestoExp -> LAMBDA | or Junc RestoExp
    def resto_exp(self, left_type):
        if self.current_token[0] == TOKEN.OR:
            self.consume(TOKEN.OR)
            right_type = self.junc()

            if left_type != ("int", False) or right_type != ("int", False):
                semantic_error(self.current_token, "Logical 'or' requires boolean (int) operands")

            return self.resto_exp(("int", False))
        return left_type

    # Junc -> Nao RestoJunc
    def junc(self):
        left_type = self.nao()
        return self.resto_junc(left_type)

    # RestoJunc -> LAMBDA | and Nao RestoJunc
    def resto_junc(self, left_type):
        if self.current_token[0] == TOKEN.AND:
            self.consume(TOKEN.AND)
            right_type = self.nao()

            if left_type != ("int", False) or right_type != ("int", False):
                semantic_error(self.current_token, "Logical 'and' requires boolean (int) operands")

            return self.resto_junc(("int", False))
        return left_type

    # Nao -> not Nao | Rel
    def nao(self):
        if self.current_token[0] == TOKEN.NOT:
            self.consume(TOKEN.NOT)
            expr_type = self.nao()

            if expr_type != ("int", False):
                semantic_error(self.current_token, "'not' operation requires boolean (int)")

            return ("int", False)
        else:
            return self.rel()

    # Rel -> Soma RestoRel
    def rel(self):
        left_type = self.soma()
        return self.resto_rel(left_type)

    # RestoRel -> LAMBDA | == Soma | != Soma | <= Soma | >= Soma | > Soma | < Soma
    def resto_rel(self, left_type):
        if self.current_token[0] in {
            TOKEN.equalEqual, TOKEN.notEqual,
            TOKEN.lessThanOrEqual, TOKEN.greaterThanOrEqual,
            TOKEN.lessThan, TOKEN.greaterThan
        }:
            op = self.current_token[0]
            self.consume(op)
            right_type = self.soma()

            if left_type != right_type or left_type[1] or right_type[1]:
                semantic_error(self.current_token,
                               f"Relational operation '{TOKEN.message(op)}' requires operands of same non-list type")

            return ("int", False)  # Resultado de comparação é sempre booleano (int)
        return left_type

    # Soma -> Mult RestoSoma
    def soma(self):
        left_type = self.mult()
        return self.resto_soma(left_type)

    # RestoSoma -> LAMBDA | + Mult RestoSoma | - Mult RestoSoma
    def resto_soma(self, left_type):
        if self.current_token[0] in {TOKEN.plus, TOKEN.minus}:
            op_token = self.current_token
            op = op_token[0]
            self.consume(op)
            right_type = self.mult()

            # Operador de adição (+)
            if op == TOKEN.plus:
                # Caso 1: Concatenação de listas do mesmo tipo
                if left_type[1] and right_type[1]:
                    if left_type[0] == right_type[0]:
                        return (left_type[0], True)  # Retorna tipo da lista concatenada
                    else:
                        semantic_error(op_token,
                                       f"Cannot concatenate lists of different types: "
                                       f"{left_type[0]}[] and {right_type[0]}[]")

                # Caso 2: Operação aritmética normal
                elif not left_type[1] and not right_type[1]:
                    if left_type[0] == right_type[0] and left_type[0] in {'int', 'float'}:
                        return left_type
                    else:
                        semantic_error(op_token,
                                       f"Cannot add non-numeric or different types: "
                                       f"{left_type[0]} and {right_type[0]}")

                # Caso 3: Operação inválida entre lista e não-lista
                else:
                    semantic_error(op_token,
                                   f"Cannot add list and non-list: "
                                   f"{left_type[0]}{'[]' if left_type[1] else ''} + "
                                   f"{right_type[0]}{'[]' if right_type[1] else ''}")

            # Operador de subtração (-)
            elif op == TOKEN.minus:
                # Subtração só é permitida para tipos numéricos não-lista
                if left_type[1] or right_type[1]:
                    semantic_error(op_token,
                                   f"Cannot subtract lists: "
                                   f"{left_type[0]}{'[]' if left_type[1] else ''} - "
                                   f"{right_type[0]}{'[]' if right_type[1] else ''}")

                if left_type[0] != right_type[0]:
                    semantic_error(op_token,
                                   f"Cannot subtract different types: "
                                   f"{left_type[0]} - {right_type[0]}")

                if left_type[0] not in {'int', 'float'}:
                    semantic_error(op_token,
                                   f"Cannot subtract non-numeric types: "
                                   f"{left_type[0]} - {right_type[0]}")

                return left_type
            return self.resto_soma(left_type)  # Para encadear operações (a + b - c + d)
        return left_type  # Caso não haja mais operadores

    # Mult -> Uno RestoMult
    def mult(self):
        left_type = self.uno()
        return self.resto_mult(left_type)

    # RestoMult -> LAMBDA | * Uno RestoMult | / Uno RestoMult | mod Uno RestoMult | div Uno RestoMult
    def resto_mult(self, left_type):
        if self.current_token[0] in {TOKEN.star, TOKEN.slash, TOKEN.MOD, TOKEN.DIV}:
            op = self.current_token[0]
            self.consume(op)
            right_type = self.uno()

            if left_type != right_type or left_type[1] or right_type[1]:
                semantic_error(self.current_token,
                               f"Arithmetic operation '{TOKEN.message(op)}' requires operands of same non-list numeric type")

            return self.resto_mult(left_type)
        return left_type

    # Uno -> + Uno | - Uno | Folha
    def uno(self):
        if self.current_token[0] in {TOKEN.plus, TOKEN.minus}:
            op = self.current_token[0]
            self.consume(op)
            expr_type = self.uno()

            if expr_type[0] not in {"int", "float"} or expr_type[1]:
                semantic_error(self.current_token,
                               f"Unary '{TOKEN.message(op)}' requires numeric non-list operand")

            return expr_type
        else:
            return self.folha()

    # Folha -> ValPrim | ident Recorte | ident ( ListaArgs ) | ( Exp ) | ValLista
    def folha(self):
        token = self.current_token[0]

        if token in {TOKEN.valInt, TOKEN.valFloat, TOKEN.valString}:
            return self.val_prim()

        elif token == TOKEN.ident:
            ident_token = self.current_token
            ident_name = ident_token[1]
            self.consume(TOKEN.ident)

            if self.current_token[0] == TOKEN.openBracket:
                self.consume(TOKEN.openBracket)
                tipo = self.semantic.get_var_info(ident_name, ident_token)

                if not tipo[1]:
                    semantic_error(ident_token, f"Variable '{ident_name}' is not a list")

                # Verifica se é slicing
                if self.current_token[0] == TOKEN.colon or self.peek_char() == ':':
                    # Consome início se existir
                    if self.current_token[0] != TOKEN.colon:
                        self.exp()
                    self.consume(TOKEN.colon)
                    # Consome fim se existir
                    if self.current_token[0] != TOKEN.closeBracket:
                        self.exp()
                    self.consume(TOKEN.closeBracket)
                    return (tipo[0], True)
                else:
                    # Acesso normal
                    self.exp()
                    self.consume(TOKEN.closeBracket)
                    return (tipo[0], False)

            elif self.current_token[0] == TOKEN.openParenthesis:
                self.consume(TOKEN.openParenthesis)
                arg_types = self.lista_args()
                self.consume(TOKEN.closeParenthesis)

                func_info = self.semantic.get_func_info(ident_name, ident_token)
                ret_type, params, _ = func_info

                # Verificar número de argumentos
                if len(arg_types) != len(params):
                    semantic_error(ident_token,
                                   f"Function '{ident_name}' expects {len(params)} arguments, got {len(arg_types)}")

                # Verificar tipos dos argumentos
                for i, (arg_type, (_, param_type)) in enumerate(zip(arg_types, params)):
                    if arg_type != param_type:
                        semantic_error(ident_token,
                                       f"Argument {i + 1} of '{ident_name}' expected {param_type}, got {arg_type}")

                return ret_type

            else:  # Variável simples
                tipo = self.semantic.get_var_info(ident_name, ident_token)
                return tipo

        elif token == TOKEN.openParenthesis:
            self.consume(TOKEN.openParenthesis)
            expr_type = self.exp()
            self.consume(TOKEN.closeParenthesis)
            return expr_type

        elif token == TOKEN.openBracket:
            return self.val_lista()

        else:
            semantic_error(self.current_token, "Invalid expression")

    # ValPrim -> valint | valfloat | valstring
    def val_prim(self):
        token = self.current_token[0]

        if token == TOKEN.valInt:
            self.consume(TOKEN.valInt)
            return ("int", False)
        elif token == TOKEN.valFloat:
            self.consume(TOKEN.valFloat)
            return ("float", False)
        elif token == TOKEN.valString:
            self.consume(TOKEN.valString)
            return ("string", False)
        else:
            semantic_error(self.current_token, "Expected primitive value")

    # ValLista -> [ ListaExp ]
    def val_lista(self):
        self.consume(TOKEN.openBracket)

        if self.current_token[0] == TOKEN.closeBracket:  # Lista vazia
            self.consume(TOKEN.closeBracket)
            return ("int", True)  # Por padrão, assumimos lista de inteiros vazia

        element_types = self.lista_exp()
        self.consume(TOKEN.closeBracket)

        # Verificar se todos os elementos têm o mesmo tipo
        if len(element_types) > 0:
            first_type = element_types[0]
            for t in element_types[1:]:
                if t != first_type:
                    semantic_error(self.current_token, "All list elements must be of the same type")
            return (first_type[0], True)
        else:
            return ("int", True)  # Lista vazia

    def recorte(self):
        if self.current_token[0] == TOKEN.openBracket:
            self.consume(TOKEN.openBracket)

            # Verifica se é slicing
            if self.current_token[0] == TOKEN.colon or self.peek_char() == ':':
                if self.current_token[0] != TOKEN.colon:
                    self.exp()  # Início do slice
                self.consume(TOKEN.colon)
                if self.current_token[0] != TOKEN.closeBracket:
                    self.exp()  # Fim do slice
                self.consume(TOKEN.closeBracket)
                return True
            else:
                self.exp()  # Acesso normal
                self.consume(TOKEN.closeBracket)
                return False
        return False

    # ListaArgs -> LAMBDA | Exp RestoListaArgs
    def lista_args(self):
        arg_types = []
        if self.current_token[0] in {
            TOKEN.ident, TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
            TOKEN.openParenthesis, TOKEN.openBracket, TOKEN.NOT,
            TOKEN.plus, TOKEN.minus
        }:
            arg_types.append(self.exp())
            arg_types.extend(self.resto_lista_args())
        return arg_types

    # RestoListaArgs -> LAMBDA | , Exp RestoListaArgs
    def resto_lista_args(self):
        arg_types = []
        if self.current_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            arg_types.append(self.exp())
            arg_types.extend(self.resto_lista_args())
        return arg_types

    # ListaExp -> LAMBDA | Exp OpcListaExp
    def lista_exp(self):
        exp_types = []
        if self.current_token[0] in {
            TOKEN.ident, TOKEN.valInt, TOKEN.valFloat, TOKEN.valString,
            TOKEN.openParenthesis, TOKEN.openBracket, TOKEN.NOT,
            TOKEN.plus, TOKEN.minus
        }:
            exp_types.append(self.exp())
            exp_types.extend(self.opc_lista_exp(exp_types[0]))
        return exp_types

    # OpcListaExp -> LAMBDA | , Exp OpcListaExp
    def opc_lista_exp(self, expected_type):
        exp_types = []
        if self.current_token[0] == TOKEN.comma:
            self.consume(TOKEN.comma)
            current_type = self.exp()
            if current_type != expected_type:
                semantic_error(self.current_token,
                               f"All list elements must have the same type. Expected {expected_type}, got {current_type}")
            exp_types.append(current_type)
            exp_types.extend(self.opc_lista_exp(expected_type))
        return exp_types

    def translate(self):
        try:
            self.parse()
            print('Success on translation!')
        except Exception as e:
            print(f'Translation failed: {str(e)}')
        finally:
            self.semantic.finish()