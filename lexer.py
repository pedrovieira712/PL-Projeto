# lexer_corrected.py - Analisador léxico para Pascal Standard (VERSÃO CORRIGIDA)
# Seguindo as diretrizes do professor - sem dicionário de palavras reservadas
import ply.lex as lex

# Lista de tokens
tokens = (
    # Palavras reservadas
    'PROGRAM', 'BEGIN', 'END', 'VAR', 'INTEGER', 'REAL', 'BOOLEAN', 'STRING',
    'ARRAY', 'OF', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO', 'DOWNTO',
    'FUNCTION', 'PROCEDURE', 'CONST', 'TYPE', 'DIV', 'MOD', 'AND',
    'OR', 'NOT', 'TRUE', 'FALSE', 'READLN', 'WRITELN', 'READ', 'WRITE',
    'LENGTH',  # Adicionado token LENGTH
    
    # Identificadores e literais
    'ID', 'INTEGER_CONST', 'REAL_CONST', 'STRING_CONST',
    
    # Operadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    
    # Delimitadores
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA', 'SEMICOLON', 'COLON', 'DOT', 'DOTDOT'
)

# IMPORTANTE: A ordem das definições importa no PLY!
# As palavras reservadas devem vir ANTES da regra geral de identificadores

# ===== PALAVRAS RESERVADAS - Definidas com ER específicas (case-insensitive) =====

def t_PROGRAM(t):
    r'[pP][rR][oO][gG][rR][aA][mM]'
    return t

def t_PROCEDURE(t):
    r'[pP][rR][oO][cC][eE][dD][uU][rR][eE]'
    return t

def t_FUNCTION(t):
    r'[fF][uU][nN][cC][tT][iI][oO][nN]'
    return t

def t_BEGIN(t):
    r'[bB][eE][gG][iI][nN]'
    return t

def t_END(t):
    r'[eE][nN][dD]'
    return t

def t_CONST(t):
    r'[cC][oO][nN][sS][tT]'
    return t

def t_TYPE(t):
    r'[tT][yY][pP][eE]'
    return t

def t_VAR(t):
    r'[vV][aA][rR]'
    return t

def t_INTEGER(t):
    r'[iI][nN][tT][eE][gG][eE][rR]'
    return t

def t_REAL(t):
    r'[rR][eE][aA][lL]'
    return t

def t_BOOLEAN(t):
    r'[bB][oO][oO][lL][eE][aA][nN]'
    return t

def t_STRING(t):
    r'[sS][tT][rR][iI][nN][gG]'
    return t

def t_ARRAY(t):
    r'[aA][rR][rR][aA][yY]'
    return t

def t_OF(t):
    r'[oO][fF]'
    return t

def t_IF(t):
    r'[iI][fF]'
    return t

def t_THEN(t):
    r'[tT][hH][eE][nN]'
    return t

def t_ELSE(t):
    r'[eE][lL][sS][eE]'
    return t

def t_WHILE(t):
    r'[wW][hH][iI][lL][eE]'
    return t

def t_DOWNTO(t):
    r'[dD][oO][wW][nN][tT][oO]'
    return t

def t_DO(t):
    r'[dD][oO]'
    return t

def t_FOR(t):
    r'[fF][oO][rR]'
    return t

def t_TO(t):
    r'[tT][oO]'
    return t

def t_DIV(t):
    r'[dD][iI][vV]'
    return t

def t_MOD(t):
    r'[mM][oO][dD]'
    return t

def t_AND(t):
    r'[aA][nN][dD]'
    return t

def t_OR(t):
    r'[oO][rR]'
    return t

def t_NOT(t):
    r'[nN][oO][tT]'
    return t

def t_TRUE(t):
    r'[tT][rR][uU][eE]'
    return t

def t_FALSE(t):
    r'[fF][aA][lL][sS][eE]'
    return t

def t_READLN(t):
    r'[rR][eE][aA][dD][lL][nN]'
    return t

def t_WRITELN(t):
    r'[wW][rR][iI][tT][eE][lL][nN]'
    return t

def t_READ(t):
    r'[rR][eE][aA][dD]'
    return t

def t_WRITE(t):
    r'[wW][rR][iI][tT][eE]'
    return t

# Adicionado token LENGTH
def t_LENGTH(t):
    r'[lL][eE][nN][gG][tT][hH]'
    return t

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
def t_REAL_CONST(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Números inteiros
def t_INTEGER_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Strings
def t_STRING_CONST(t):
    r'\'([^\']|\'\')*\''
    # Remove as aspas e substitui '' por '
    t.value = t.value[1:-1].replace("''", "'")
    return t

# ===== IDENTIFICADORES - DEVE vir DEPOIS das palavras reservadas =====
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    return t

# ===== COMENTÁRIOS =====

# Comentários de chaves { ... }
def t_COMMENT_BRACE(t):
    r'\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignora o comentário

# Comentários de parênteses (* ... *)
def t_COMMENT_PAREN(t):
    r'$$\*(.|\n)*?\*$$'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignora o comentário

# ===== CONTROLO DE LINHAS E ESPAÇOS =====

# Ignorar espaços em branco e tabs
t_ignore = ' \t'

# Quebras de linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# ===== TRATAMENTO DE ERROS =====

def t_error(t):
    print(f"Erro léxico: Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

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
    # Exemplo de código Pascal do projeto
    test_code = """
    program HelloWorld;
    begin
        writeln('Ola, Mundo!');
        writeln(length('teste'));
    end.
    """
    
    print("Analisando o código:")
    print(test_code)
    print("\nTokens encontrados:")
    
    tokens_result = test_lexer(test_code)
    for token_type, token_value, line_no in tokens_result:
        print(f"Linha {line_no}: {token_type} - '{token_value}'")
