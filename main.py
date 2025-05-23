# main.py - Arquivo principal do compilador Pascal
import sys
import os
import glob
from lexer import lexer, test_lexer
from parser import parse_code, print_ast
from semantic import SemanticAnalyzer
from codegen import CodeGenerator

def compile_file(input_file, output_file=None, debug=False):
    """Compila um arquivo Pascal."""
    try:
        # Lê o arquivo de entrada
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Define o arquivo de saída
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.vm"
        
        print(f"\n{'='*60}")
        print(f"Compilando: {input_file}")
        print(f"{'='*60}")
        
        # Análise léxica
        if debug:
            print("\n=== ANÁLISE LÉXICA ===")
            tokens = test_lexer(source_code)
            for token_type, token_value, line_no in tokens:
                print(f"Linha {line_no}: {token_type} - '{token_value}'")
        
        # Análise sintática
        if debug:
            print("\n=== ANÁLISE SINTÁTICA ===")
        
        ast = parse_code(source_code)
        if ast is None:
            print("Erro: Falha na análise sintática")
            return False
        
        if debug:
            print("\n=== ÁRVORE SINTÁTICA ABSTRATA ===")
            print_ast(ast)
        
        # Análise semântica
        if debug:
            print("\n=== ANÁLISE SEMÂNTICA ===")
        
        analyzer = SemanticAnalyzer()
        if not analyzer.analyze(ast):
            analyzer.print_errors()
            analyzer.print_warnings()
            print("Erro: Falha na análise semântica")
            return False
        
        if debug:
            analyzer.symbol_table.print_table()
            analyzer.print_warnings()
        
        # Geração de código
        if debug:
            print("\n=== GERAÇÃO DE CÓDIGO ===")
        
        generator = CodeGenerator(analyzer.symbol_table)
        code = generator.generate(ast)
        
        # Escreve o código gerado no arquivo de saída
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in code:
                f.write(f"{line}\n")
        
        print(f"Compilação concluída com sucesso!")
        print(f"Código gerado em: {output_file}")
        
        # Mostra estatísticas
        print(f"   Linhas de código gerado: {len(code)}")
        print(f"   Tamanho do arquivo: {os.path.getsize(output_file)} bytes")
        
        return True
    
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado")
        return False
    except Exception as e:
        print(f"Erro durante a compilação: {e}")
        return False

def find_pascal_files(directory="."):
    """Encontra todos os arquivos Pascal com padrão example*.pas"""
    pattern = os.path.join(directory, "example*.pas")
    files = glob.glob(pattern)
    
    # Ordena os arquivos numericamente
    def extract_number(filename):
        base = os.path.basename(filename)
        try:
            # Extrai o número do nome do arquivo (example1.pas -> 1)
            num_str = base.replace("example", "").replace(".pas", "")
            return int(num_str) if num_str.isdigit() else 999
        except:
            return 999
    
    files.sort(key=extract_number)
    return files

def compile_all_examples(directory=".", debug=False):
    """Compila todos os arquivos example*.pas encontrados no diretório."""
    pascal_files = find_pascal_files(directory)
    
    if not pascal_files:
        print(f"Nenhum arquivo 'example*.pas' encontrado no diretório '{directory}'")
        print("   Certifique-se de que os arquivos estão no formato: example1.pas, example2.pas, etc.")
        return False
    
    print(f"📁 Encontrados {len(pascal_files)} arquivo(s) Pascal:")
    for file in pascal_files:
        print(f"   - {file}")
    
    successful_compilations = 0
    failed_compilations = 0
    
    for input_file in pascal_files:
        try:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.vm"
            
            if compile_file(input_file, output_file, debug):
                successful_compilations += 1
            else:
                failed_compilations += 1
                
        except KeyboardInterrupt:
            print("\n⚠️  Compilação interrompida pelo usuário")
            break
        except Exception as e:
            print(f"Erro inesperado ao compilar {input_file}: {e}")
            failed_compilations += 1
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"RESUMO DA COMPILAÇÃO")
    print(f"{'='*60}")
    print(f"Sucessos: {successful_compilations}")
    print(f"Falhas: {failed_compilations}")
    print(f"Total: {successful_compilations + failed_compilations}")
    
    if successful_compilations > 0:
        print(f"\nArquivos gerados:")
        for input_file in pascal_files:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.vm"
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"   - {output_file} ({size} bytes)")
    
    return failed_compilations == 0

def create_example_files():
    """Cria arquivos de exemplo se não existirem."""
    examples = {
        "example1.pas": """program HelloWorld; 
begin 
    writeln('Ola, Mundo!'); 
end.""",
        
        "example2.pas": """program Maior3; 
var 
    num1, num2, num3, maior: Integer; 
begin 
    Write('Introduza o primeiro número: '); 
    ReadLn(num1); 
    Write('Introduza o segundo número: '); 
    ReadLn(num2); 
    Write('Introduza o terceiro número: '); 
    ReadLn(num3); 
    
    if num1 > num2 then 
        if num1 > num3 then maior := num1 
        else maior := num3 
    else 
        if num2 > num3 then maior := num2 
        else maior := num3; 
    
    WriteLn('O maior é: ', maior) 
end.""",
        
        "example3.pas": """program Fatorial; 
var 
    n, i, fat: integer; 
begin 
    writeln('Introduza um número inteiro positivo:'); 
    readln(n); 
    fat := 1; 
    for i := 1 to n do 
        fat := fat * i; 
    writeln('Fatorial de ', n, ': ', fat); 
end.""",
        
        "example4.pas": """program NumeroPrimo; 
var 
    num, i: integer; 
    primo: boolean; 
begin 
    writeln('Introduza um número inteiro positivo:'); 
    readln(num); 
    primo := true; 
    i := 2; 
    while (i <= (num div 2)) and primo do 
    begin 
        if (num mod i) = 0 then 
            primo := false; 
        i := i + 1; 
    end; 
    if primo then 
        writeln(num, ' é um número primo') 
    else 
        writeln(num, ' não é um número primo') 
end.""",
        
        "example5.pas": """program SomaArray; 
var 
    numeros: array[1..5] of integer; 
    i, soma: integer; 
begin 
    soma := 0; 
    writeln('Introduza 5 números inteiros:'); 
    for i := 1 to 5 do 
    begin 
        readln(numeros[i]); 
        soma := soma + numeros[i]; 
    end; 
    writeln('A soma dos números é: ', soma); 
end."""
    }
    
    created_files = []
    for filename, content in examples.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filename)
    
    if created_files:
        print(f"Criados {len(created_files)} arquivo(s) de exemplo:")
        for file in created_files:
            print(f"   - {file}")
        print()
    
    return created_files

def main():
    """Função principal."""
    print("COMPILADOR PASCAL STANDARD")
    print("=" * 60)
    
    # Verifica os argumentos da linha de comando
    if len(sys.argv) == 1:
        # Modo padrão: compila todos os example*.pas
        print("Modo: Compilação automática de arquivos example*.pas")
        
        # Cria arquivos de exemplo se não existirem
        create_example_files()
        
        # Compila todos os arquivos encontrados
        compile_all_examples(".", debug=False)
        
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uso:")
            print("  python main.py                    # Compila todos os example*.pas")
            print("  python main.py arquivo.pas        # Compila um arquivo específico")
            print("  python main.py arquivo.pas -d     # Compila com modo debug")
            print("  python main.py --all [-d]         # Compila todos os example*.pas")
            print("  python main.py --create           # Cria arquivos de exemplo")
            print("  python main.py --help             # Mostra esta ajuda")
            return
        
        elif sys.argv[1] == "--create":
            print("📝 Criando arquivos de exemplo...")
            created = create_example_files()
            if not created:
                print("ℹ️  Todos os arquivos de exemplo já existem")
            return
        
        elif sys.argv[1] == "--all":
            print("📋 Modo: Compilação de todos os example*.pas")
            debug = "-d" in sys.argv
            compile_all_examples(".", debug)
            return
        
        else:
            # Modo específico: compila um arquivo específico
            input_file = sys.argv[1]
            output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('-') else None
            debug = '-d' in sys.argv
            
            print(f"📋 Modo: Compilação de arquivo específico")
            compile_file(input_file, output_file, debug)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\nErro inesperado: {e}")