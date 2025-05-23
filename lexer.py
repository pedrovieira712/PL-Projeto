# lexer.py - Analisador léxico para Pascal Standard (CORRIGIDO)
import ply.lex as lex

# Lista de tokens (removido RECORD)
tokens = (
    # Palavras reservadas
    'PROGRAM', 'BEGIN', 'END', 'VAR', 'INTEGER', 'REAL', 'BOOLEAN', 'STRING',
    'ARRAY', 'OF', 'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO', 'DOWNTO',
    'FUNCTION', 'PROCEDURE', 'CONST', 'TYPE', 'DIV', 'MOD', 'AND',
    'OR', 'NOT', 'TRUE', 'FALSE', 'READLN', 'WRITELN', 'READ', 'WRITE',
    
    # Identificadores e literais
    'ID', 'INTEGER_CONST', 'REAL_CONST', 'STRING_CONST',
    
    # Operadores
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    
    # Delimitadores
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA', 'SEMICOLON', 'COLON', 'DOT', 'DOTDOT'
)

# Palavras reservadas (case-insensitive em Pascal) - removido 'record'
reserved = {
    'program': 'PROGRAM',
    'begin': 'BEGIN',
    'end': 'END',
    'var': 'VAR',
    'integer': 'INTEGER',
    'real': 'REAL',
    'boolean': 'BOOLEAN',
    'string': 'STRING',
    'array': 'ARRAY',
    'of': 'OF',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'for': 'FOR',
    'to': 'TO',
    'downto': 'DOWNTO',
    'function': 'FUNCTION',
    'procedure': 'PROCEDURE',
    'const': 'CONST',
    'type': 'TYPE',
    'div': 'DIV',
    'mod': 'MOD',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'true': 'TRUE',
    'false': 'FALSE',
    'readln': 'READLN',
    'writeln': 'WRITELN',
    'read': 'READ',
    'write': 'WRITE'
}

# Regras para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r':='
t_EQ = r'='
t_NEQ = r'<>'
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_DOT = r'\.'
t_DOTDOT = r'\.\.'

# Ignorar espaços em branco e tabs
t_ignore = ' \t'

# Regra para identificadores e palavras reservadas
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    # Verifica se é uma palavra reservada (case-insensitive)
    t.type = reserved.get(t.value.lower(), 'ID')
    return t

# Regra para números reais
def t_REAL_CONST(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Regra para números inteiros
def t_INTEGER_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regra para strings
def t_STRING_CONST(t):
    r'\'([^\']|\'\')*\''
    # Remove as aspas e substitui '' por '
    t.value = t.value[1:-1].replace("''", "'")
    return t

# Regra para comentários de chaves { ... }
def t_COMMENT_BRACE(t):
    r'\{[^}]*\}'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignora o comentário

# Regra para comentários de parênteses (* ... *)
def t_COMMENT_PAREN(t):
    r'$$\*(.|\n)*?\*$$'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignora o comentário

# Regra para quebras de linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Regra para erros
def t_error(t):
    print(f"Erro léxico: Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

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
    end.
    """
    
    print("Analisando o código:")
    print(test_code)
    print("\nTokens encontrados:")
    
    tokens_result = test_lexer(test_code)
    for token_type, token_value, line_no in tokens_result:
        print(f"Linha {line_no}: {token_type} - '{token_value}'")