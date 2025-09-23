# intelligent-rescue-agent (resumido)


## Visão Geral
Agente de resgate em labirintos. O robô explora um mapa, localiza e coleta um humano (@) e retorna até a entrada (E), registrando um log CSV.


## Como executar

1. **Crie um ambiente virtual (recomendado)**

    - Linux/Mac:
        ```bash
        python -m venv venv
        ```

    - Windows:
        ```bash
        python -m venv venv
        ```

2. **Ative o ambiente virtual:**

    - Linux/Mac:
        ```bash
        source venv/bin/activate
        ```

    - Windows:
        ```bash
        venv\Scripts\activate
        ```



3. **Instalar as dependências**

    Execute o cmando abaixo para instalar as dependências necessárias para o projeto: 

    ```
    pip install -r requirements.txt
    ```

4. **Preparar os mapas**

    - Copie seus arquivos `.txt` dos mapas para a pasta `labirintos/`.

    - Atualize a variável `LABIRINTOS` no arquivo `config.py` com os nomes dos arquivos que colocou em `labirintos/`

        ```python
        LABIRINTOS = ["lab1.txt", "lab4.txt"]  # Adicione os nomes dos seus arquivos aqui
        ```

5. **Executar o script principal**

    Na raiz do projeto, execute o comando:
    ```
    python run.py
    ```

5. Verifique os logs gerados na pasta `logs/` (ex.: `logs/lab1.csv`, `logs/lab4.csv`).

## Testes
Execute os testes unitários com pytest:
```
pytest testes_alarmes.py
```

Ou, para mais detalhes:
```
pytest -v testes_alarmes.py
```


**OBSERVAÇÃO:** Para os testes funcionarem, a biblioteca `pytest` deve estar instalada (já incluída em `requirements.txt`). Portanto, certifique-se de ter executado o comando `pip install -r requirements.txt` antes de rodar os testes.



