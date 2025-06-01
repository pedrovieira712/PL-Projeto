# semantic.py - Analisador semântico para Pascal Standard (CORRIGIDO)
from symboltable import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
    
    def analyze(self, ast):
        """Analisa a árvore sintática abstrata."""
        if ast is None:
            return False
        
        # Inicia a análise a partir do nó raiz (programa)
        if ast.type == 'program':
            program_name = ast.value
            self.symbol_table.add_symbol(program_name, None, 'program', ast.line)
            
            # Analisa as declarações
            declarations = ast.children[0]
            self.analyze_declarations(declarations)
            
            # Analisa o bloco principal
            main_block = ast.children[1]
            self.analyze_compound_statement(main_block)
            
            return len(self.errors) == 0
        else:
            self.errors.append(f"Erro: Nó raiz não é um programa")
            return False
    
    def analyze_declarations(self, declarations_node):
        """Analisa as declarações (variáveis, constantes, tipos, funções, procedimentos)."""
        if declarations_node is None or declarations_node.type != 'declarations':
            return
        
        for declaration in declarations_node.children:
            if declaration.type == 'var_declaration':
                self.analyze_var_declaration(declaration)
            elif declaration.type == 'const_declaration':
                self.analyze_const_declaration(declaration)
            elif declaration.type == 'type_declaration':
                self.analyze_type_declaration(declaration)
            elif declaration.type == 'function_declaration':
                self.analyze_function_declaration(declaration)
            elif declaration.type == 'procedure_declaration':
                self.analyze_procedure_declaration(declaration)
    
    def analyze_var_declaration(self, var_declaration_node):
        """Analisa declarações de variáveis."""
        for var_item in var_declaration_node.children:
            id_list_node = var_item.children[0]
            type_node = var_item.children[1]
            
            var_type = self.get_type_name(type_node)
            
            # Adiciona cada variável à tabela de símbolos
            for var_name in id_list_node.value:
                if not self.symbol_table.add_symbol(var_name, var_type, 'variable', var_item.line):
                    self.errors.append(f"Erro na linha {var_item.line}: Variável '{var_name}' já declarada no escopo atual")
                
                # Se for um array, adiciona as dimensões
                if type_node.type == 'array_type':
                    dimensions = type_node.value  # [start, end]
                    self.symbol_table.add_array_dimensions(var_name, dimensions)
    
    def analyze_const_declaration(self, const_declaration_node):
        """Analisa declarações de constantes."""
        for const_item in const_declaration_node.children:
            const_name = const_item.value
            expr_node = const_item.children[0]
            
            # Avalia a expressão para determinar o tipo e valor
            expr_type, expr_value = self.evaluate_constant_expression(expr_node)
            
            if expr_type:
                if not self.symbol_table.add_symbol(const_name, expr_type, 'constant', const_item.line, expr_value):
                    self.errors.append(f"Erro na linha {const_item.line}: Constante '{const_name}' já declarada no escopo atual")
            else:
                self.errors.append(f"Erro na linha {const_item.line}: Expressão inválida para constante '{const_name}'")
    
    def analyze_type_declaration(self, type_declaration_node):
        """Analisa declarações de tipos."""
        for type_item in type_declaration_node.children:
            type_name = type_item.value
            type_node = type_item.children[0]
            
            type_value = self.get_type_name(type_node)
            
            if not self.symbol_table.add_symbol(type_name, type_value, 'type', type_item.line):
                self.errors.append(f"Erro na linha {type_item.line}: Tipo '{type_name}' já declarado no escopo atual")
    
    def analyze_function_declaration(self, function_node):
        """Analisa declarações de funções."""
        function_name = function_node.value
        return_type_node = function_node.children[1]
        return_type = self.get_type_name(return_type_node)
        
        # Adiciona a função à tabela de símbolos
        if not self.symbol_table.add_symbol(function_name, return_type, 'function', function_node.line):
            self.errors.append(f"Erro na linha {function_node.line}: Função '{function_name}' já declarada no escopo atual")
            return
        
        # Entra no escopo da função
        self.symbol_table.enter_scope(function_name)
        
        # Analisa os parâmetros
        params_node = function_node.children[0]
        self.analyze_parameters(params_node, function_name)
        
        # Analisa as declarações locais
        local_declarations = function_node.children[2]
        self.analyze_declarations(local_declarations)
        
        # Analisa o corpo da função
        body_node = function_node.children[3]
        self.analyze_compound_statement(body_node)
        
        # Verifica se a função tem um valor de retorno
        self.check_function_return(function_name, body_node)
        
        # Sai do escopo da função
        self.symbol_table.exit_scope()
    
    def analyze_procedure_declaration(self, procedure_node):
        """Analisa declarações de procedimentos."""
        procedure_name = procedure_node.value
        
        # Adiciona o procedimento à tabela de símbolos
        if not self.symbol_table.add_symbol(procedure_name, None, 'procedure', procedure_node.line):
            self.errors.append(f"Erro na linha {procedure_node.line}: Procedimento '{procedure_name}' já declarado no escopo atual")
            return
        
        # Entra no escopo do procedimento
        self.symbol_table.enter_scope(procedure_name)
        
        # Analisa os parâmetros
        params_node = procedure_node.children[0]
        self.analyze_parameters(params_node, procedure_name)
        
        # Analisa as declarações locais
        local_declarations = procedure_node.children[1]
        self.analyze_declarations(local_declarations)
        
        # Analisa o corpo do procedimento
        body_node = procedure_node.children[2]
        self.analyze_compound_statement(body_node)
        
        # Sai do escopo do procedimento
        self.symbol_table.exit_scope()
    
    def analyze_parameters(self, params_node, subprogram_name):
        """Analisa os parâmetros de funções e procedimentos."""
        if params_node.type != 'parameter_list':
            return
        
        for param_node in params_node.children:
            id_list_node = param_node.children[0]
            type_node = param_node.children[1]
            
            param_type = self.get_type_name(type_node)
            
            # Adiciona cada parâmetro à tabela de símbolos
            for param_name in id_list_node.value:
                if not self.symbol_table.add_symbol(param_name, param_type, 'parameter', param_node.line):
                    self.errors.append(f"Erro na linha {param_node.line}: Parâmetro '{param_name}' duplicado")
                
                # Adiciona o parâmetro à lista de parâmetros da função/procedimento
                self.symbol_table.add_parameter(subprogram_name, param_name, param_type)
    
    def analyze_compound_statement(self, compound_node):
        """Analisa um bloco de comandos."""
        if compound_node.type != 'compound_statement':
            return
        
        for statement in compound_node.children:
            self.analyze_statement(statement)
    
    def analyze_statement(self, statement_node):
        """Analisa um comando."""
        if statement_node is None:
            return
        
        if statement_node.type == 'assignment':
            self.analyze_assignment(statement_node)
        elif statement_node.type == 'compound_statement':
            self.analyze_compound_statement(statement_node)
        elif statement_node.type == 'if_statement':
            self.analyze_if_statement(statement_node)
        elif statement_node.type == 'while_statement':
            self.analyze_while_statement(statement_node)
        elif statement_node.type == 'for_statement':
            self.analyze_for_statement(statement_node)
        elif statement_node.type == 'procedure_call':
            self.analyze_procedure_call(statement_node)
        elif statement_node.type == 'read_statement':
            self.analyze_read_statement(statement_node)
        elif statement_node.type == 'write_statement':
            self.analyze_write_statement(statement_node)
    
    def analyze_assignment(self, assignment_node):
        """Analisa uma atribuição."""
        var_node = assignment_node.children[0]
        expr_node = assignment_node.children[1]
        
        # Verifica se a variável existe
        var_name = var_node.value
        var_symbol = self.symbol_table.lookup(var_name)
        
        if not var_symbol:
            self.errors.append(f"Erro na linha {var_node.line}: Variável '{var_name}' não declarada")
            return
        
        if var_symbol.kind == 'constant':
            self.errors.append(f"Erro na linha {var_node.line}: Não é possível atribuir valor à constante '{var_name}'")
            return
        
        # Verifica o tipo da expressão
        expr_type = self.check_expression_type(expr_node)
        
        # Se o tipo da expressão for None, não verifica compatibilidade
        if expr_type is None:
            return
        
        # Verifica compatibilidade de tipos
        if not self.are_types_compatible(var_symbol.type, expr_type):
            self.errors.append(f"Erro na linha {assignment_node.line}: Tipos incompatíveis na atribuição. Esperado '{var_symbol.type}', encontrado '{expr_type}'")
    
    def analyze_if_statement(self, if_node):
        """Analisa um comando if."""
        condition_node = if_node.children[0]
        then_node = if_node.children[1]
        
        # Verifica se a condição é booleana
        condition_type = self.check_expression_type(condition_node)
        if condition_type is not None and condition_type != 'boolean':
            self.errors.append(f"Erro na linha {if_node.line}: Condição do if deve ser booleana, encontrado '{condition_type}'")
        
        # Analisa o bloco then
        self.analyze_statement(then_node)
        
        # Analisa o bloco else, se existir
        if len(if_node.children) > 2:
            else_node = if_node.children[2]
            self.analyze_statement(else_node)
    
    def analyze_while_statement(self, while_node):
        """Analisa um comando while."""
        condition_node = while_node.children[0]
        body_node = while_node.children[1]
        
        # Verifica se a condição é booleana
        condition_type = self.check_expression_type(condition_node)
        if condition_type is not None and condition_type != 'boolean':
            self.errors.append(f"Erro na linha {while_node.line}: Condição do while deve ser booleana, encontrado '{condition_type}'")
        
        # Analisa o corpo do loop
        self.analyze_statement(body_node)
    
    def analyze_for_statement(self, for_node):
        """Analisa um comando for."""
        var_name = for_node.value[0]
        direction = for_node.value[1]  # 'to' ou 'downto'
        start_expr = for_node.children[0]
        end_expr = for_node.children[1]
        body_node = for_node.children[2]
        
        # Verifica se a variável de controle existe e é inteira
        var_symbol = self.symbol_table.lookup(var_name)
        if not var_symbol:
            self.errors.append(f"Erro na linha {for_node.line}: Variável de controle '{var_name}' não declarada")
        elif var_symbol.type != 'integer':
            self.errors.append(f"Erro na linha {for_node.line}: Variável de controle '{var_name}' deve ser do tipo integer")
        
        # Verifica se as expressões de início e fim são inteiras
        start_type = self.check_expression_type(start_expr)
        if start_type is not None and start_type != 'integer':
            self.errors.append(f"Erro na linha {for_node.line}: Expressão inicial do for deve ser inteira, encontrado '{start_type}'")
        
        end_type = self.check_expression_type(end_expr)
        if end_type is not None and end_type != 'integer':
            self.errors.append(f"Erro na linha {for_node.line}: Expressão final do for deve ser inteira, encontrado '{end_type}'")
        
        # Analisa o corpo do loop
        self.analyze_statement(body_node)
    
    def analyze_procedure_call(self, call_node):
        """Analisa uma chamada de procedimento."""
        proc_name = call_node.value
        
        # Verifica se o procedimento existe
        proc_symbol = self.symbol_table.lookup(proc_name)
        if not proc_symbol:
            self.errors.append(f"Erro na linha {call_node.line}: Procedimento '{proc_name}' não declarado")
            return
        
        if proc_symbol.kind != 'procedure':
            self.errors.append(f"Erro na linha {call_node.line}: '{proc_name}' não é um procedimento")
            return
        
        # Verifica os argumentos
        if len(call_node.children) > 0:
            args_node = call_node.children[0]
            self.check_arguments(args_node, proc_symbol, call_node.line)
    
    def analyze_read_statement(self, read_node):
        """Analisa um comando read/readln."""
        # Se não tiver argumentos, é um readln simples
        if len(read_node.children) == 0:
            return
        
        # Verifica se as variáveis existem
        var_list_node = read_node.children[0]
        for var_node in var_list_node.children:
            var_name = var_node.value
            var_symbol = self.symbol_table.lookup(var_name)
            
            if not var_symbol:
                self.errors.append(f"Erro na linha {var_node.line}: Variável '{var_name}' não declarada")
            elif var_symbol.kind == 'constant':
                self.errors.append(f"Erro na linha {var_node.line}: Não é possível ler para constante '{var_name}'")
    
    def analyze_write_statement(self, write_node):
        """Analisa um comando write/writeln."""
        # Se não tiver argumentos, é um writeln simples
        if len(write_node.children) == 0:
            return
        
        # Verifica as expressões
        expr_list_node = write_node.children[0]
        for expr_node in expr_list_node.children:
            self.check_expression_type(expr_node)  # Apenas para verificar se a expressão é válida
    
    def check_function_return(self, function_name, body_node):
        """Verifica se a função tem um valor de retorno."""
        # Simplificação: apenas verifica se há uma atribuição para a função no corpo
        has_return = False
        
        # Função recursiva para procurar atribuições à função
        def find_return(node):
            nonlocal has_return
            if node is None:
                return
            
            if node.type == 'assignment':
                var_node = node.children[0]
                if var_node.type == 'variable' and var_node.value == function_name:
                    has_return = True
            
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        find_return(item)
                else:
                    find_return(child)
        
        find_return(body_node)
        
        if not has_return:
            self.warnings.append(f"Aviso: Função '{function_name}' pode não retornar um valor")
    
    def check_arguments(self, args_node, subprogram_symbol, line):
        """Verifica os argumentos de uma chamada de função/procedimento."""
        if args_node.type != 'argument_list':
            return
        
        # Verifica o número de argumentos
        if len(args_node.children) != len(subprogram_symbol.params):
            self.errors.append(f"Erro na linha {line}: Número incorreto de argumentos para '{subprogram_symbol.name}'. Esperado {len(subprogram_symbol.params)}, encontrado {len(args_node.children)}")
            return
        
        # Verifica o tipo de cada argumento
        for i, arg_node in enumerate(args_node.children):
            arg_type = self.check_expression_type(arg_node)
            param_type = subprogram_symbol.params[i].type
            
            if arg_type is not None and not self.are_types_compatible(param_type, arg_type):
                self.errors.append(f"Erro na linha {line}: Tipo incompatível para argumento {i+1} de '{subprogram_symbol.name}'. Esperado '{param_type}', encontrado '{arg_type}'")
    
    def check_expression_type(self, expr_node):
        """Verifica o tipo de uma expressão."""
        if expr_node is None:
            return None
        
        if expr_node.type == 'number':
            # Verifica se é inteiro ou real
            if isinstance(expr_node.value, int):
                return 'integer'
            else:
                return 'real'
        
        elif expr_node.type == 'string':
            return 'string'
        
        elif expr_node.type == 'boolean':
            return 'boolean'
        
        elif expr_node.type == 'variable':
            var_name = expr_node.value
            var_symbol = self.symbol_table.lookup(var_name)
            
            if not var_symbol:
                self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Variável '{var_name}' não declarada")
                return None
            
            return var_symbol.type
        
        elif expr_node.type == 'array_access':
            array_name = expr_node.value
            index_node = expr_node.children[0]
            
            # Verifica se a variável existe
            var_symbol = self.symbol_table.lookup(array_name)
            if not var_symbol:
                self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Variável '{array_name}' não declarada")
                return None
            
            # Se for uma string, trata como acesso a caractere
            if var_symbol.type == 'string':
                # Verifica se o índice é inteiro
                index_type = self.check_expression_type(index_node)
                if index_type is not None and index_type != 'integer':
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Índice de string deve ser inteiro, encontrado '{index_type}'")
                # Em Pascal, um caractere de string é tratado como integer (código ASCII)
                return 'integer'
            
            # Se for um array
            elif var_symbol.array_dims:
                # Verifica se o índice é inteiro
                index_type = self.check_expression_type(index_node)
                if index_type is not None and index_type != 'integer':
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Índice de array deve ser inteiro, encontrado '{index_type}'")
                
                # Retorna o tipo do elemento do array
                if 'array of' in var_symbol.type:
                    return var_symbol.type.split(' of ')[1]
                else:
                    return 'integer'
            
            # Se não for nem string nem array
            else:
                self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: '{array_name}' não é um array nem uma string")
                return None
            
        # Em semantic.py, no método check_expression_type
        elif expr_node.type == 'length_call':
                arg_node = expr_node.children[0]
                arg_type = self.check_expression_type(arg_node)

                if arg_type is not None and arg_type != 'string':
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Função length() requer argumento string, encontrado '{arg_type}'")
                    return None

                return 'integer'  # length() retorna um inteiro

        elif expr_node.type == 'function_call':
            func_name = expr_node.value
            
            # Verifica se a função existe
            func_symbol = self.symbol_table.lookup(func_name)
            if not func_symbol:
                self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Função '{func_name}' não declarada")
                return None
            
            if func_symbol.kind != 'function':
                self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: '{func_name}' não é uma função")
                return None
            
            # Verifica os argumentos
            if len(expr_node.children) > 0:
                args_node = expr_node.children[0]
                self.check_arguments(args_node, func_symbol, getattr(expr_node, 'line', 0))
            
            return func_symbol.type
        
        elif expr_node.type == 'binary_op':
            left_node = expr_node.children[0]
            right_node = expr_node.children[1]
            operator = expr_node.value
            
            left_type = self.check_expression_type(left_node)
            right_type = self.check_expression_type(right_node)
            
            if left_type is None or right_type is None:
                return None
            
            # Operadores aritméticos
            if operator in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
                if left_type in ['integer', 'real'] and right_type in ['integer', 'real']:
                    # Se um dos operandos for real, o resultado é real
                    if left_type == 'real' or right_type == 'real':
                        return 'real'
                    else:
                        return 'integer'
                else:
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Operador '{operator}' requer operandos numéricos")
                    return None
            
            # Operadores div e mod
            elif operator in ['DIV', 'MOD']:
                if left_type == 'integer' and right_type == 'integer':
                    return 'integer'
                else:
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Operador '{operator}' requer operandos inteiros")
                    return None
            
            # Operadores relacionais
            elif operator in ['EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE']:
                if self.are_types_compatible(left_type, right_type):
                    return 'boolean'
                else:
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Tipos incompatíveis para operador '{operator}'")
                    return None
            
            # Operadores lógicos
            elif operator in ['AND', 'OR']:
                if left_type == 'boolean' and right_type == 'boolean':
                    return 'boolean'
                else:
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Operador '{operator}' requer operandos booleanos")
                    return None
        
        elif expr_node.type == 'unary_op':
            operand_node = expr_node.children[0]
            operator = expr_node.value
            
            operand_type = self.check_expression_type(operand_node)
            
            if operand_type is None:
                return None
            
            # Operador unário -
            if operator == 'MINUS':
                if operand_type in ['integer', 'real']:
                    return operand_type
                else:
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Operador unário '-' requer operando numérico")
                    return None
            
            # Operador not
            elif operator == 'NOT':
                if operand_type == 'boolean':
                    return 'boolean'
                else:
                    self.errors.append(f"Erro na linha {getattr(expr_node, 'line', 0)}: Operador 'not' requer operando booleano")
                    return None
        
        return None
    
    def get_type_name(self, type_node):
        """Obtém o nome do tipo a partir do nó de tipo."""
        if type_node.type == 'type':
            return type_node.value
        elif type_node.type == 'array_type':
            element_type = self.get_type_name(type_node.children[0])
            return f"array of {element_type}"
        return None
    
    def are_types_compatible(self, type1, type2):
        """Verifica se dois tipos são compatíveis."""
        if type1 is None or type2 is None:
            return False
        
        # Tipos iguais são compatíveis
        if type1 == type2:
            return True
        
        # Integer é compatível com real (mas não o contrário)
        if type1 == 'real' and type2 == 'integer':
            return True
        
        # Para strings e caracteres (representados como integer em Pascal)
        # Caractere individual pode ser tratado como integer
        if type1 == 'integer' and type2 == 'string':
            return False  # String não pode ser atribuída a integer diretamente
        
        if type1 == 'string' and type2 == 'integer':
            return False  # Integer não pode ser atribuído a string diretamente
        
        return False
    
    def evaluate_constant_expression(self, expr_node):
        """Avalia uma expressão constante para determinar seu tipo e valor."""
        if expr_node.type == 'number':
            if isinstance(expr_node.value, int):
                return 'integer', expr_node.value
            else:
                return 'real', expr_node.value
        
        elif expr_node.type == 'string':
            return 'string', expr_node.value
        
        elif expr_node.type == 'boolean':
            return 'boolean', expr_node.value.lower() == 'true'
        
        # Para simplificar, não avaliamos expressões complexas
        return None, None
    
    def print_errors(self):
        """Imprime os erros encontrados."""
        if not self.errors:
            print("Nenhum erro semântico encontrado.")
        else:
            print("\n=== ERROS SEMÂNTICOS ===")
            for error in self.errors:
                print(error)
    
    def print_warnings(self):
        """Imprime os avisos encontrados."""
        if self.warnings:
            print("\n=== AVISOS ===")
            for warning in self.warnings:
                print(warning)

# Exemplo de uso
if __name__ == "__main__":
    from parser import parse_code
    
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
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        analyzer.symbol_table.print_table()
        analyzer.print_errors()
        analyzer.print_warnings()

