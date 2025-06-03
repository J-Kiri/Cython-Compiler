"""
#--- tokens
ident ( ) , void [ ] int float string { } ;
valint valfloat valstring = if else elif while for
foreach : continue break return read write
+ - * / mod div not and or == != > < >= <=
ERRO EOF

#--- programa
Prog --> lambda | Func Prog
Func --> TipoRet ident ( ListaParam ) Corpo
TipoRet --> void | Tipo
ListaParam --> lambda | Param OpcParams
OpcParams --> lambda | , Param OpcParams
Param --> Tipo ident
Corpo --> { ListaDeclara ListaComando }
ListaDeclara --> lambda | Declara ListaDeclara
ListaComando --> lambda | Comando ListaComando

#--- declaracoes e tipos
Tipo --> Primitivo | [ Primitivo ]
Primitivo --> int | float | string
Declara --> Tipo ListaVar ;
ListaVar --> Var RestoListaVar
RestoListaVar --> lambda | , ListaVar
Var --> ident OpcValor
OpcValor --> lambda | = Exp

#--- comandos
Comando --> ComAtrib | ComIf | ComFor | ComWhile |
| ComReturn | ComContinue | ComBreak | ComEntrada
| ComSaida | ComBloco
ComAtrib --> ident PosicaoOpc = Exp ;
PosicaoOpc --> LAMBDA | [ Exp ]
ComIf --> if ( Exp ) Comando OpcElse
OpcElse --> lambda | else Comando | elif ( Exp ) Comando OpcElse
ComFor --> for ( ident = Exp ; Exp ; ident = Exp ) Comando
| foreach ident = Exp : Comando
ComWhile --> while ( Exp ) Comando
ComReturn --> return OpcRet ;
OpcRet --> lambda | Exp
ComContinue --> continue ;
ComBreak --> break ;
ComEntrada --> read ( ident ) ;
ComSaida --> write ( ListaOut ) ;
ListaOut --> Exp RestoListaOut
RestoListaOut --> lambda | , ListaOut
ComBloco --> { ListaComando }

#### EXPRESSOES (etapas da construcao da gramatica )

#-- 1a versao (beta)
Folha --> ValPrim | ident Recorte | ident ( ListaArgs ) | ( Exp ) | ValLista
ValPrim --> valint | valfloat | valstring
ValLista --> [ ListaExp ]
Recorte --> lambda | [ Dentro ]
Dentro --> Exp RestoDentro | : OpcInt
RestoDentro --> lambda | : OpcInt
OpcInt --> lambda | Exp
ListaArgs --> lambda | Exp RestoListaArgs
RestoListaArgs --> lambda | , Exp RestoListaArgs
ListaExp --> LAMBDA | Exp OpcListaExp
OpcListaExp --> LAMBDA | , Exp OpcListaExp
Uno --> + Uno | - Uno | Folha

# Mult --> Mult * Uno | Mult / Uno | Mult mod Uno | Mult div Uno | Uno
Mult --> Uno RestoMult
RestoMult --> lambda | * Uno RestoMult | / Uno RestoMult
| mod Uno RestoMult | div Uno RestoMult

# Soma --> Soma + Mult | Soma - Mult | Mult
Soma --> Mult RestoSoma
RestoSoma --> lambda | + Mult RestoSoma | - Mult RestoSoma

# Rel --> Soma == Soma | Soma != Soma | Soma <= Soma |
# Soma >= Soma | Soma < Soma | Soma > Soma | Soma
Rel --> Soma RestoRel
RestoRel --> lambda | == Soma | != Soma | <= Soma | >= Soma
| > Soma | < Soma

Nao --> not Nao | Rel
# Junc --> Junc and Nao | Nao
Junc --> Nao RestoJunc
RestoJunc --> lambda | and Nao RestoJunc

# Exp --> Exp or Junc | Junc
Exp --> Junc RestoExp
RestoExp --> lambda | or Junc RestoExp
"""

from enum import IntEnum

class TOKEN(IntEnum):
    ident = 1
    openParenthesis = 2
    closeParenthesis = 3
    comma = 4
    VOID = 5
    openBracket = 6
    closeBracket = 7
    INT = 8
    FLOAT = 9
    STRING = 10
    openBraces = 11
    closeBraces = 12
    semiColon = 13
    valInt = 14
    valFloat = 15
    valString = 16
    equal = 17
    IF = 18
    ELSE = 19
    ELIF = 20
    WHILE = 21
    FOR = 22
    FOREACH = 23
    colon = 24
    CONTINUE = 25
    BREAK = 26
    RETURN = 27
    READ = 28
    WRITE = 29
    plus = 30
    minus = 31
    star = 32
    slash = 33
    MOD = 34
    DIV = 35
    NOT = 36
    AND = 37
    OR = 38
    equalEqual = 39
    notEqual = 40
    greaterThan = 41
    lessThan = 42
    greaterThanOrEqual = 43
    lessThanOrEqual = 44
    ERROR = 45
    EOF = 46
    commandAtribution = 47
    
    @classmethod
    def message(cls, token):
        names = {
            1: 'ident',
            2: '(',
            3: ')',
            4: ',',
            5: 'void',
            6: '[',
            7: ']',
            8: 'int',
            9: 'float',
            10: 'string',
            11: '{',
            12: '}',
            13: ';',
            14: 'valint',
            15: 'valfloat',
            16: 'valstring',
            17: '=',
            18: 'if',
            19: 'else',
            20: 'elif',
            21: 'while',
            22: 'for',
            23: 'foreach',
            24: ':',
            25: 'continue',
            26: 'break',
            27: 'return',
            28: 'read',
            29: 'write',
            30: '+',
            31: '-',
            32: '*',
            33: '/',
            34: 'mod',
            35: 'div',
            36: 'not',
            37: 'and',
            38: 'or',
            39: '==',
            40: '!=',
            41: '>',
            42: '<',
            43: '>=',
            44: '<=',
            45: 'error',
            46: 'eof',
            47: '='
        }
        
        return names[token]
    
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
            'or': TOKEN.OR,
            'error': TOKEN.ERROR,
            'eof': TOKEN.EOF
        }
        
        if lexeme in reserved:
            return reserved[lexeme]
        else:
            return TOKEN.ident
    