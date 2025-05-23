# symboltable.py - Tabela de símbolos para o compilador Pascal
class Symbol:
    def __init__(self, name, type, kind, scope, line, value=None):
        self.name = name        # Nome do símbolo
        self.type = type        # Tipo do símbolo (integer, real, boolean, string, array, etc.)
        self.kind = kind        # Tipo de símbolo (variable, constant, function, procedure, parameter)
        self.scope = scope      # Escopo do símbolo
        self.line = line        # Linha onde o símbolo foi declarado
        self.value = value      # Valor (para constantes)
        self.params = []        # Parâmetros (para funções e procedimentos)
        self.array_dims = None  # Dimensões (para arrays)

    def __str__(self):
        result = f"{self.name} ({self.kind}, {self.type}, escopo: {self.scope}, linha: {self.line})"
        if self.value is not None:
            result += f", valor: {self.value}"
        if self.array_dims:
            result += f", dimensões: {self.array_dims}"
        if self.params:
            params_str = ", ".join([f"{p.name}: {p.type}" for p in self.params])
            result += f", parâmetros: [{params_str}]"
        return result

class SymbolTable:
    def __init__(self):
        self.symbols = {}       # Dicionário de símbolos
        self.scopes = ["global"] # Pilha de escopos
        self.current_scope = "global"
    
    def enter_scope(self, scope_name):
        """Entra em um novo escopo."""
        new_scope = f"{self.current_scope}.{scope_name}"
        self.scopes.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        """Sai do escopo atual."""
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.current_scope = self.scopes[-1]
        return self.current_scope
    
    def add_symbol(self, name, type, kind, line, value=None):
        """Adiciona um símbolo à tabela."""
        key = f"{self.current_scope}.{name}"
        
        # Verifica se o símbolo já existe no escopo atual
        if key in self.symbols:
            return False
        
        # Adiciona o símbolo
        self.symbols[key] = Symbol(name, type, kind, self.current_scope, line, value)
        return True
    
    def lookup(self, name, current_scope_only=False):
        """Procura um símbolo na tabela."""
        # Procura no escopo atual
        key = f"{self.current_scope}.{name}"
        if key in self.symbols:
            return self.symbols[key]
        
        # Se não encontrou e não está restrito ao escopo atual, procura nos escopos superiores
        if not current_scope_only:
            scope = self.current_scope
            while "." in scope:
                scope = scope.rsplit(".", 1)[0]  # Remove o último componente do escopo
                key = f"{scope}.{name}"
                if key in self.symbols:
                    return self.symbols[key]
        
        return None
    
    def add_array_dimensions(self, name, dimensions):
        """Adiciona dimensões a um array."""
        symbol = self.lookup(name, True)
        if symbol:
            symbol.array_dims = dimensions
            return True
        return False
    
    def add_parameter(self, function_name, param_name, param_type):
        """Adiciona um parâmetro a uma função ou procedimento."""
        function = self.lookup(function_name)
        if function and (function.kind == "function" or function.kind == "procedure"):
            param = Symbol(param_name, param_type, "parameter", function.scope, function.line)
            function.params.append(param)
            return True
        return False
    
    def print_table(self):
        """Imprime a tabela de símbolos."""
        print("\n=== TABELA DE SÍMBOLOS ===")
        for key, symbol in sorted(self.symbols.items()):
            print(f"{key}: {symbol}")

# Exemplo de uso
if __name__ == "__main__":
    # Criar uma tabela de símbolos
    table = SymbolTable()
    
    # Adicionar alguns símbolos
    table.add_symbol("x", "integer", "variable", 5)
    table.add_symbol("y", "real", "variable", 6)
    
    # Entrar em um novo escopo
    table.enter_scope("function1")
    
    # Adicionar símbolos no novo escopo
    table.add_symbol("z", "boolean", "variable", 10)
    table.add_symbol("calc", "integer", "function", 9)
    
    # Adicionar parâmetros à função
    table.add_parameter("calc", "a", "integer")
    table.add_parameter("calc", "b", "integer")
    
    # Imprimir a tabela
    table.print_table()
    
    # Procurar símbolos
    print("\n=== PROCURANDO SÍMBOLOS ===")
    print(f"Procurando 'x': {table.lookup('x')}")
    print(f"Procurando 'z': {table.lookup('z')}")
    print(f"Procurando 'w': {table.lookup('w')}")
    
    # Sair do escopo
    table.exit_scope()
    
    # Verificar se ainda podemos acessar 'z'
    print(f"Procurando 'z' após sair do escopo: {table.lookup('z')}")