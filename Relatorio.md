# Construção de um Compilador para Pascal

**Projeto de Processamento de Linguagens**  
**Maio, 2025**

**Autores:**
- Pedro Pinto (a104176)
- Marco Brito (a104187) 
- Pedro Vieira (a104352)

---

## Resumo

O presente relatório foi concebido pela UC de computação gráfica, no âmbito de uma implementação de um compilador completo para a linguagem Pascal, desenvolvido como parte do projeto de Processamento de Linguagens. O compilador é capaz de analisar, interpretar e traduzir código Pascal para código da máquina virtual, seguindo todas as etapas clássicas de compilação: análise léxica, análise sintática, análise semântica e geração de código.

**Área de Aplicação**: Desenvolvimento de Linguagens, Engenharia de Software

**Palavras-Chave**: Pascal; Análise Léxica; Análise Sintática; Análise Semântica; PLY; EWVM; Processamento de Linguagens.

---

## Índice

1. [Introdução](#1-introdução)
2. [Análise Léxica](#2-análise-léxica)
3. [Análise Sintática](#3-análise-sintática)
4. [Análise Semântica](#4-análise-semântica)
5. [Geração de Código](#5-geração-de-código)
6. [Testes e Validação](#6-testes-e-validação)
7. [Arquitetura e Qualidade do Código](#7-arquitetura-e-qualidade-do-código)
8. [Desafios e Soluções](#8-desafios-e-soluções)
9. [Conclusão](#9-conclusão)

---

## 1. Introdução

Este projeto representa a aplicação prática dos conhecimentos teóricos adquiridos sobre compiladores, linguagens formais e técnicas de processamento de linguagens de programação.

O compilador desenvolvido implementa todas as fases clássicas do processo de compilação: análise léxica, análise sintática, análise semântica e geração de código. O sistema traduz programas escritos em Pascal para código executável na máquina virtual, permitindo a execução de programas que incluem desde estruturas básicas até construções avançadas como funções, procedimentos e manipulação de estruturas de dados.

### 1.1 Objetivos

O objetivo principal deste projeto foi desenvolver um compilador funcional para Pascal que fosse capaz de:

- Processar programas Pascal com todas as construções fundamentais da linguagem
- Gerar código executável para a máquina virtual
- Fornecer análise semântica robusta com deteção de erros
- Suportar funcionalidades avançadas como funções, procedimentos e arrays

### 1.2 Arquitetura do Sistema

O compilador foi estruturado em quatro módulos principais:

- **Analisador Léxico** (`lexer.py`)
- **Analisador Sintático** (`parser.py`)
- **Analisador Semântico** (`semantic.py`)
- **Gerador de Código** (`codegen.py`)

Adicionalmente, foram implementados módulos de apoio:

- **Tabela de Símbolos** (`symboltable.py`)
- **Controlador Principal** (`main.py`)
- **Testes Unitários** (`test_compiler.py`)

## 2. Análise Léxica

### 2.1 Implementação

O analisador léxico foi implementado utilizando a ferramenta PLY (Python Lex-Yacc), especificamente o módulo `ply.lex`. A implementação segue uma abordagem baseada exclusivamente em expressões regulares, conforme orientação do professor.

### 2.2 Características Principais

- **Palavras Reservadas**: Suporte completo a todas as palavras-chave do Pascal (program, begin, end, var, if, then, else, while, do, for, to, downto, function, procedure, etc.)
- **Identificadores**: Reconhecimento de identificadores válidos seguindo as regras do Pascal
- **Literais**: Suporte a constantes inteiras, reais, strings e booleanas
- **Operadores**: Implementação completa de operadores aritméticos, relacionais e lógicos
- **Delimitadores**: Reconhecimento de todos os símbolos especiais necessários
- **Comentários**: Suporte a comentários em chaves `{ }` e parênteses `(* *)`

### 2.3 Tratamento de Casos Especiais

O lexer implementa tratamento especial para:

- Palavras reservadas case-insensitive
- Strings com aspas simples e escape de aspas duplas
- Números reais e inteiros
- Operadores de dois caracteres (`:=`, `<>`, `<=`, `>=`, `..`)

## 3. Análise Sintática

### 3.1 Gramática Implementada

O analisador sintático foi desenvolvido utilizando `ply.yacc` e implementa uma gramática completa para Pascal. A gramática suporta:

- **Estrutura de Programa**: `program nome; declarações begin comandos end.`
- **Declarações**: Variáveis, constantes, tipos, funções e procedimentos
- **Comandos**: Atribuição, compostos, condicionais, ciclos, chamadas de procedimentos
- **Expressões**: Aritméticas, relacionais, lógicas e chamadas de funções

### 3.2 Precedência de Operadores

Foi implementada uma tabela de precedência completa que garante a correta análise de expressões complexas:

```python
precedence = (
    ('nonassoc', 'THEN'),
    ('nonassoc', 'ELSE'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ', 'LT', 'LTE', 'GT', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'DIV', 'MOD'),
    ('right', 'UMINUS', 'NOT'),
)
```
## 3.3 Árvore Sintática Abstracta (AST)

O parser gera uma AST estruturada que facilita as fases posteriores de análise semântica e geração de código. Cada nó da árvore contém:

- Tipo do nó  
- Filhos (sub-árvores)  
- Valor associado  
- Informação de linha para relatório de erros  

## 4. Análise Semântica

A análise semântica é realizada pela classe `SemanticAnalyzer` que percorre a Árvore Sintática Abstrata (AST) gerada pelo parser para verificar a correção semântica do código Pascal. O componente central é a `SymbolTable`, que mantém informações sobre todos os identificadores (variáveis, constantes, funções, procedimentos) organizados por escopos hierárquicos, armazenando para cada símbolo o nome, tipo, categoria, escopo e linha de declaração.

O processo divide-se em três etapas principais: 
- Análise de declarações (verificando redeclarações e registando tipos)
- Análise de comandos (validando atribuições, estruturas de controle e chamadas de funções) 
- Verificação de expressões (garantindo compatibilidade de tipos em operações, acesso correto a arrays e validação de argumentos em chamadas de função).

Durante esta travessia recursiva, o analisador verifica regras como declaração antes do uso, compatibilidade de tipos, escopo correto de variáveis e parâmetros válidos.

As verificações incluem compatibilidade de tipos em atribuições e operações, validação de que condições em estruturas de controle são booleanas, verificação de que arrays são acedidos com índices inteiros, e que funções retornam valores do tipo correto. O analisador coleta todos os erros encontrados sem interromper a análise, permitindo detectar múltiplos problemas numa única execução e fornecendo informações de linha para facilitar a depuração.


## 5. Testes e Validação

### 5.1 Conjunto de Testes

Foram implementados e testados todos os exemplos fornecidos:

- **Exemplo 1**: Olá, Mundo! - Teste básico de saída  
- **Exemplo 2**: Maior de 3 - Comandos condicionais e entrada/saída  
- **Exemplo 3**: Fatorial - Ciclos for e operações aritméticas  
- **Exemplo 4**: Número Primo - Ciclos while e operações lógicas  
- **Exemplo 5**: Soma de Array - Arrays e ciclos  
- **Exemplo 6**: Binário para Decimal - Strings e acesso a caracteres  
- **Exemplo 7**: Binário para Decimal com Função - Funções e recursividade  
- **Exemplo 8**: Ordenação Parcial - Algoritmos complexos  
- **Exemplo 9**: Teste Avançado - Múltiplas funções e operações complexas  

### 5.2 Casos de Teste Adicionais

Além dos exemplos fornecidos, foram criados testes específicos para:

- Deteção de erros léxicos  
- Deteção de erros sintáticos  
- Deteção de erros semânticos  
- Validação de tipos  

### 5.3 Resultados dos Testes

Todos os testes passaram com sucesso, gerando código correto e executável. O compilador demonstrou robustez na deteção de erros e na geração de código eficiente.

## 6. Arquitetura e Qualidade do Código

A arquitetura do compilador foi cuidadosamente planeada para garantir modularidade e extensibilidade. Cada fase da compilação foi implementada como um módulo separado, com interfaces bem definidas entre os módulos. Esta separação facilita não apenas a compreensão do código mas também futuras extensões e modificações.

O módulo de análise léxica encapsula toda a lógica relacionada com tokenização, fornecendo uma interface limpa para o analisador sintático. O analisador sintático, por sua vez, produz uma AST bem estruturada que serve como entrada para as fases subsequentes. A análise semântica opera sobre esta AST, enriquecendo-a com informação de tipos e verificando a correção semântica.

## 7. Desafios 

O desenvolvimento do compilador apresentou vários desafios técnicos significativos, cada um exigindo soluções criativas e uma compreensão profunda dos princípios de compilação. O desafio mais persistente foi o tratamento correto de strings na máquina virtual, que inicialmente causava erros relacionados com referências inválidas.

Outro desafio significativo foi a implementação correta de condições booleanas. 

## 8. Conclusão

O projeto de desenvolvimento do compilador Pascal foi concluído com sucesso, cumprindo todos os objetivos propostos e demonstrando uma implementação robusta e funcional. O compilador desenvolvido não apenas processa corretamente programas Pascal mas também fornece uma base sólida para futuras extensões e melhorias.

Os resultados obtidos demonstram o sucesso do projeto em todos os seus objetivos principais. O compilador processa corretamente todos os exemplos fornecidos, gerando código que executa sem erros e produz os resultados esperados. A robustez do sistema é evidenciada pela sua capacidade de lidar com programas complexos envolvendo múltiplas funções, estruturas de dados e operações avançadas.

As aprendizagens obtidas durante o desenvolvimento foram significativas, proporcionando uma compreensão profunda dos princípios de compilação, desde a análise léxica até à geração de código.

O resultado final constitui não apenas uma ferramenta útil mas também uma demonstração prática dos conceitos fundamentais de processamento de linguagens.