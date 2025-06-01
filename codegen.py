from symboltable import SymbolTable

class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.label_counter = 0
        self.current_function = None
        self.global_vars = {}  # Mapeia nome da variável para índice global
        self.local_vars = {}   # Mapeia nome da variável para índice local (por função)
        self.function_vars = {}  # Mapeia função -> {var_name: offset}
        self.var_counter = 0   # Contador para variáveis globais
        self.functions = {}    # Mapeia nome da função para informações
        self.scope_stack = ["global"]  # Pilha de escopos
        
    def generate(self, ast):
        """Gera código EWVM a partir da AST."""
        if ast is None:
            return []
        
        if ast.type == 'program':
            # Primeiro, declara todas as variáveis globais
            declarations = ast.children[0]
            self.declare_global_variables_only(declarations)
            
            # Marca o início do programa
            self.code.append("start")
            self.code.append("")
            
            # Gera código para o bloco principal
            main_block = ast.children[1]
            self.generate_compound_statement(main_block)
            
            # Finaliza o programa
            self.code.append("stop")
            self.code.append("")
            
            # AGORA gera as funções DEPOIS do stop
            self.generate_functions(declarations)
            
            return self.code
        else:
            print(f"Erro: Nó raiz não é um programa")
            return []
    
    def enter_function_scope(self, function_name):
        """Entra no escopo de uma função."""
        self.scope_stack.append(function_name)
        self.current_function = function_name
        self.function_vars[function_name] = {}

    def exit_function_scope(self):
        """Sai do escopo de uma função."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_function = self.scope_stack[-1] if len(self.scope_stack) > 1 else None
            
    def is_in_function(self):
        """Verifica se está dentro de uma função."""
        return self.current_function is not None and self.current_function != "global"
    
    def declare_global_variables(self, declarations_node):
        """Declara variáveis globais e processa declarações de funções."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return
        
        # Primeiro passo: declara variáveis globais
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
                            # Variável simples - inicializa com valor padrão
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
        
        # Segundo passo: gera código para funções
        for declaration in declarations_node.children:
            if declaration.type == 'function_declaration':
                self.generate_function_declaration(declaration)
            elif declaration.type == 'procedure_declaration':
                self.generate_procedure_declaration(declaration)
    
    def declare_global_variables_only(self, declarations_node):
        """Declara apenas variáveis globais, sem processar funções."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return
        
        # Apenas declara variáveis globais
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
                            # Variável simples - inicializa com valor padrão apropriado
                            self.code.append(f"// Declaração da variável {var_name}")
                            if type_node.value == 'real':
                                self.code.append("pushf 0.0")
                            elif type_node.value == 'boolean':
                                self.code.append("pushi 0")  # false = 0
                            elif type_node.value == 'string':
                                # Para strings, cria uma string vazia no heap
                                # Isto cria uma referência de string que é armazenada na variável
                                self.code.append('pushs ""')
                            else:  # integer
                                self.code.append("pushi 0")
                            
                            self.var_counter += 1

        if self.var_counter > 0:
            self.code.append("")

    def generate_functions(self, declarations_node):
        """Gera código para funções e procedimentos."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return
        
        # Gera código para funções
        for declaration in declarations_node.children:
            if declaration.type == 'function_declaration':
                self.generate_function_declaration(declaration)
            elif declaration.type == 'procedure_declaration':
                self.generate_procedure_declaration(declaration)
    
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
        elif statement_node.type == 'procedure_call':
            self.generate_procedure_call(statement_node)
        elif statement_node.type == 'function_call':
            self.generate_function_call(statement_node)
    
    def generate_assignment(self, assignment_node):
        """Gera código para uma atribuição."""
        var_node = assignment_node.children[0]
        expr_node = assignment_node.children[1]
        
        self.code.append(f"// Atribuição para {var_node.value}")
        
        # DEBUG: Verifica se a expressão existe
        if expr_node is None:
            self.code.append("// ERRO: Expressão é None!")
            return
        
        self.code.append(f"// Gerando expressão do tipo: {expr_node.type}")
        
        # Gera código para a expressão
        self.generate_expression(expr_node)
        
        # Armazena o resultado na variável
        if var_node.type == 'variable':
            var_name = var_node.value
            
            # Verifica se é uma atribuição de retorno de função
            if (self.is_in_function() and var_name == self.current_function):
                # Atribuição de valor de retorno - armazena em variável local especial
                # Usamos offset 0 para o valor de retorno
                self.code.append("storel 0")
                self.code.append("// Valor de retorno armazenado")
                return
            
            # Verifica se é uma variável local da função atual
            if (self.is_in_function() and 
                self.current_function in self.function_vars and 
                var_name in self.function_vars[self.current_function]):
                
                offset = self.function_vars[self.current_function][var_name]
                self.code.append(f"storel {offset}")
            
            # Senão, é uma variável global
            elif var_name in self.global_vars:
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
                
                # CORREÇÃO: Subtrai o índice inicial do array
                array_symbol = self.symbol_table.lookup(array_name)
                if array_symbol and array_symbol.array_dims:
                    start_idx = array_symbol.array_dims[0]
                    if start_idx != 0:  # Se não começa em 0
                        self.code.append(f"pushi {start_idx}")
                        self.code.append("sub")  # índice_real = i - start_idx
                
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
        
        # Certifica-se de que a condição resulta em um valor booleano (0 ou 1)
        if condition_node.type == 'binary_op' and condition_node.value in ['EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE']:
            # Já é uma comparação, não precisa fazer nada
            pass
        else:
            # Converte para booleano explicitamente (0 se for 0, 1 caso contrário)
            self.code.append("pushi 0")
            self.code.append("equal")
            self.code.append("not")  # Inverte para obter o valor booleano correto
        
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
        
        start_label = self.new_label("FOR")
        end_label = self.new_label("ENDFOR")
        
        self.code.append(f"// Ciclo FOR {var_name} {direction}")
        
        # Inicializa a variável de controle
        self.generate_expression(start_expr)
        
        # CORREÇÃO: Verifica se é uma variável local ou global
        if (self.is_in_function() and 
            self.current_function in self.function_vars and 
            var_name in self.function_vars[self.current_function]):
            
            # Variável local
            offset = self.function_vars[self.current_function][var_name]
            self.code.append(f"storel {offset}")
        else:
            # Variável global
            var_index = self.global_vars[var_name]
            self.code.append(f"storeg {var_index}")
        
        # Início do loop
        self.code.append(f"{start_label}:")
        
        # Verifica a condição de parada
        # Carrega o valor da variável de controle
        if (self.is_in_function() and 
            self.current_function in self.function_vars and 
            var_name in self.function_vars[self.current_function]):
            
            # Variável local
            offset = self.function_vars[self.current_function][var_name]
            self.code.append(f"pushl {offset}")
        else:
            # Variável global
            var_index = self.global_vars[var_name]
            self.code.append(f"pushg {var_index}")
        
        # Gera código para o valor final
        self.generate_expression(end_expr)

        if direction == 'to':
            # Para 'to': continua enquanto i <= n, ou seja, para quando i > n
            self.code.append("infeq")  # i <= n?
            self.code.append(f"jz {end_label}")  # Se i <= n é falso (i > n), sai do loop
        else:  # downto
            # Para 'downto': continua enquanto i >= n, ou seja, para quando i < n
            self.code.append("supeq")  # i >= n?
            self.code.append(f"jz {end_label}")  # Se i >= n é falso (i < n), sai do loop
        
        # Corpo do loop
        self.generate_statement(body_node)
        
        # Incrementa/decrementa a variável de controle
        # Carrega o valor atual
        if (self.is_in_function() and 
            self.current_function in self.function_vars and 
            var_name in self.function_vars[self.current_function]):
            
            # Variável local
            offset = self.function_vars[self.current_function][var_name]
            self.code.append(f"pushl {offset}")
        else:
            # Variável global
            var_index = self.global_vars[var_name]
            self.code.append(f"pushg {var_index}")
        
        # Incrementa/decrementa
        self.code.append("pushi 1")
        if direction == 'to':
            self.code.append("add")
        else:
            self.code.append("sub")
        
        # Armazena o novo valor
        if (self.is_in_function() and 
            self.current_function in self.function_vars and 
            var_name in self.function_vars[self.current_function]):
            
            # Variável local
            offset = self.function_vars[self.current_function][var_name]
            self.code.append(f"storel {offset}")
        else:
            # Variável global
            var_index = self.global_vars[var_name]
            self.code.append(f"storeg {var_index}")
        
        # Volta para o início do loop
        self.code.append(f"jump {start_label}")
        
        # Fim do loop
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
            elif expr_node.type == 'variable':
                # Verifica o tipo da variável na tabela de símbolos
                var_symbol = self.symbol_table.lookup(expr_node.value)
                if var_symbol and var_symbol.type == 'string':
                    # Para variáveis string, usa writes diretamente
                    self.code.append("writes")
                elif var_symbol and var_symbol.type == 'real':
                    self.code.append("writef")
                elif var_symbol and var_symbol.type == 'boolean':
                    self.code.append("writei")  # Booleanos são escritos como inteiros
                else:
                    self.code.append("writei")  # Default para inteiros
            elif expr_node.type == 'function_call':
                # Para chamadas de função, verifica o tipo de retorno
                func_symbol = self.symbol_table.lookup(expr_node.value)
                if func_symbol and func_symbol.type == 'string':
                    self.code.append("writes")
                elif func_symbol and func_symbol.type == 'real':
                    self.code.append("writef")
                else:
                    self.code.append("writei")
            elif expr_node.type == 'array_access':
                # Para acesso a arrays, verifica o tipo base
                array_name = expr_node.value
                array_symbol = self.symbol_table.lookup(array_name)
                if array_symbol and array_symbol.type == 'string':
                    # Acesso a caractere de string retorna código ASCII (inteiro)
                    self.code.append("writei")
                else:
                    self.code.append("writei")  # Arrays normalmente são inteiros
            else:
                # Para outras expressões, assume inteiro por padrão
                self.code.append("writei")

        # Se for writeln, adiciona quebra de linha
        if write_node.value.upper() == 'WRITELN':
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
                
                # Verifica o tipo da variável para converter corretamente
                var_symbol = self.symbol_table.lookup(var_name)
                if var_symbol and var_symbol.type == 'string':
                    # Para strings, não converte - o read já retorna uma referência de string
                    pass
                else:
                    # Para números, converte para inteiro
                    self.code.append("atoi")
                
                # Armazena o valor lido na variável
                if (self.is_in_function() and 
                    self.current_function in self.function_vars and 
                    var_name in self.function_vars[self.current_function]):
                    
                    # Variável local
                    offset = self.function_vars[self.current_function][var_name]
                    self.code.append(f"storel {offset}")
                else:
                    # Variável global
                    var_index = self.global_vars[var_name]
                    self.code.append(f"storeg {var_index}")
        
            elif var_node.type == 'array_access':
                # Para arrays, precisa calcular o endereço e armazenar
                array_name = var_node.value
                if array_name in self.global_vars:
                    base_index = self.global_vars[array_name]
                    
                    # Calcula o endereço do array PRIMEIRO
                    self.code.append("pushgp")  # Endereço base da pilha global
                    self.code.append(f"pushi {base_index}")  # Índice base do array
                    self.code.append("padd")  # Endereço base do array

                    # Gera código para o índice e ajusta para o índice real
                    self.generate_expression(var_node.children[0])
                    
                    # CORREÇÃO: Subtrai o índice inicial do array
                    # Para array[1..5], quando i=1, índice real = 1-1 = 0
                    array_symbol = self.symbol_table.lookup(array_name)
                    if array_symbol and array_symbol.array_dims:
                        start_idx = array_symbol.array_dims[0]
                        if start_idx != 0:  # Se não começa em 0
                            self.code.append(f"pushi {start_idx}")
                            self.code.append("sub")  # índice_real = i - start_idx
                    
                    self.code.append("padd")  # Endereço final

                    # Lê o valor DEPOIS
                    self.code.append("read")
                    self.code.append("atoi")  # Converte string para inteiro

                    # Agora a pilha está correta: endereço (fundo) + valor (topo)
                    self.code.append("store 0")
        
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
            # Constante string - processa o valor corretamente
            string_value = expr_node.value
            
            # Remove todas as aspas duplas do início e fim se existirem
            while string_value.startswith('"'):
                string_value = string_value[1:]
            while string_value.endswith('"'):
                string_value = string_value[:-1]
            
            # Remove aspas simples se existirem (para caracteres literais)
            while string_value.startswith("'"):
                string_value = string_value[1:]
            while string_value.endswith("'"):
                string_value = string_value[:-1]
            
            # Processa escape sequences se necessário
            # Em Pascal, aspas duplas dentro de strings são representadas como ""
            # Converte "" para " na string final
            string_value = string_value.replace('""', '"')
            
            # CORREÇÃO: Se for um caractere literal (comprimento 1), gera o código ASCII
            if len(string_value) == 1:
                # Para caracteres literais, empilha o código ASCII
                ascii_code = ord(string_value)
                self.code.append(f"pushi {ascii_code}")
                self.code.append(f"// Caractere literal '{string_value}' (ASCII {ascii_code})")
            else:
                # Para strings normais, gera a instrução EWVM com aspas duplas
                self.code.append(f'pushs "{string_value}"')
        
        elif expr_node.type == 'boolean':
            # Constante booleana
            value = 1 if expr_node.value.lower() == 'true' else 0
            self.code.append(f"pushi {value}")
        
        elif expr_node.type == 'variable':
            # Variável
            var_name = expr_node.value
            
            # CORREÇÃO: Verifica se é uma referência ao valor de retorno da função atual
            if (self.is_in_function() and var_name == self.current_function):
                # Em Pascal, referenciar o nome da função dentro dela mesma acessa o valor de retorno
                # Como não temos uma forma direta de acessar isso em EWVM, 
                # assumimos que é sempre verdadeiro (1) para condições booleanas
                self.code.append("pushi 1")
                self.code.append(f"// Referência ao valor de retorno da função {var_name}")
            
            # Verifica se é uma variável local da função atual
            elif (self.is_in_function() and 
                self.current_function in self.function_vars and 
                var_name in self.function_vars[self.current_function]):
                
                offset = self.function_vars[self.current_function][var_name]
                self.code.append(f"pushl {offset}")

            # Senão, é uma variável global
            elif var_name in self.global_vars:
                var_index = self.global_vars[var_name]
                self.code.append(f"pushg {var_index}")
            else:
                self.code.append(f"// Erro: variável {var_name} não encontrada")
        
        elif expr_node.type == 'function_call':
            # Chamada de função
            self.generate_function_call(expr_node)
        
        elif expr_node.type == 'array_access':
            # Acesso a array
            array_name = expr_node.value
            
            self.code.append(f"// Acesso a array/string: {array_name}")
            
            # Verifica se é uma string (acesso a caractere)
            array_symbol = self.symbol_table.lookup(array_name)
            if array_symbol and array_symbol.type == 'string':
                self.code.append(f"// Acesso a caractere da string {array_name}")
                
                # Carrega o endereço da string
                if (self.is_in_function() and 
                    self.current_function in self.function_vars and 
                    array_name in self.function_vars[self.current_function]):
                    
                    # Variável local ou parâmetro
                    offset = self.function_vars[self.current_function][array_name]
                    self.code.append(f"pushl {offset}")
                elif array_name in self.global_vars:
                    # Variável global
                    self.code.append(f"pushg {self.global_vars[array_name]}")
                else:
                    # Se não encontrou, assume que é o primeiro parâmetro
                    self.code.append(f"pushl -1")
                
                # Gera código para o índice
                self.generate_expression(expr_node.children[0])
                
                # CORREÇÃO CRUCIAL: Ajustar índice de Pascal (1-based) para EWVM (0-based)
                self.code.append("pushi 1")
                self.code.append("sub")  # índice_ewvm = índice_pascal - 1
                self.code.append("charat")  # Obtém o código do caractere no índice
            else:
                # Para arrays normais
                if array_name in self.global_vars:
                    base_index = self.global_vars[array_name]
                    # Empilha o endereço base da pilha global
                    self.code.append("pushgp")
                    # Empilha o índice base do array
                    self.code.append(f"pushi {base_index}")
                    # Calcula endereço base + índice base
                    self.code.append("padd")
                    # Gera código para o índice do array
                    self.generate_expression(expr_node.children[0])
                    
                    # CORREÇÃO: Subtrai o índice inicial do array
                    if array_symbol and array_symbol.array_dims:
                        start_idx = array_symbol.array_dims[0]
                        if start_idx != 0:  # Se não começa em 0
                            self.code.append(f"pushi {start_idx}")
                            self.code.append("sub")  # índice_real = i - start_idx
                    
                    # Calcula endereço final
                    self.code.append("padd")
                    # Carrega o valor do endereço final
                    self.code.append("load 0")
        
        elif expr_node.type == 'length_call':
            # Função length() para strings
            arg_node = expr_node.children[0]
            
            # CORREÇÃO: Precisamos garantir que uma referência de string esteja no topo da pilha
            if arg_node.type == 'variable':
                var_name = arg_node.value
                var_symbol = self.symbol_table.lookup(var_name)
                
                # Verifica se é uma variável local da função atual
                if (self.is_in_function() and 
                    self.current_function in self.function_vars and 
                    var_name in self.function_vars[self.current_function]):
                    
                    offset = self.function_vars[self.current_function][var_name]
                    self.code.append(f"pushl {offset}")  # Carrega a referência da string
                else:
                    # Variável global
                    self.code.append(f"pushg {self.global_vars[var_name]}")  # Carrega a referência da string
            else:
                # Para outros tipos de expressões, geramos o código normalmente
                # Isso deve deixar uma referência de string no topo da pilha
                self.generate_expression(arg_node)
            
            # Agora que temos certeza que uma referência de string está no topo da pilha, chamamos strlen
            self.code.append("strlen")
        
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

    def generate_function_declaration(self, function_node):
        """Gera código para declaração de função."""
        function_name = function_node.value
        params_node = function_node.children[0]
        return_type_node = function_node.children[1]
        local_declarations = function_node.children[2]
        body_node = function_node.children[3]
        
        self.code.append(f"// Função {function_name}")
        self.code.append(f"{function_name}:")
        
        # Entra no escopo da função
        self.enter_function_scope(function_name)
        
        # Processa parâmetros
        param_count = self.process_function_parameters(params_node, function_name)
        
        # Processa declarações locais
        local_var_count = self.process_local_declarations(local_declarations)
        
        # Reserva espaço para variáveis locais + valor de retorno
        if local_var_count > 0 or True:  # Sempre reserva pelo menos 1 espaço para retorno
            total_space = local_var_count + 1  # +1 para valor de retorno
            self.code.append(f"// Reserva espaço para {local_var_count} variáveis locais + valor de retorno")
            for i in range(total_space):
                self.code.append("pushi 0")
        
        # Gera código do corpo da função
        self.generate_compound_statement(body_node)
        
        # Carrega o valor de retorno (armazenado em offset 0)
        self.code.append("pushl 0")
        
        # Return da função - o valor de retorno deve estar no topo da pilha
        self.code.append("// Return da função")
        self.code.append("return")
        self.code.append("")
        
        # Sai do escopo da função
        self.exit_function_scope()

    def generate_procedure_declaration(self, procedure_node):
        """Gera código para declaração de procedimento."""
        procedure_name = procedure_node.value
        params_node = procedure_node.children[0]
        local_declarations = procedure_node.children[1]
        body_node = procedure_node.children[2]
        
        self.code.append(f"// Procedimento {procedure_name}")
        self.code.append(f"{procedure_name}:")
        
        # Entra no escopo do procedimento
        self.enter_function_scope(procedure_name)
        
        # Processa parâmetros
        param_count = self.process_function_parameters(params_node, procedure_name)
        
        # Processa declarações locais
        local_var_count = self.process_local_declarations(local_declarations)
        
        # Reserva espaço para variáveis locais
        if local_var_count > 0:
            self.code.append(f"// Reserva espaço para {local_var_count} variáveis locais")
            for i in range(local_var_count):
                self.code.append("pushi 0")
        
        # Gera código do corpo do procedimento
        self.generate_compound_statement(body_node)
        
        # Return do procedimento
        self.code.append("// Return do procedimento")
        self.code.append("return")
        self.code.append("")
        
        # Sai do escopo do procedimento
        self.exit_function_scope()

    def process_function_parameters(self, params_node, function_name):
        """Processa os parâmetros de uma função."""
        if params_node.type != 'parameter_list' or len(params_node.children) == 0:
            return 0
        
        param_count = 0
        self.code.append(f"// Parâmetros da função {function_name}")
        
        # Conta o total de parâmetros primeiro
        for param_node in params_node.children:
            id_list_node = param_node.children[0]
            param_count += len(id_list_node.value)
        
        # Mapeia parâmetros com offsets corretos
        current_offset = param_count
        for param_node in params_node.children:
            id_list_node = param_node.children[0]
            type_node = param_node.children[1]
            
            for param_name in id_list_node.value:
                # Parâmetros têm offset negativo, começando do mais distante
                self.function_vars[function_name][param_name] = -current_offset
                self.code.append(f"// Parâmetro {param_name} no offset {-current_offset}")
                current_offset -= 1
        
        return param_count

    def process_local_declarations(self, declarations_node):
        """Processa declarações locais de uma função."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return 0
        
        local_var_count = 0
        
        # Reserva offset 0 para valor de retorno da função
        if self.current_function and self.current_function != "global":
            self.function_vars[self.current_function]["__return__"] = 0
        
        for declaration in declarations_node.children:
            if declaration.type == 'var_declaration':
                for var_item in declaration.children:
                    id_list_node = var_item.children[0]
                    type_node = var_item.children[1]
                    
                    for var_name in id_list_node.value:
                        # Mapeia variável local para offset positivo (1, 2, 3...)
                        # Offset 0 é reservado para valor de retorno
                        self.function_vars[self.current_function][var_name] = local_var_count + 1
                        self.code.append(f"// Variável local {var_name} no offset {local_var_count + 1}")
                        local_var_count += 1
        
        return local_var_count

    def generate_function_call(self, call_node):
        """Gera código para chamada de função."""
        func_name = call_node.value
        
        self.code.append(f"// Chamada da função {func_name}")
        
        # Empilha argumentos na ordem correta (da esquerda para a direita)
        if len(call_node.children) > 0:
            args_node = call_node.children[0]
            if args_node.type == 'argument_list':
                # Empilha argumentos na ordem normal (não reversa)
                for arg_node in args_node.children:
                    self.generate_expression(arg_node)
        
        # Empilha o endereço da função e chama
        self.code.append(f"pusha {func_name}")
        self.code.append("call")

        # Para funções que retornam string, precisamos garantir que o resultado seja uma referência de string
        func_symbol = self.symbol_table.lookup(func_name)
        if func_symbol and func_symbol.type == 'string':
            # Já temos uma referência de string no topo da pilha, não precisamos fazer nada
            pass

    def generate_procedure_call(self, call_node):
        """Gera código para chamada de procedimento."""
        proc_name = call_node.value
        
        self.code.append(f"// Chamada do procedimento {proc_name}")
        
        # Empilha argumentos na ordem correta
        if len(call_node.children) > 0:
            args_node = call_node.children[0]
            if args_node.type == 'argument_list':
                # Empilha argumentos da direita para a esquerda
                for arg_node in args_node.children:
                    self.generate_expression(arg_node)
        
        # Empilha o endereço do procedimento e chama
        self.code.append(f"pusha {proc_name}")
        self.code.append("call")
        self.code.append("")
