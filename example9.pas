program TestAdvanced;

{ Função recursiva para calcular o maior divisor comum }
function MDC(a, b: integer): integer;
begin
  if b = 0 then
    MDC := a
  else
    MDC := MDC(b, a mod b);
end;

{ Função para verificar se um número é primo }
function EhPrimo(n: integer): integer;
var
  i, limite: integer;
begin
  if n <= 1 then
    EhPrimo := 0
  else if n <= 3 then
    EhPrimo := 1
  else if (n mod 2 = 0) or (n mod 3 = 0) then
    EhPrimo := 0
  else
  begin
    EhPrimo := 1;
    limite := n div 2;
    i := 5;
    while (i <= limite) and (EhPrimo = 1) do
    begin
      if (n mod i = 0) or (n mod (i + 2) = 0) then
        EhPrimo := 0;
      i := i + 6;
    end;
  end;
end;

{ Função complexa que combina várias operações }
function CalculoComplexo(x, y, z: integer): integer;
var
  resultado, temp1, temp2, i: integer;
  fatorial: integer;
begin
  { Calcula fatorial de x }
  fatorial := 1;
  for i := 1 to x do
    fatorial := fatorial * i;
  
  { Calcula MDC de y e z }
  temp1 := MDC(y, z);
  
  { Verifica se temp1 é primo }
  temp2 := EhPrimo(temp1);
  
  { Fórmula complexa }
  if temp2 = 1 then
    resultado := fatorial + temp1 * 2
  else
    resultado := fatorial - temp1;
  
  { Ajuste final baseado em z }
  if z mod 2 = 0 then
    resultado := resultado * 2
  else
    resultado := resultado + z;
  
  CalculoComplexo := resultado;
end;

{ Função que trabalha com strings }
function ContaVogais(texto: string): integer;
var
  i, contador: integer;
  c: integer;
begin
  contador := 0;
  for i := 1 to length(texto) do
  begin
    c := texto[i];
    { Códigos ASCII: a=97, e=101, i=105, o=111, u=117 }
    { A=65, E=69, I=73, O=79, U=85 }
    if (c = 97) or (c = 101) or (c = 105) or (c = 111) or (c = 117) or
       (c = 65) or (c = 69) or (c = 73) or (c = 79) or (c = 85) then
      contador := contador + 1;
  end;
  ContaVogais := contador;
end;

{ Função que simula um algoritmo de ordenação (Bubble Sort parcial) }
function SortParcial(a, b, c, d: integer): integer;
var
  temp, trocas: integer;
  trocou: integer;
begin
  trocas := 0;
  trocou := 1;
  
  { Simula algumas passadas do bubble sort }
  while trocou = 1 do
  begin
    trocou := 0;
    
    if a > b then
    begin
      temp := a;
      a := b;
      b := temp;
      trocas := trocas + 1;
      trocou := 1;
    end;
    
    if b > c then
    begin
      temp := b;
      b := c;
      c := temp;
      trocas := trocas + 1;
      trocou := 1;
    end;
    
    if c > d then
    begin
      temp := c;
      c := d;
      d := temp;
      trocas := trocas + 1;
      trocou := 1;
    end;
  end;
  
  SortParcial := trocas;
end;

var
  num1, num2, num3, resultado: integer;
  texto: string;
  vogais: integer;

begin
  writeln('=== TESTE DE FUNÇÕES AVANÇADAS ===');
  writeln();
  
  { Teste 1: MDC recursivo }
  writeln('Teste 1: MDC recursivo');
  write('Digite dois números: ');
  readln(num1);
  readln(num2);
  resultado := MDC(num1, num2);
  writeln('MDC(', num1, ', ', num2, ') = ', resultado);
  writeln();
  
  { Teste 2: Verificação de primo }
  writeln('Teste 2: Verificação de primo');
  write('Digite um número: ');
  readln(num1);
  resultado := EhPrimo(num1);
  if resultado = 1 then
    writeln(num1, ' é primo')
  else
    writeln(num1, ' não é primo');
  writeln();
  
  { Teste 3: Cálculo complexo }
  writeln('Teste 3: Cálculo complexo');
  write('Digite três números: ');
  readln(num1);
  readln(num2);
  readln(num3);
  resultado := CalculoComplexo(num1, num2, num3);
  writeln('Resultado complexo: ', resultado);
  writeln();
  
  { Teste 4: Contagem de vogais }
  writeln('Teste 4: Contagem de vogais');
  write('Digite uma palavra: ');
  readln(texto);
  vogais := ContaVogais(texto);
  writeln('A palavra "', texto, '" tem ', vogais, ' vogais');
  writeln();
  
  { Teste 5: Simulação de ordenação }
  writeln('Teste 5: Simulação de ordenação');
  writeln('Testando com números: 64, 34, 25, 12');
  resultado := SortParcial(64, 34, 25, 12);
  writeln('Número de trocas necessárias: ', resultado);
  writeln();
  
  writeln();
  writeln('=== FIM DOS TESTES ===');
end.
