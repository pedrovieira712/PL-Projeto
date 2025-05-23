# test_units.py - Testes unitários para o compilador Pascal
import unittest
from lexer import test_lexer
from parser import parse_code
from semantic import SemanticAnalyzer
from codegen import CodeGenerator

class TestLexer(unittest.TestCase):
    """Testes para o analisador léxico."""
    
    def test_simple_program(self):
        """Testa o lexer com um programa simples."""
        code = """
        program Test;
        begin
            writeln('Hello');
        end.
        """
        tokens = test_lexer(code)
        token_types = [t[0] for t in tokens]
        
        self.assertIn('PROGRAM', token_types)
        self.assertIn('ID', token_types)
        self.assertIn('BEGIN', token_types)
        self.assertIn('WRITELN', token_types)
        self.assertIn('STRING_CONST', token_types)
        self.assertIn('END', token_types)
        self.assertIn('DOT', token_types)
    
    def test_operators(self):
        """Testa o lexer com operadores."""
        code = "a := b + c * d / e - f"
        tokens = test_lexer(code)
        token_types = [t[0] for t in tokens]
        
        self.assertIn('ASSIGN', token_types)
        self.assertIn('PLUS', token_types)
        self.assertIn('TIMES', token_types)
        self.assertIn('DIVIDE', token_types)
        self.assertIn('MINUS', token_types)
    
    def test_comments(self):
        """Testa o lexer com comentários."""
        code = """
        { This is a comment }
        program Test;
        (* This is another comment *)
        begin
            writeln('Hello');
        end.
        """
        tokens = test_lexer(code)
        token_types = [t[0] for t in tokens]
        
        self.assertIn('PROGRAM', token_types)
        self.assertNotIn('This', token_types)  # Comentários devem ser ignorados

class TestParser(unittest.TestCase):
    """Testes para o analisador sintático."""
    
    def test_simple_program(self):
        """Testa o parser com um programa simples."""
        code = """
        program Test;
        begin
            writeln('Hello');
        end.
        """
        ast = parse_code(code)
        
        self.assertIsNotNone(ast)
        self.assertEqual(ast.type, 'program')
        self.assertEqual(ast.value, 'Test')
    
    def test_variable_declaration(self):
        """Testa o parser com declaração de variáveis."""
        code = """
        program Test;
        var
            x, y: integer;
            z: real;
        begin
            x := 10;
        end.
        """
        ast = parse_code(code)
        
        self.assertIsNotNone(ast)
        self.assertEqual(ast.type, 'program')
        
        # Verifica se há declarações de variáveis
        declarations = ast.children[0]
        self.assertEqual(declarations.type, 'declarations')
        self.assertGreater(len(declarations.children), 0)
        
        # Verifica se há pelo menos uma declaração de variável
        var_decl = None
        for child in declarations.children:
            if child.type == 'var_declaration':
                var_decl = child
                break
        
        self.assertIsNotNone(var_decl)
    
    def test_if_statement(self):
        """Testa o parser com comando if."""
        code = """
        program Test;
        var
            x: integer;
        begin
            if x > 0 then
                writeln('Positive')
            else
                writeln('Non-positive');
        end.
        """
        ast = parse_code(code)
        
        self.assertIsNotNone(ast)
        
        # Procura o comando if
        if_stmt = None
        
        def find_if(node):
            nonlocal if_stmt
            if node is None:
                return
            
            if node.type == 'if_statement':
                if_stmt = node
                return
            
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        find_if(item)
                else:
                    find_if(child)
        
        find_if(ast)
        
        self.assertIsNotNone(if_stmt)
        self.assertEqual(len(if_stmt.children), 3)  # condição, then, else

class TestSemanticAnalyzer(unittest.TestCase):
    """Testes para o analisador semântico."""
    
    def test_variable_redeclaration(self):
        """Testa a detecção de redeclaração de variáveis."""
        code = """
        program Test;
        var
            x: integer;
            x: real;  # Erro: x já foi declarado
        begin
            x := 10;
        end.
        """
        ast = parse_code(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        self.assertFalse(result)
        self.assertGreater(len(analyzer.errors), 0)
    
    def test_type_mismatch(self):
        """Testa a detecção de incompatibilidade de tipos."""
        code = """
        program Test;
        var
            x: integer;
            b: boolean;
        begin
            x := b;  # Erro: tipos incompatíveis
        end.
        """
        ast = parse_code(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        self.assertFalse(result)
        self.assertGreater(len(analyzer.errors), 0)
    
    def test_undeclared_variable(self):
        """Testa a detecção de variáveis não declaradas."""
        code = """
        program Test;
        begin
            x := 10;  # Erro: x não foi declarado
        end.
        """
        ast = parse_code(code)
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        self.assertFalse(result)
        self.assertGreater(len(analyzer.errors), 0)

class TestCodeGenerator(unittest.TestCase):
    """Testes para o gerador de código."""
    
    def test_code_generation(self):
        """Testa a geração de código para um programa simples."""
        code = """
        program Test;
        var
            x: integer;
        begin
            x := 10;
            writeln(x);
        end.
        """
        ast = parse_code(code)
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        
        generator = CodeGenerator(analyzer.symbol_table)
        generated_code = generator.generate(ast)
        
        self.assertIsNotNone(generated_code)
        self.assertGreater(len(generated_code), 0)
        
        # Verifica se há instruções específicas no código gerado
        code_str = '\n'.join(generated_code)
        self.assertIn("PUSH 10", code_str)
        self.assertIn("STORE x", code_str)
        self.assertIn("WRITE", code_str)
        self.assertIn("WRITELN", code_str)
        self.assertIn("HALT", code_str)

if __name__ == '__main__':
    unittest.main()