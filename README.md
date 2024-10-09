
# DAX Filtros

Este projeto tem como objetivo a análise e cálculo de impedâncias para diferentes configurações de filtros, com foco em harmônicos de corrente.

## Estrutura do Projeto

- **`principal.py`**: Script principal que executa a análise das impedâncias e harmônicos.
- **`funcoes.py`**: Contém as funções auxiliares usadas no cálculo e análise das impedâncias.
- **`traducoes.py`**: Script responsável por traduções de mensagens ou textos.
- **`Impedancias_diferentes_configuracoes_filtros.slx`**: Arquivo Simulink usado para simulação das configurações de filtros.
- **`leitura_harmonicos_de_corrente.csv` / `leitura_harmonicos_de_corrente.xlsx`**: Dados de leitura dos harmônicos de corrente, usados para análise.
- **`figs/`**: Pasta contendo figuras geradas durante a execução do projeto.
- **`requirements.txt`**: Lista de dependências necessárias para a execução do projeto.

## Como Executar

1. Certifique-se de ter as dependências instaladas. Você pode instalá-las usando o comando:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute o script principal:

   ```bash
   python principal.py
   ```

3. As simulações do Simulink podem ser abertas e executadas através do arquivo `Impedancias_diferentes_configuracoes_filtros.slx` no MATLAB.

## Requisitos

- Python 3.x
- MATLAB com Simulink (para simulações)
- Bibliotecas adicionais listadas em `requirements.txt`

## Saída

- O projeto gera análises e gráficos que são salvos na pasta `figs/`.
- Os resultados são baseados nos dados fornecidos nos arquivos CSV e XLSX.

## Autor

Este projeto foi desenvolvido por [Seu Nome] como parte de uma análise de filtros de harmônicos para sistemas elétricos.
