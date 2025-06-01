# parser.py - Analisador sintático para Pascal Standard (CORRIGIDO CONFORME PROFESSOR)
import ply.yacc as yacc
from lexer import tokens  # Importa os tokens do lexer

# Estrutura para representar a AST (Abstract Syntax Tree)
class ASTNode:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children else []
        self.value = value
        self.line = 0  # Linha do código fonte
        
    def __repr__(self):
        return f"ASTNode({self.type}, {self.value}, {len(self.children)} children)"

# Precedência e associatividade dos operadores
precedence = (
    ('nonassoc', 'THEN'),
    ('nonassoc', 'ELSE'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'DIV', 'MOD'),
    ('right', 'UMINUS', 'NOT'),
)

# ===== REGRAS GRAMATICAIS =====

# Programa principal
def p_program(p):
    '''program : PROGRAM ID SEMICOLON declarations compound_statement DOT'''
    p[0] = ASTNode('program', [p[4], p[5]], p[2])
    p[0].line = p.lineno(1)

# Declarações
def p_declarations(p):
    '''declarations : declarations var_declaration
                   | declarations const_declaration
                   | declarations type_declaration
                   | declarations function_declaration
                   | declarations procedure_declaration
                   | empty'''
    if len(p) == 2:  # empty
        p[0] = ASTNode('declarations', [])
    else:
        p[1].children.append(p[2])
        p[0] = p[1]

# Declaração de variáveis
def p_var_declaration(p):
    '''var_declaration : VAR var_list'''
    p[0] = ASTNode('var_declaration', p[2])
    p[0].line = p.lineno(1)

def p_var_list(p):
    '''var_list : var_list var_item
                | var_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_var_item(p):
    '''var_item : id_list COLON type SEMICOLON'''
    p[0] = ASTNode('var_item', [p[1], p[3]])
    p[0].line = p.lineno(2)

def p_id_list(p):
    '''id_list : id_list COMMA ID
               | ID'''
    if len(p) == 2:
        p[0] = ASTNode('id_list', [], [p[1]])
        p[0].line = p.lineno(1)
    else:
        p[1].value.append(p[3])
        p[0] = p[1]

# Tipos
def p_type(p):
    '''type : simple_type
            | array_type'''
    p[0] = p[1]

def p_simple_type(p):
    '''simple_type : INTEGER
                   | REAL
                   | BOOLEAN
                   | STRING'''
    p[0] = ASTNode('type', [], p[1])
    p[0].line = p.lineno(1)

def p_array_type(p):
    '''array_type : ARRAY LBRACKET INTEGER_CONST DOTDOT INTEGER_CONST RBRACKET OF simple_type'''
    p[0] = ASTNode('array_type', [p[8]], [p[3], p[5]])
    p[0].line = p.lineno(1)

# Declaração de constantes
def p_const_declaration(p):
    '''const_declaration : CONST const_list'''
    p[0] = ASTNode('const_declaration', p[2])
    p[0].line = p.lineno(1)

def p_const_list(p):
    '''const_list : const_list const_item
                  | const_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_const_item(p):
    '''const_item : ID EQ expr_bool SEMICOLON'''
    p[0] = ASTNode('const_item', [p[3]], p[1])
    p[0].line = p.lineno(2)

# Declaração de tipos
def p_type_declaration(p):
    '''type_declaration : TYPE type_list'''
    p[0] = ASTNode('type_declaration', p[2])
    p[0].line = p.lineno(1)

def p_type_list(p):
    '''type_list : type_list type_item
                 | type_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[1].append(p[2])
        p[0] = p[1]

def p_type_item(p):
    '''type_item : ID EQ type SEMICOLON'''
    p[0] = ASTNode('type_item', [p[3]], p[1])
    p[0].line = p.lineno(2)

# Declaração de funções
def p_function_declaration(p):
    '''function_declaration : FUNCTION ID LPAREN parameter_list RPAREN COLON simple_type SEMICOLON declarations compound_statement SEMICOLON'''
    p[0] = ASTNode('function_declaration', [p[4], p[7], p[9], p[10]], p[2])
    p[0].line = p.lineno(1)

def p_function_declaration_no_params(p):
    '''function_declaration : FUNCTION ID COLON simple_type SEMICOLON declarations compound_statement SEMICOLON'''
    p[0] = ASTNode('function_declaration', [ASTNode('parameter_list', []), p[4], p[6], p[7]], p[2])
    p[0].line = p.lineno(1)

# Declaração de procedimentos
def p_procedure_declaration(p):
    '''procedure_declaration : PROCEDURE ID LPAREN parameter_list RPAREN SEMICOLON declarations compound_statement SEMICOLON'''
    p[0] = ASTNode('procedure_declaration', [p[4], p[7], p[8]], p[2])
    p[0].line = p.lineno(1)

def p_procedure_declaration_no_params(p):
    '''procedure_declaration : PROCEDURE ID SEMICOLON declarations compound_statement SEMICOLON'''
    p[0] = ASTNode('procedure_declaration', [ASTNode('parameter_list', []), p[4], p[5]], p[2])
    p[0].line = p.lineno(1)

# Lista de parâmetros
def p_parameter_list(p):
    '''parameter_list : parameter_list SEMICOLON parameter
                      | parameter'''
    if len(p) == 2:
        p[0] = ASTNode('parameter_list', [p[1]])
    else:
        p[1].children.append(p[3])
        p[0] = p[1]

def p_parameter(p):
    '''parameter : id_list COLON simple_type'''
    p[0] = ASTNode('parameter', [p[1], p[3]])
    p[0].line = p.lineno(2)

# Comando composto
def p_compound_statement(p):
    '''compound_statement : BEGIN statement_list END'''
    p[0] = ASTNode('compound_statement', p[2])
    p[0].line = p.lineno(1)

def p_statement_list(p):
    '''statement_list : statement_list SEMICOLON statement
                      | statement'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        if p[3]:  # Se o statement não for vazio
            p[1].append(p[3])
        p[0] = p[1]

# Comandos
def p_statement(p):
    '''statement : assignment_statement
                 | compound_statement
                 | if_statement
                 | while_statement
                 | for_statement
                 | procedure_call
                 | read_statement
                 | write_statement
                 | empty'''
    p[0] = p[1]

# Comando de atribuição
def p_assignment_statement(p):
    '''assignment_statement : var ASSIGN expr_bool'''
    p[0] = ASTNode('assignment', [p[1], p[3]])
    p[0].line = p.lineno(2)

# Comando if
def p_if_statement(p):
    '''if_statement : IF expr_bool THEN statement ELSE statement
                    | IF expr_bool THEN statement'''
    if len(p) == 5:  # sem else
        p[0] = ASTNode('if_statement', [p[2], p[4]])
    else:  # com else
        p[0] = ASTNode('if_statement', [p[2], p[4], p[6]])
    p[0].line = p.lineno(1)

# Comando while
def p_while_statement(p):
    '''while_statement : WHILE expr_bool DO statement'''
    p[0] = ASTNode('while_statement', [p[2], p[4]])
    p[0].line = p.lineno(1)

# Comando for
def p_for_statement(p):
    '''for_statement : FOR ID ASSIGN expr_bool TO expr_bool DO statement
                     | FOR ID ASSIGN expr_bool DOWNTO expr_bool DO statement'''
    
    # Verificação robusta do tipo de loop
    token = p[5]
    if hasattr(token, 'type'):
        # Se é um objeto token, usa o tipo
        direction = 'to' if token.type == 'TO' else 'downto'
    elif hasattr(token, 'value'):
        # Se é um objeto token, usa o valor
        direction = 'to' if token.value.upper() == 'TO' else 'downto'
    else:
        # Se é uma string direta
        direction = 'to' if str(token).upper() == 'TO' else 'downto'
    
    p[0] = ASTNode('for_statement', [p[4], p[6], p[8]], [p[2], direction])
    p[0].line = p.lineno(1)

# Comando read/readln
def p_read_statement(p):
    '''read_statement : READ LPAREN variable_list RPAREN
                      | READLN LPAREN variable_list RPAREN
                      | READLN'''
    if len(p) == 2:  # readln sem argumentos
        p[0] = ASTNode('read_statement', [], p[1])
    else:
        p[0] = ASTNode('read_statement', [p[3]], p[1])
    p[0].line = p.lineno(1)

# Comando write/writeln
def p_write_statement(p):
    '''write_statement : WRITE LPAREN expression_list RPAREN
                       | WRITELN LPAREN expression_list RPAREN
                       | WRITELN
                       | WRITE LPAREN RPAREN
                       | WRITELN LPAREN RPAREN'''
    if len(p) == 2:  # writeln sem argumentos
        p[0] = ASTNode('write_statement', [], p[1])
    elif len(p) == 4:  # write() ou writeln() vazios
        p[0] = ASTNode('write_statement', [], p[1])
    else:
        p[0] = ASTNode('write_statement', [p[3]], p[1])
    p[0].line = p.lineno(1)

# Lista de variáveis
def p_variable_list(p):
    '''variable_list : variable_list COMMA var
                     | var'''
    if len(p) == 2:
        p[0] = ASTNode('variable_list', [p[1]])
    else:
        p[1].children.append(p[3])
        p[0] = p[1]

# Lista de expressões
def p_expression_list(p):
    '''expression_list : expression_list COMMA expr_bool
                       | expr_bool'''
    if len(p) == 2:
        p[0] = ASTNode('expression_list', [p[1]])
    else:
        p[1].children.append(p[3])
        p[0] = p[1]

# Chamada de procedimento
def p_procedure_call(p):
    '''procedure_call : ID LPAREN argument_list RPAREN
                      | ID'''
    if len(p) == 2:
        p[0] = ASTNode('procedure_call', [], p[1])
    else:
        p[0] = ASTNode('procedure_call', [p[3]], p[1])
    p[0].line = p.lineno(1)

# Lista de argumentos
def p_argument_list(p):
    '''argument_list : argument_list COMMA expr_bool
                     | expr_bool
                     | empty'''
    if len(p) == 2:
        if p[1] is None:  # empty
            p[0] = ASTNode('argument_list', [])
        else:
            p[0] = ASTNode('argument_list', [p[1]])
    else:
        p[1].children.append(p[3])
        p[0] = p[1]

# ===== IMPLEMENTAÇÃO DA GRAMÁTICA DE EXPRESSÕES CONFORME ESPECIFICADO PELO PROFESSOR =====

# ExprBool : Expr
#          | Expr OpRel Expr
def p_expr_bool(p):
    '''expr_bool : expr
                 | expr op_rel expr'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('binary_op', [p[1], p[3]], p[2])
        p[0].line = p.lineno(2)

# OpRel : EQ | NE | LT | LE | GT | GE
def p_op_rel(p):
    '''op_rel : EQ
              | NEQ
              | LT
              | LTE
              | GT
              | GTE'''
    p[0] = p[1]

# Expr : Termo
#      | Expr OpAd Termo
def p_expr(p):
    '''expr : termo
            | expr op_ad termo'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('binary_op', [p[1], p[3]], p[2])
        p[0].line = p.lineno(2)

# OpAd : MAIS | MENOS | OU
def p_op_ad(p):
    '''op_ad : PLUS
             | MINUS
             | OR'''
    p[0] = p[1]

# Termo : Fator
#       | Termo OpMul Fator
def p_termo(p):
    '''termo : fator
             | termo op_mul fator'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('binary_op', [p[1], p[3]], p[2])
        p[0].line = p.lineno(2)

# OpMul : VEZES | DIV | AND
def p_op_mul(p):
    '''op_mul : TIMES
              | DIV
              | DIVIDE
              | MOD
              | AND'''
    p[0] = p[1]

# Fator : Const
#       | Var
#       | "(" ExprBool ")"
#       | FuncCall
def p_fator(p):
    '''fator : const
             | var
             | LPAREN expr_bool RPAREN
             | func_call
             | unary_op'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]  # Para o caso de parênteses

def p_fator_length(p):
    '''fator : LENGTH LPAREN expr_bool RPAREN'''
    p[0] = ASTNode('length_call', [p[3]], 'length')
    p[0].line = p.lineno(1)
    
# Unary operators
def p_unary_op_precedence(p):
    '''unary_op : MINUS fator %prec UMINUS
                | NOT fator %prec NOT'''
    p[0] = ASTNode('unary_op', [p[2]], p[1])
    p[0].line = p.lineno(1)

# Const : INT | REAL | STRING
def p_const(p):
    '''const : INTEGER_CONST
             | REAL_CONST
             | STRING_CONST
             | TRUE
             | FALSE'''
    if p[1] in ['true', 'false', 'TRUE', 'FALSE']:
        p[0] = ASTNode('boolean', [], p[1])
    elif isinstance(p[1], int):
        p[0] = ASTNode('number', [], p[1])
    elif isinstance(p[1], float):
        p[0] = ASTNode('number', [], p[1])
    else:
        p[0] = ASTNode('string', [], p[1])
    p[0].line = p.lineno(1)

# Var : ID | ID "[" Expr "]"
def p_var(p):
    '''var : ID
           | ID LBRACKET expr RBRACKET'''
    if len(p) == 2:
        p[0] = ASTNode('variable', [], p[1])
    else:
        p[0] = ASTNode('array_access', [p[3]], p[1])
    p[0].line = p.lineno(1)

# FuncCall : ID "(" Args ")"
def p_func_call(p):
    '''func_call : ID LPAREN argument_list RPAREN'''
    p[0] = ASTNode('function_call', [p[3]], p[1])
    p[0].line = p.lineno(1)

# Regra vazia
def p_empty(p):
    '''empty :'''
    p[0] = None

# Tratamento de erros
def p_error(p):
    if p:
        print(f"Erro sintático na linha {p.lineno}: Token inesperado '{p.value}' ({p.type})")
    else:
        print("Erro sintático: Fim de arquivo inesperado")

# Construir o parser
parser = yacc.yacc()

# Função para testar o parser
def parse_code(code):
    from lexer import lexer
    try:
        result = parser.parse(code, lexer=lexer)
        return result
    except Exception as e:
        print(f"Erro durante o parsing: {e}")
        import traceback
        traceback.print_exc()  # Imprime o stack trace para depuração
        return None

# Função para imprimir a AST
def print_ast(node, indent=0):
    if node is None:
        return
    
    spaces = "  " * indent
    if isinstance(node.value, list):
        value_str = ", ".join(str(v) for v in node.value)
        print(f"{spaces}{node.type}: [{value_str}]")
    elif node.value is not None:
        print(f"{spaces}{node.type}: {node.value}")
    else:
        print(f"{spaces}{node.type}")
    
    for child in node.children:
        if isinstance(child, list):
            for item in child:
                print_ast(item, indent + 1)
        else:
            print_ast(child, indent + 1)

# Exemplo de uso
if __name__ == "__main__":
    test_code = """
    program HelloWorld;
    begin
        writeln('Ola, Mundo!');
    end.
    """
    
    print("Analisando o código:")
    print(test_code)
    print("\nÁrvore Sintática Abstrata (AST):")
    
    ast = parse_code(test_code)
    if ast:
        print_ast(ast)
    else:
        print("Falha no parsing")
