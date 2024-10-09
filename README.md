
# DAX Filtros

Este projeto tem como objetivo a análise e cálculo de impedâncias para diferentes configurações de filtros, com foco em harmônicos de corrente.

## Estrutura do Projeto

- **`principal.py`**: Script principal que executa a análise das impedâncias e harmônicos.
- **`funcoes.py`**: Contém as funções auxiliares usadas no cálculo e análise das impedâncias.
- **`traducoes.py`**: Script responsável por traduções de mensagens ou textos.
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

## Requisitos

- Python 3.x
- Bibliotecas adicionais listadas em `requirements.txt`

## Saída

- O projeto gera análises e gráficos que são salvos na pasta `figs/`.
- Os resultados são baseados nos dados fornecidos nos arquivos CSV e XLSX.

## Licença

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT). Sinta-se livre para usar, modificar e distribuir este código, desde que inclua a devida atribuição ao autor.

## Autor

Desenvolvido por **Angelo Alfredo Hafner**. Para contato, envie um e-mail para [aah@dax.energy](mailto:aah@dax.energy).
