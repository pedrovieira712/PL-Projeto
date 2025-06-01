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
        self.symbols = {}       
        self.scopes = ["global"] 
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
        
        if key in self.symbols:
            return False
        
        self.symbols[key] = Symbol(name, type, kind, self.current_scope, line, value)
        return True
    
    def lookup(self, name, current_scope_only=False):
        """Procura um símbolo na tabela."""
        # Procura no escopo atual
        key = f"{self.current_scope}.{name}"
        if key in self.symbols:
            return self.symbols[key]
        
        if not current_scope_only:
            scope = self.current_scope
            while "." in scope:
                scope = scope.rsplit(".", 1)[0]  
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

if __name__ == "__main__":
    pass
