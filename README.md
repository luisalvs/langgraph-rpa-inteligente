# LangGraph RPA Inteligente

Workflow inteligente para monitoramento e diagnóstico de automações RPA, desenvolvido em Python com LangGraph, FastAPI, HTTPX, OpenAI e SQLite.

O projeto demonstra como combinar orquestração de workflows, integração com APIs REST, inteligência artificial e persistência de estado.

## Tecnologias utilizadas

- **Python 3.13** — Linguagem principal.
- **LangGraph** — Construção de grafos, estados e roteamento condicional.
- **FastAPI** — API externa utilizada para simular o monitoramento de automações RPA.
- **HTTPX** — Comunicação HTTP com a API de monitoramento.
- **OpenAI Responses API** — Análise inteligente de falhas.
- **SQLite** — Persistência de checkpoints do LangGraph.
- **Pytest** — Testes automatizados.

## Arquitetura

O workflow segue o fluxo:

```text
Usuário informa o código da RPA
              |
              v
       Validar código
              |
              v
      Consultar API REST
              |
              v
       Verificar status
              |
       +------+------+
       |      |      |
       v      v      v
   CONCLUIDO ERRO  EM_EXECUCAO
       |      |      |
       v      v      v
   Finalizar  IA   Acompanhar
              |
              v
       Diagnóstico técnico
              |
              v
       Salvar checkpoint
```

O projeto também trata automações aguardando execução, códigos inválidos, processos inexistentes e falhas na comunicação com a API.

## Funcionalidades

- Consulta de status de automações por código.
- Validação de entradas.
- Roteamento condicional utilizando LangGraph.
- Integração HTTP com API FastAPI.
- Diagnóstico de falhas com inteligência artificial.
- Consulta de logs para contextualizar a análise.
- Tratamento de erros de conexão e timeout.
- Persistência de checkpoints utilizando SQLite.
- Recuperação de históricos por `thread_id`.
- Testes automatizados com mocks.

A inteligência artificial é utilizada somente quando a automação apresenta erro, evitando chamadas desnecessárias ao modelo.

## Estrutura do projeto

```text
langgraph-python/
├── main.py
├── cliente_rpa.py
├── diagnostico_ia.py
├── tests/
│   └── test_workflow.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Os arquivos `.env` e `checkpoints.sqlite` são utilizados localmente e não devem ser publicados no GitHub.

## Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/luisalvs/langgraph-rpa-inteligente.git
cd langgraph-rpa-inteligente
```

### 2. Criar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar a OpenAI

Crie um arquivo `.env` a partir de `.env.example` e configure:

```env
OPENAI_API_KEY=sua_chave_aqui
```

### 5. Iniciar a API de monitoramento

Este projeto utiliza uma API FastAPI de treinamento, desenvolvida separadamente, para consultar status e logs das automações.

A API deve estar disponível em:

```text
http://127.0.0.1:8002
```

Endpoints esperados:

```text
GET /rpas/{codigo}
GET /rpas/{codigo}/logs
```

A API de monitoramento não está incluída neste repositório e deve ser disponibilizada separadamente.

### 6. Executar o workflow

```bash
python main.py
```

Exemplo de utilização:

```text
Código da RPA: RPA-101

[VALIDAR] Código: RPA-101
[API] Consultando RPA-101
[HTTPX] Status HTTP: 200
[NODE] Finalizando processo

RESPOSTA:
A automação RPA-101 foi concluída com sucesso.
```

Para consultar o último estado salvo:

```text
Código da RPA: HISTORICO
Código da RPA para consultar: RPA-101
```

## Diagnóstico inteligente

Quando a automação apresenta erro, o workflow utiliza a OpenAI para analisar os registros retornados pela API.

O diagnóstico apresenta:

1. Status e erro registrado.
2. Três possíveis causas técnicas.
3. Duas verificações práticas.
4. Uma recomendação preventiva.
5. Exemplo de configuração HTTPX quando a falha envolve timeout.

O diagnóstico é informativo: o sistema não executa correções automaticamente.

## Persistência com SQLite

Os checkpoints são armazenados no arquivo local `checkpoints.sqlite`.

Com isso, é possível recuperar estados anteriores mesmo após encerrar e reiniciar o programa.

O armazenamento é isolado por `thread_id`, utilizando o código da RPA como identificador no ambiente de treinamento.

## Testes automatizados

O projeto utiliza Pytest e mocks para testar os fluxos sem depender de chamadas reais à API ou à OpenAI.

Execute:

```bash
python3 -m pytest -v
```

**Resultado validado: 8 testes aprovados.**

Os testes incluem roteamento condicional, erros de comunicação, uso seletivo da IA, validação de entradas e persistência SQLite.

## Objetivo educacional

Este projeto foi desenvolvido como parte de uma trilha prática de evolução de desenvolvimento Python/RPA para Engenharia de IA e Automação Inteligente.

Seu objetivo é demonstrar a integração entre sistemas tradicionais, workflows com estado e modelos de linguagem.
