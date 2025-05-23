# test_compiler.py - Testes para o compilador Pascal
import os
import tempfile
from main import compile_file

# Exemplos do projeto
examples = {
    "Exemplo 1: Olá, Mundo!": """
program HelloWorld; 
begin 
    writeln('Ola, Mundo!'); 
end.
""",
    
    "Exemplo 2: Maior de 3": """
program Maior3; 

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
        if num1 > num3 then 
            maior := num1 
        else 
            maior := num3 
    else 
        if num2 > num3 then 
            maior := num2 
        else 
            maior := num3; 
     
    WriteLn('O maior é: ', maior) 
end.
""",

    "Exemplo 3: Fatorial": """
program Fatorial; 
var 
    n, i, fat: integer; 
begin 
    writeln('Introduza um número inteiro positivo:'); 
    readln(n); 

    fat := 1; 
    for i := 1 to n do 
        fat := fat * i; 
    writeln('Fatorial de ', n, ': ', fat); 
end.
""",

    "Exemplo 4: Número Primo": """
program NumeroPrimo; 
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
end.
""",

    "Exemplo 5: Soma de Array": """
program SomaArray; 
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
end.
""",

    "Exemplo 6: Binário para Inteiro": """
program BinarioParaInteiro; 
var 
    bin: string; 
    i, valor, potencia: integer; 
begin 
    writeln('Introduza uma string binária:'); 
    readln(bin); 

    valor := 0; 
    potencia := 1; 
    for i := length(bin) downto 1 do 
    begin 
        if bin[i] = '1' then 
            valor := valor + potencia; 
        potencia := potencia * 2; 
    end; 
     
    writeln('O valor inteiro correspondente é: ', valor); 
end.
""",

    "Exemplo 7: Binário para Inteiro (com função)": """
program BinarioParaInteiro; 

function BinToInt(bin: string): integer; 
var 
    i, valor, potencia: integer; 
begin 
    valor := 0; 
    potencia := 1; 
     
    for i := length(bin) downto 1 do 
    begin 
        if bin[i] = '1' then 
            valor := valor + potencia; 
        potencia := potencia * 2; 
    end; 
     
    BinToInt := valor; 
end; 

var 
    bin: string; 
    valor: integer; 
begin 
    writeln('Introduza uma string binária:'); 
    readln(bin); 

    valor := BinToInt(bin); 
     
    writeln('O valor inteiro correspondente é: ', valor); 
end.
"""
}

def run_tests():
    """Executa testes para todos os exemplos."""
    print("=== TESTES DO COMPILADOR PASCAL ===")
    
    # Cria um diretório temporário para os arquivos de teste
    with tempfile.TemporaryDirectory() as temp_dir:
        for name, code in examples.items():
            print(f"\n{'='*60}")
            print(f"Testando {name}")
            print(f"{'='*60}")
            
            # Cria um arquivo temporário com o código Pascal
            input_file = os.path.join(temp_dir, f"{name.split(':')[0].strip()}.pas")
            output_file = os.path.join(temp_dir, f"{name.split(':')[0].strip()}.vm")
            
            with open(input_file, 'w') as f:
                f.write(code)
            
            # Compila o arquivo
            print(f"Compilando {input_file}...")
            result = compile_file(input_file, output_file, debug=True)
            
            if result:
                print(f"✅ Teste passou! Código gerado em {output_file}")
                
                # Mostra as primeiras linhas do código gerado
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                    print("\nPrimeiras 10 linhas do código gerado:")
                    for i, line in enumerate(lines[:10]):
                        print(f"{i+1}: {line.strip()}")
                    if len(lines) > 10:
                        print(f"... e mais {len(lines) - 10} linhas")
            else:
                print(f"❌ Teste falhou!")

if __name__ == "__main__":
    run_tests()