import ply.lex as lex

tokens = (
    # Palavras reservadas
    'PROGRAM', 'BEGIN', 'END', 'VAR', 'INTEGER', 'REAL', 'BOOLEAN', 'STRING',
    'ARRAY', 'OF', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO', 'DOWNTO',
    'FUNCTION', 'PROCEDURE', 'CONST', 'TYPE', 'DIV', 'MOD', 'AND',
    'OR', 'NOT', 'TRUE', 'FALSE', 'READLN', 'WRITELN', 'READ', 'WRITE',
    'LENGTH',
    
    # Identificadores e literais
    'ID', 'INTEGER_CONST', 'REAL_CONST', 'STRING_CONST',
    
    # Operadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    
    # Delimitadores
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA', 'SEMICOLON', 'COLON', 'DOT', 'DOTDOT'
)

# ===== PALAVRAS RESERVADAS - Definidas com ER específicas (case-insensitive) =====

def t_PROGRAM(p):
    r'(?i)program(?![a-zA-Z0-9_])'
    return p

def t_PROCEDURE(p):
    r'(?i)procedure(?![a-zA-Z0-9_])'
    return p

def t_FUNCTION(p):
    r'(?i)function(?![a-zA-Z0-9_])'
    return p

def t_BEGIN(p):
    r'(?i)begin(?![a-zA-Z0-9_])'
    return p

def t_END(p):
    r'(?i)end(?![a-zA-Z0-9_])'
    return p

def t_CONST(p):
    r'(?i)const(?![a-zA-Z0-9_])'
    return p

def t_TYPE(p):
    r'(?i)type(?![a-zA-Z0-9_])'
    return p

def t_VAR(p):
    r'(?i)var(?![a-zA-Z0-9_])'
    return p

def t_INTEGER(p):
    r'(?i)integer(?![a-zA-Z0-9_])'
    return p

def t_REAL(p):
    r'(?i)real(?![a-zA-Z0-9_])'
    return p

def t_BOOLEAN(p):
    r'(?i)boolean(?![a-zA-Z0-9_])'
    return p

def t_STRING(p):
    r'(?i)string(?![a-zA-Z0-9_])'
    return p

def t_ARRAY(p):
    r'(?i)array(?![a-zA-Z0-9_])'
    return p

def t_OF(p):
    r'(?i)of(?![a-zA-Z0-9_])'
    return p

def t_IF(p):
    r'(?i)if(?![a-zA-Z0-9_])'
    return p

def t_THEN(p):
    r'(?i)then(?![a-zA-Z0-9_])'
    return p

def t_ELSE(p):
    r'(?i)else(?![a-zA-Z0-9_])'
    return p

def t_WHILE(p):
    r'(?i)while(?![a-zA-Z0-9_])'
    return p

def t_DOWNTO(p):
    r'(?i)downto(?![a-zA-Z0-9_])'
    return p

def t_DO(p):
    r'(?i)do(?![a-zA-Z0-9_])'
    return p

def t_FOR(p):
    r'(?i)for(?![a-zA-Z0-9_])'
    return p

def t_TO(p):
    r'(?i)to(?![a-zA-Z0-9_])'
    return p

def t_DIV(p):
    r'(?i)div(?![a-zA-Z0-9_])'
    return p

def t_MOD(p):
    r'(?i)mod(?![a-zA-Z0-9_])'
    return p

def t_AND(p):
    r'(?i)and(?![a-zA-Z0-9_])'
    return p

def t_OR(p):
    r'(?i)or(?![a-zA-Z0-9_])'
    return p

def t_NOT(p):
    r'(?i)not(?![a-zA-Z0-9_])'
    return p

def t_TRUE(p):
    r'(?i)true(?![a-zA-Z0-9_])'
    return p

def t_FALSE(p):
    r'(?i)false(?![a-zA-Z0-9_])'
    return p

def t_READLN(p):
    r'(?i)readln(?![a-zA-Z0-9_])'
    return p

def t_WRITELN(p):
    r'(?i)writeln(?![a-zA-Z0-9_])'
    return p

def t_READ(p):
    r'(?i)read(?![a-zA-Z0-9_])'
    return p

def t_WRITE(p):
    r'(?i)write(?![a-zA-Z0-9_])'
    return p

def t_LENGTH(p):
    r'(?i)length(?![a-zA-Z0-9_])'
    return p

# ===== IDENTIFICADORES - DEVE vir DEPOIS das palavras reservadas =====
def t_ID(p):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    return p

# ===== OPERADORES E DELIMITADORES =====

# Operadores de dois caracteres devem vir antes dos de um caractere
t_ASSIGN = r':='
t_NEQ = r'<>'
t_LTE = r'<='
t_GTE = r'>='
t_DOTDOT = r'\.\.'

# Operadores simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQ = r'='
t_LT = r'<'
t_GT = r'>'

# Delimitadores
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_DOT = r'\.'

# ===== LITERAIS =====

# Números reais (deve vir antes de inteiros)
def t_REAL_CONST(p):
    r'\d+\.\d+'
    p.value = float(p.value)
    return p

# Números inteiros
def t_INTEGER_CONST(p):
    r'\d+'
    p.value = int(p.value)
    return p

# Strings
def t_STRING_CONST(p):
    r'\'([^\']|\'\')*\''
    raw_value = p.value[1:-1]  # Remove aspas externas
    processed_value = raw_value.replace("''", "'")
    p.value = processed_value
    return p

# ===== COMENTÁRIOS =====

# Comentários de chaves { ... }
def t_COMMENT_BRACE(p):
    r'\{[^}]*\}'
    p.lexer.lineno += p.value.count('\n')
    pass  # Ignora o comentário

# Comentários de parênteses (* ... *)
def t_COMMENT_PAREN(p):
    r'$$\*(.|\n)*?\*$$'
    p.lexer.lineno += p.value.count('\n')
    pass  # Ignora o comentário

# ===== CONTROLO DE LINHAS E ESPAÇOS =====

# Ignorar espaços em branco e tabs
t_ignore = ' \t'

# Quebras de linha
def t_newline(p):
    r'\n+'
    p.lexer.lineno += len(p.value)

# ===== TRATAMENTO DE ERROS =====

def t_error(p):
    print(f"Erro léxico: Caractere ilegal '{p.value[0]}' na linha {p.lexer.lineno}")
    p.lexer.skip(1)

# ===== CONSTRUÇÃO DO LEXER =====

# Construir o lexer
lexer = lex.lex()

# Função para testar o lexer
def test_lexer(data):
    lexer.input(data)
    tokens_list = []
    for tok in lexer:
        tokens_list.append((tok.type, tok.value, tok.lineno))
    return tokens_list

# Exemplo de uso
if __name__ == "__main__":
    # Teste com OrdenaParcial
    test_code = """
    program Test;
    function OrdenaParcial(a: integer): integer;
    begin
        OrdenaParcial := a;
    end;
    begin
        writeln('Teste');
    end.
    """
    
    print("Analisando o código:")
    print(test_code)
    print("\nTokens encontrados:")
    
    tokens_result = test_lexer(test_code)
    for token_type, token_value, line_no in tokens_result:
        print(f"Linha {line_no}: {token_type} - '{token_value}'")
