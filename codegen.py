# codegen.py - Gerador de código para a máquina virtual
from symboltable import SymbolTable

class CodeGenerator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function = None
    
    def generate(self, ast):
        """Gera código a partir da AST."""
        if ast is None:
            return []
        
        # Inicia a geração a partir do nó raiz (programa)
        if ast.type == 'program':
            # Gera código para o programa principal
            self.code.append(f"# Código para o programa {ast.value}")
            
            # Gera código para as declarações
            declarations = ast.children[0]
            self.generate_declarations(declarations)
            
            # Gera código para o bloco principal
            main_block = ast.children[1]
            self.generate_compound_statement(main_block)
            
            # Adiciona instrução de parada
            self.code.append("HALT")
            
            return self.code
        else:
            print(f"Erro: Nó raiz não é um programa")
            return []
    
    def generate_declarations(self, declarations_node):
        """Gera código para as declarações."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return
        
        # Não precisamos gerar código para declarações de variáveis,
        # pois a alocação de memória é feita pela máquina virtual.
        # Mas precisamos gerar código para funções e procedimentos.
        
        for declaration in declarations_node.children:
            if declaration.type == 'function_declaration':
                self.generate_function(declaration)
            elif declaration.type == 'procedure_declaration':
                self.generate_procedure(declaration)
    
    def generate_function(self, function_node):
        """Gera código para uma função."""
        function_name = function_node.value
        
        # Salva o nome da função atual
        old_function = self.current_function
        self.current_function = function_name
        
        # Gera o rótulo da função
        self.code.append(f"\n# Função {function_name}")
        self.code.append(f"LABEL {function_name}")
        
        # Gera código para o prólogo da função
        self.code.append("ENTER")
        
        # Gera código para as declarações locais
        local_declarations = function_node.children[2]
        self.generate_declarations(local_declarations)
        
        # Gera código para o corpo da função
        body_node = function_node.children[3]
        self.generate_compound_statement(body_node)
        
        # Gera código para o epílogo da função
        self.code.append("LEAVE")
        self.code.append("RET")
        
        # Restaura o nome da função anterior
        self.current_function = old_function
    
    def generate_procedure(self, procedure_node):
        """Gera código para um procedimento."""
        procedure_name = procedure_node.value
        
        # Salva o nome da função atual
        old_function = self.current_function
        self.current_function = procedure_name
        
        # Gera o rótulo do procedimento
        self.code.append(f"\n# Procedimento {procedure_name}")
        self.code.append(f"LABEL {procedure_name}")
        
        # Gera código para o prólogo do procedimento
        self.code.append("ENTER")
        
        # Gera código para as declarações locais
        local_declarations = procedure_node.children[1]
        self.generate_declarations(local_declarations)
        
        # Gera código para o corpo do procedimento
        body_node = procedure_node.children[2]
        self.generate_compound_statement(body_node)
        
        # Gera código para o epílogo do procedimento
        self.code.append("LEAVE")
        self.code.append("RET")
        
        # Restaura o nome da função anterior
        self.current_function = old_function
    
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
        elif statement_node.type == 'procedure_call':
            self.generate_procedure_call(statement_node)
        elif statement_node.type == 'read_statement':
            self.generate_read_statement(statement_node)
        elif statement_node.type == 'write_statement':
            self.generate_write_statement(statement_node)
    
    def generate_assignment(self, assignment_node):
        """Gera código para uma atribuição."""
        var_node = assignment_node.children[0]
        expr_node = assignment_node.children[1]
        
        # Gera código para a expressão
        expr_result = self.generate_expression(expr_node)
        
        # Gera código para a atribuição
        if var_node.type == 'variable':
            var_name = var_node.value
            
            # Se estamos em uma função e a variável tem o mesmo nome da função,
            # estamos atribuindo o valor de retorno
            if self.current_function and var_name == self.current_function:
                self.code.append(f"STORE_RET {expr_result}")
            else:
                self.code.append(f"STORE {var_name}, {expr_result}")
        
        elif var_node.type == 'array_access':
            array_name = var_node.value
            index_result = self.generate_expression(var_node.children[0])
            self.code.append(f"STORE_ARRAY {array_name}, {index_result}, {expr_result}")
    
    def generate_if_statement(self, if_node):
        """Gera código para um comando if."""
        condition_node = if_node.children[0]
        then_node = if_node.children[1]
        
        # Gera rótulos para os blocos then e else
        else_label = self.new_label()
        end_label = self.new_label()
        
        # Gera código para a condição
        condition_result = self.generate_expression(condition_node)
        
        # Gera salto condicional para o bloco else
        self.code.append(f"JZ {condition_result}, {else_label}")
        
        # Gera código para o bloco then
        self.generate_statement(then_node)
        
        # Gera salto para o fim do if
        self.code.append(f"JMP {end_label}")
        
        # Gera código para o bloco else, se existir
        self.code.append(f"LABEL {else_label}")
        if len(if_node.children) > 2:
            else_node = if_node.children[2]
            self.generate_statement(else_node)
        
        # Gera rótulo para o fim do if
        self.code.append(f"LABEL {end_label}")
    
    def generate_while_statement(self, while_node):
        """Gera código para um comando while."""
        condition_node = while_node.children[0]
        body_node = while_node.children[1]
        
        # Gera rótulos para o início e fim do loop
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Gera rótulo para o início do loop
        self.code.append(f"LABEL {start_label}")
        
        # Gera código para a condição
        condition_result = self.generate_expression(condition_node)
        
        # Gera salto condicional para o fim do loop
        self.code.append(f"JZ {condition_result}, {end_label}")
        
        # Gera código para o corpo do loop
        self.generate_statement(body_node)
        
        # Gera salto para o início do loop
        self.code.append(f"JMP {start_label}")
        
        # Gera rótulo para o fim do loop
        self.code.append(f"LABEL {end_label}")
    
    def generate_for_statement(self, for_node):
        """Gera código para um comando for."""
        var_name = for_node.value[0]
        direction = for_node.value[1]  # 'to' ou 'downto'
        start_expr = for_node.children[0]
        end_expr = for_node.children[1]
        body_node = for_node.children[2]
        
        # Gera rótulos para o início e fim do loop
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Gera código para a expressão inicial
        start_result = self.generate_expression(start_expr)
        
        # Inicializa a variável de controle
        self.code.append(f"STORE {var_name}, {start_result}")
        
        # Gera código para a expressão final (apenas uma vez)
        end_result = self.generate_expression(end_expr)
        end_temp = self.new_temp()
        self.code.append(f"STORE {end_temp}, {end_result}")
        
        # Gera rótulo para o início do loop
        self.code.append(f"LABEL {start_label}")
        
        # Gera código para a condição do loop
        if direction == 'to':
            self.code.append(f"LOAD {var_name}")
            self.code.append(f"LOAD {end_temp}")
            self.code.append(f"GT")
            condition_result = self.new_temp()
            self.code.append(f"STORE {condition_result}, POP")
        else:  # downto
            self.code.append(f"LOAD {var_name}")
            self.code.append(f"LOAD {end_temp}")
            self.code.append(f"LT")
            condition_result = self.new_temp()
            self.code.append(f"STORE {condition_result}, POP")
        
        # Gera salto condicional para o fim do loop
        self.code.append(f"JNZ {condition_result}, {end_label}")
        
        # Gera código para o corpo do loop
        self.generate_statement(body_node)
        
        # Incrementa ou decrementa a variável de controle
        if direction == 'to':
            self.code.append(f"LOAD {var_name}")
            self.code.append(f"PUSH 1")
            self.code.append(f"ADD")
            self.code.append(f"STORE {var_name}, POP")
        else:  # downto
            self.code.append(f"LOAD {var_name}")
            self.code.append(f"PUSH 1")
            self.code.append(f"SUB")
            self.code.append(f"STORE {var_name}, POP")
        
        # Gera salto para o início do loop
        self.code.append(f"JMP {start_label}")
        
        # Gera rótulo para o fim do loop
        self.code.append(f"LABEL {end_label}")
    
    def generate_procedure_call(self, call_node):
        """Gera código para uma chamada de procedimento."""
        proc_name = call_node.value
        
        # Gera código para os argumentos, se houver
        if len(call_node.children) > 0:
            args_node = call_node.children[0]
            self.generate_arguments(args_node)
        
        # Gera código para a chamada
        self.code.append(f"CALL {proc_name}")
    
    def generate_read_statement(self, read_node):
        """Gera código para um comando read/readln."""
        # Se não tiver argumentos, é um readln simples
        if len(read_node.children) == 0:
            self.code.append("READLN")
            return
        
        # Gera código para ler cada variável
        var_list_node = read_node.children[0]
        for var_node in var_list_node.children:
            if var_node.type == 'variable':
                var_name = var_node.value
                self.code.append(f"READ {var_name}")
            elif var_node.type == 'array_access':
                array_name = var_node.value
                index_result = self.generate_expression(var_node.children[0])
                self.code.append(f"READ_ARRAY {array_name}, {index_result}")
        
        # Se for readln, adiciona uma leitura de linha
        if read_node.value == 'READLN':
            self.code.append("READLN")
    
    def generate_write_statement(self, write_node):
        """Gera código para um comando write/writeln."""
        # Se não tiver argumentos, é um writeln simples
        if len(write_node.children) == 0:
            self.code.append("WRITELN")
            return
        
        # Gera código para escrever cada expressão
        expr_list_node = write_node.children[0]
        for expr_node in expr_list_node.children:
            expr_result = self.generate_expression(expr_node)
            self.code.append(f"WRITE {expr_result}")
        
        # Se for writeln, adiciona uma quebra de linha
        if write_node.value == 'WRITELN':
            self.code.append("WRITELN")
    
    def generate_arguments(self, args_node):
        """Gera código para os argumentos de uma chamada de função/procedimento."""
        if args_node.type != 'argument_list':
            return
        
        # Gera código para cada argumento
        for arg_node in args_node.children:
            arg_result = self.generate_expression(arg_node)
            self.code.append(f"PARAM {arg_result}")
    
    def generate_expression(self, expr_node):
        """Gera código para uma expressão e retorna o resultado."""
        if expr_node is None:
            return None
        
        if expr_node.type == 'number':
            # Constante numérica
            temp = self.new_temp()
            self.code.append(f"PUSH {expr_node.value}")
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'string':
            # Constante string
            temp = self.new_temp()
            self.code.append(f"PUSH \"{expr_node.value}\"")
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'boolean':
            # Constante booleana
            temp = self.new_temp()
            value = 1 if expr_node.value.lower() == 'true' else 0
            self.code.append(f"PUSH {value}")
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'variable':
            # Variável
            var_name = expr_node.value
            temp = self.new_temp()
            self.code.append(f"LOAD {var_name}")
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'array_access':
            # Acesso a array
            array_name = expr_node.value
            index_result = self.generate_expression(expr_node.children[0])
            temp = self.new_temp()
            self.code.append(f"LOAD_ARRAY {array_name}, {index_result}")
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'function_call':
            # Chamada de função
            func_name = expr_node.value
            
            # Gera código para os argumentos, se houver
            if len(expr_node.children) > 0:
                args_node = expr_node.children[0]
                self.generate_arguments(args_node)
            
            # Gera código para a chamada
            self.code.append(f"CALL {func_name}")
            
            # Armazena o valor de retorno
            temp = self.new_temp()
            self.code.append(f"LOAD_RET")
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'binary_op':
            # Operação binária
            left_node = expr_node.children[0]
            right_node = expr_node.children[1]
            operator = expr_node.value
            
            # Gera código para os operandos
            left_result = self.generate_expression(left_node)
            right_result = self.generate_expression(right_node)
            
            # Gera código para a operação
            temp = self.new_temp()
            self.code.append(f"LOAD {left_result}")
            self.code.append(f"LOAD {right_result}")
            
            if operator == 'PLUS':
                self.code.append("ADD")
            elif operator == 'MINUS':
                self.code.append("SUB")
            elif operator == 'TIMES':
                self.code.append("MUL")
            elif operator == 'DIVIDE':
                self.code.append("DIV")
            elif operator == 'DIV':
                self.code.append("IDIV")
            elif operator == 'MOD':
                self.code.append("MOD")
            elif operator == 'EQ':
                self.code.append("EQ")
            elif operator == 'NEQ':
                self.code.append("NEQ")
            elif operator == 'LT':
                self.code.append("LT")
            elif operator == 'GT':
                self.code.append("GT")
            elif operator == 'LTE':
                self.code.append("LTE")
            elif operator == 'GTE':
                self.code.append("GTE")
            elif operator == 'AND':
                self.code.append("AND")
            elif operator == 'OR':
                self.code.append("OR")
            
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        elif expr_node.type == 'unary_op':
            # Operação unária
            operand_node = expr_node.children[0]
            operator = expr_node.value
            
            # Gera código para o operando
            operand_result = self.generate_expression(operand_node)
            
            # Gera código para a operação
            temp = self.new_temp()
            self.code.append(f"LOAD {operand_result}")
            
            if operator == 'MINUS':
                self.code.append("NEG")
            elif operator == 'NOT':
                self.code.append("NOT")
            
            self.code.append(f"STORE {temp}, POP")
            return temp
        
        return None
    
    def new_temp(self):
        """Gera um novo nome de variável temporária."""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp
    
    def new_label(self):
        """Gera um novo rótulo."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

# Exemplo de uso
if __name__ == "__main__":
    from parser import parse_code
    from semantic import SemanticAnalyzer
    
    test_code = """
    program Test;
    var
        x, y: integer;
        z: real;
    begin
        x := 10;
        y := 20;
        z := x + y;
        if x > y then
            writeln('x é maior')
        else
            writeln('y é maior ou igual');
    end.
    """
    
    print("Analisando o código:")
    print(test_code)
    
    ast = parse_code(test_code)
    if ast:
        # Análise semântica
        analyzer = SemanticAnalyzer()
        if analyzer.analyze(ast):
            # Geração de código
            generator = CodeGenerator(analyzer.symbol_table)
            code = generator.generate(ast)
            
            print("\n=== CÓDIGO GERADO ===")
            for line in code:
                print(line)
        else:
            print("Falha na análise semântica")
    else:
        print("Falha no parsing")