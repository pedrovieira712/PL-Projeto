program TestFunction;

function Potencia(base, expoente: integer): integer;
var
  resultado, i: integer;
begin
  resultado := 1;
  for i := 1 to expoente do
    resultado := resultado * base;
  Potencia := resultado;
end;

function Fibonacci(n: integer): integer;
var
  a, b, temp, i: integer;
begin
  if n <= 1 then
    Fibonacci := n
  else
  begin
    a := 0;
    b := 1;
    for i := 2 to n do
    begin
      temp := a + b;
      a := b;
      b := temp;
    end;
    Fibonacci := b;
  end;
end;

var
  num, resultado: integer;

begin
  writeln('Teste de funções');
  
  write('Digite um número para calcular 2^n: ');
  readln(num);
  resultado := Potencia(2, num);
  writeln('2^', num, ' = ', resultado);
  
  write('Digite um número para Fibonacci: ');
  readln(num);
  resultado := Fibonacci(num);
  writeln('Fibonacci(', num, ') = ', resultado);
  
  writeln('Teste de múltiplas chamadas:');
  writeln('3^4 = ', Potencia(3, 4));
  writeln('5^2 = ', Potencia(5, 2));
  writeln('Fib(7) = ', Fibonacci(7));
end.
