# codegen.py - Gerador de código para EWVM (Educational Web Virtual Machine)
# Versão adaptada para a VM do professor

from symboltable import SymbolTable

class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.label_counter = 0
        self.current_function = None
        self.global_vars = {}  # Mapeia nome da variável para índice global
        self.local_vars = {}   # Mapeia nome da variável para índice local
        self.var_counter = 0   # Contador para variáveis globais
        
    def generate(self, ast):
        """Gera código EWVM a partir da AST."""
        if ast is None:
            return []
        
        if ast.type == 'program':
            # Primeiro, declara todas as variáveis globais
            declarations = ast.children[0]
            self.declare_global_variables(declarations)
            
            # Marca o início do programa
            self.code.append("start")
            self.code.append("")
            
            # Gera código para o bloco principal
            main_block = ast.children[1]
            self.generate_compound_statement(main_block)
            
            # Finaliza o programa
            self.code.append("stop")
            
            return self.code
        else:
            print(f"Erro: Nó raiz não é um programa")
            return []
    
    def declare_global_variables(self, declarations_node):
        """Declara variáveis globais no início do programa."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return
        
        for declaration in declarations_node.children:
            if declaration.type == 'var_declaration':
                for var_item in declaration.children:
                    id_list_node = var_item.children[0]
                    type_node = var_item.children[1]
                    
                    for var_name in id_list_node.value:
                        # Mapeia a variável para um índice global
                        self.global_vars[var_name] = self.var_counter
                        
                        # Inicializa a variável com valor padrão
                        if type_node.type == 'array_type':
                            # Para arrays, inicializa cada elemento
                            start_idx = type_node.value[0]
                            end_idx = type_node.value[1]
                            size = end_idx - start_idx + 1
                            
                            self.code.append(f"// Declaração do array {var_name}[{start_idx}..{end_idx}]")
                            for i in range(size):
                                self.code.append("pushi 0")
                                self.var_counter += 1
                        else:
                            # Variável simples - inicializa com 0
                            self.code.append(f"// Declaração da variável {var_name}")
                            if type_node.value == 'real':
                                self.code.append("pushf 0.0")
                            elif type_node.value == 'boolean':
                                self.code.append("pushi 0")  # false = 0
                            elif type_node.value == 'string':
                                self.code.append('pushs ""')
                            else:  # integer
                                self.code.append("pushi 0")
                            
                            self.var_counter += 1
        
        if self.var_counter > 0:
            self.code.append("")
    
    def generate_compound_statement(self, compound_node):
        """Gera código para um bloco de comandos."""
        if compound_node.type != 'compound_statement':
            return
        
        for statement in compound_node.children:
            self.generate_statement(statement)
    
    def generate_statement(self, statement_node):
        """Gera código para um comando."""
        if statement_node is None:
            return
        
        if statement_node.type == 'assignment':
            self.generate_assignment(statement_node)
        elif statement_node.type == 'compound_statement':
            self.generate_compound_statement(statement_node)
        elif statement_node.type == 'if_statement':
            self.generate_if_statement(statement_node)
        elif statement_node.type == 'while_statement':
            self.generate_while_statement(statement_node)
        elif statement_node.type == 'for_statement':
            self.generate_for_statement(statement_node)
        elif statement_node.type == 'write_statement':
            self.generate_write_statement(statement_node)
        elif statement_node.type == 'read_statement':
            self.generate_read_statement(statement_node)
    
    def generate_assignment(self, assignment_node):
        """Gera código para uma atribuição."""
        var_node = assignment_node.children[0]
        expr_node = assignment_node.children[1]
        
        self.code.append(f"// Atribuição para {var_node.value}")
        
        # Gera código para a expressão
        self.generate_expression(expr_node)
        
        # Armazena o resultado na variável
        if var_node.type == 'variable':
            var_name = var_node.value
            if var_name in self.global_vars:
                var_index = self.global_vars[var_name]
                self.code.append(f"storeg {var_index}")
            else:
                self.code.append(f"// Erro: variável {var_name} não encontrada")
        elif var_node.type == 'array_access':
            # Para arrays, precisa calcular o índice
            array_name = var_node.value
            if array_name in self.global_vars:
                base_index = self.global_vars[array_name]
                # Gera código para o índice do array
                self.generate_expression(var_node.children[0])
                # Adiciona o índice base
                self.code.append(f"pushi {base_index}")
                self.code.append("add")
                # Armazena no endereço calculado
                self.code.append("storen")
        
        self.code.append("")
    
    def generate_if_statement(self, if_node):
        """Gera código para um comando if."""
        condition_node = if_node.children[0]
        then_node = if_node.children[1]
        
        # Labels para controle de fluxo
        else_label = self.new_label("ELSE")
        end_label = self.new_label("ENDIF")
        
        self.code.append("// Comando IF")
        
        # Gera código para a condição
        self.generate_expression(condition_node)
        
        # Salta para else se falso (condição = 0)
        self.code.append(f"jz {else_label}")
        
        # Código do bloco then
        self.generate_statement(then_node)
        self.code.append(f"jump {end_label}")
        
        # Label do else
        self.code.append(f"{else_label}:")
        
        # Código do bloco else (se existir)
        if len(if_node.children) > 2:
            else_node = if_node.children[2]
            self.generate_statement(else_node)
        
        # Label do fim
        self.code.append(f"{end_label}:")
        self.code.append("")
    
    def generate_while_statement(self, while_node):
        """Gera código para um comando while."""
        condition_node = while_node.children[0]
        body_node = while_node.children[1]
        
        # Labels para o loop
        start_label = self.new_label("WHILE")
        end_label = self.new_label("ENDWHILE")
        
        self.code.append("// Início do ciclo while")
        self.code.append(f"{start_label}:")
        
        # Gera código para a condição
        self.code.append("// Condição de permanência no ciclo")
        self.generate_expression(condition_node)
        
        # Salta para o fim se falso
        self.code.append(f"jz {end_label}")
        
        # Código do corpo do loop
        self.generate_statement(body_node)
        
        # Volta para o início
        self.code.append(f"jump {start_label}")
        
        # Label do fim
        self.code.append(f"{end_label}:")
        self.code.append("// Fim do ciclo while")
        self.code.append("")
    
    def generate_for_statement(self, for_node):
        """Gera código para um comando for."""
        var_name = for_node.value[0]
        direction = for_node.value[1]  # 'to' ou 'downto'
        start_expr = for_node.children[0]
        end_expr = for_node.children[1]
        body_node = for_node.children[2]
        
        # Labels para o loop
        start_label = self.new_label("FOR")
        end_label = self.new_label("ENDFOR")
        
        self.code.append(f"// Ciclo FOR {var_name}")
        
        # Inicializa a variável de controle
        self.generate_expression(start_expr)
        if var_name in self.global_vars:
            var_index = self.global_vars[var_name]
            self.code.append(f"storeg {var_index}")
        
        # Label do início do loop
        self.code.append(f"{start_label}:")
        
        # Verifica a condição do loop
        # Para 'to': continua enquanto i <= n (sai quando i > n)
        # Para 'downto': continua enquanto i >= n (sai quando i < n)
        if var_name in self.global_vars:
            var_index = self.global_vars[var_name]
            self.code.append(f"pushg {var_index}")
        
        self.generate_expression(end_expr)
        
        if direction == 'to':
            # Queremos continuar enquanto i <= n
            # Então saímos quando i > n
            self.code.append("sup")  # i > n?
            self.code.append(f"not") # inverte: agora é i <= n
            self.code.append(f"jz {end_label}")  # sai se i <= n for falso (ou seja, i > n)
        else:  # downto
            # Queremos continuar enquanto i >= n
            # Então saímos quando i < n
            self.code.append("inf")  # i < n?
            self.code.append(f"not") # inverte: agora é i >= n
            self.code.append(f"jz {end_label}")  # sai se i >= n for falso (ou seja, i < n)
        
        # Código do corpo do loop
        self.generate_statement(body_node)
        
        # Incrementa/decrementa a variável de controle
        if var_name in self.global_vars:
            var_index = self.global_vars[var_name]
            self.code.append(f"pushg {var_index}")
        
        self.code.append("pushi 1")
        
        if direction == 'to':
            self.code.append("add")
        else:  # downto
            self.code.append("sub")
        
        if var_name in self.global_vars:
            var_index = self.global_vars[var_name]
            self.code.append(f"storeg {var_index}")
        
        # Volta para o início
        self.code.append(f"jump {start_label}")
        
        # Label do fim
        self.code.append(f"{end_label}:")
        self.code.append("")
    
    def generate_write_statement(self, write_node):
        """Gera código para write/writeln."""
        self.code.append("// Comando de escrita")
        
        if len(write_node.children) == 0:
            # writeln sem argumentos
            self.code.append("writeln")
            self.code.append("")
            return
        
        # Escreve cada expressão
        expr_list_node = write_node.children[0]
        for expr_node in expr_list_node.children:
            self.generate_expression(expr_node)
            
            # Determina o tipo da expressão para escolher a instrução correta
            if expr_node.type == 'string':
                self.code.append("writes")
            elif expr_node.type == 'number':
                if isinstance(expr_node.value, float):
                    self.code.append("writef")
                else:
                    self.code.append("writei")
            else:
                # Para variáveis, assume inteiro por padrão
                self.code.append("writei")
        
        # Se for writeln, adiciona quebra de linha
        if write_node.value == 'WRITELN':
            self.code.append("writeln")
        
        self.code.append("")
    
    def generate_read_statement(self, read_node):
        """Gera código para read/readln."""
        if len(read_node.children) == 0:
            return
        
        self.code.append("// Comando de leitura")
        
        # Lê cada variável
        var_list_node = read_node.children[0]
        for var_node in var_list_node.children:
            if var_node.type == 'variable':
                var_name = var_node.value
                self.code.append("read")
                self.code.append("atoi")  # Converte string para inteiro
                
                if var_name in self.global_vars:
                    var_index = self.global_vars[var_name]
                    self.code.append(f"storeg {var_index}")
        
        self.code.append("")
    
    def generate_expression(self, expr_node):
        """Gera código para uma expressão."""
        if expr_node is None:
            return
        
        if expr_node.type == 'number':
            # Constante numérica
            if isinstance(expr_node.value, int):
                self.code.append(f"pushi {expr_node.value}")
            else:
                self.code.append(f"pushf {expr_node.value}")
        
        elif expr_node.type == 'string':
            # Constante string
            self.code.append(f'pushs "{expr_node.value}"')
        
        elif expr_node.type == 'boolean':
            # Constante booleana
            value = 1 if expr_node.value.lower() == 'true' else 0
            self.code.append(f"pushi {value}")
        
        elif expr_node.type == 'variable':
            # Variável
            var_name = expr_node.value
            if var_name in self.global_vars:
                var_index = self.global_vars[var_name]
                self.code.append(f"pushg {var_index}")
            else:
                self.code.append(f"// Erro: variável {var_name} não encontrada")
        
        elif expr_node.type == 'array_access':
            # Acesso a array
            array_name = expr_node.value
            if array_name in self.global_vars:
                base_index = self.global_vars[array_name]
                # Gera código para o índice
                self.generate_expression(expr_node.children[0])
                # Adiciona o índice base
                self.code.append(f"pushi {base_index}")
                self.code.append("add")
                # Carrega o valor do endereço calculado
                self.code.append("loadn")
        
        elif expr_node.type == 'binary_op':
            # Operação binária
            left_node = expr_node.children[0]
            right_node = expr_node.children[1]
            operator = expr_node.value
            
            # Debug: mostra qual operação está sendo processada
            self.code.append(f"// Operação binária: {operator}")
            
            # Gera código para os operandos (ordem importante para a pilha)
            self.generate_expression(left_node)
            self.generate_expression(right_node)
            
            # Mapa de operadores estendido para reconhecer todos os formatos possíveis
            op_map = {
                # Aritméticos
                'PLUS': 'add',
                '+': 'add',
                'MINUS': 'sub', 
                '-': 'sub',
                'TIMES': 'mul',
                '*': 'mul',
                'DIVIDE': 'div',
                '/': 'div',
                'DIV': 'div',
                'MOD': 'mod',
                '%': 'mod',
                
                # Comparação
                'EQ': 'equal',
                '=': 'equal',
                'NEQ': 'equal\nnot',
                '<>': 'equal\nnot',
                'LT': 'inf',
                '<': 'inf',
                'GT': 'sup',
                '>': 'sup',
                'LTE': 'infeq',
                '<=': 'infeq',
                'GTE': 'supeq',
                '>=': 'supeq',
                
                # Lógicos
                'AND': 'and',
                'OR': 'or',
                'NOT': 'not'
            }
            
            # Trata o operador em diferentes formatos possíveis
            op_code = None
            if operator in op_map:
                op_code = op_map[operator]
            else:
                # Tenta converter para letras maiúsculas
                op_upper = operator.upper()
                if op_upper in op_map:
                    op_code = op_map[op_upper]
            
            if op_code:
                if operator == 'NEQ' or operator == '<>':
                    self.code.append("equal")
                    self.code.append("not")
                else:
                    self.code.append(op_code)
            else:
                self.code.append(f"// ERRO: Operador '{operator}' não reconhecido")
                # Como fallback, assume que é uma comparação > (sup)
                if operator == '>' or operator.upper() == 'GT':
                    self.code.append("sup")
                # Outros operadores de comparação como fallback
                elif operator == '<' or operator.upper() == 'LT':
                    self.code.append("inf")
                elif operator == '>=' or operator.upper() == 'GTE':
                    self.code.append("supeq")
                elif operator == '<=' or operator.upper() == 'LTE':
                    self.code.append("infeq")
    
        elif expr_node.type == 'unary_op':
            # Operação unária
            operand_node = expr_node.children[0]
            operator = expr_node.value
            
            self.generate_expression(operand_node)
            
            if operator == 'MINUS' or operator == '-':
                # Multiplica por -1
                self.code.append("pushi -1")
                self.code.append("mul")
            elif operator == 'NOT' or operator.upper() == 'NOT':
                self.code.append("not")
    
    def new_label(self, prefix="L"):
        """Gera um novo rótulo."""
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label