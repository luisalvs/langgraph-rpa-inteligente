
import pytest
import main
from unittest.mock import Mock
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver


def executar_grafo(codigo):
    grafo = main.construtor.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": f"teste-{codigo}"}}

    return grafo.invoke({
        "codigo": codigo,
        "status": "",
        "descricao": "",
        "erro": "",
        "resultado": ""
    }, config=config)


@pytest.mark.parametrize("status,esperado", [
    ("CONCLUIDO", "concluída com sucesso"),
    ("EM_EXECUCAO", "ainda está em execução"),
    ("AGUARDANDO", "aguardando o início")
])
def test_status_sem_ia(monkeypatch, status, esperado):
    consulta = Mock(return_value={"status": status, "descricao": "Teste"})
    ia = Mock()
    monkeypatch.setattr(main, "consultar_status_api", consulta)
    monkeypatch.setattr(main, "analisar_falha", ia)

    resultado = executar_grafo("RPA-101")

    assert esperado in resultado["resultado"]
    consulta.assert_called_once_with("RPA-101")
    ia.assert_not_called()


def test_erro_chama_ia(monkeypatch):
    consulta = Mock(return_value={"status": "ERRO", "descricao": "Timeout"})
    ia = Mock(return_value="Diagnóstico: verificar conexão e timeout.")
    monkeypatch.setattr(main, "consultar_status_api", consulta)
    monkeypatch.setattr(main, "analisar_falha", ia)

    resultado = executar_grafo("RPA-103")

    assert "Diagnóstico:" in resultado["resultado"]
    ia.assert_called_once_with(codigo="RPA-103", descricao="Timeout")


def test_rpa_nao_encontrada(monkeypatch):
    consulta = Mock(return_value={"status": "NAO_ENCONTRADO"})
    ia = Mock()
    monkeypatch.setattr(main, "consultar_status_api", consulta)
    monkeypatch.setattr(main, "analisar_falha", ia)

    resultado = executar_grafo("RPA-999")

    assert "não foi encontrada" in resultado["resultado"]
    ia.assert_not_called()


def test_codigo_invalido_nao_chama_api(monkeypatch):
    consulta = Mock()
    monkeypatch.setattr(main, "consultar_status_api", consulta)

    resultado = executar_grafo("RPA-ABC")

    assert "Código inválido" in resultado["resultado"]
    consulta.assert_not_called()


def test_falha_api_nao_chama_ia(monkeypatch):
    consulta = Mock(return_value={"status": "FALHA_API", "erro": "Falha de conexão."})
    ia = Mock()
    monkeypatch.setattr(main, "consultar_status_api", consulta)
    monkeypatch.setattr(main, "analisar_falha", ia)

    resultado = executar_grafo("RPA-101")

    assert "Falha de conexão" in resultado["resultado"]
    ia.assert_not_called()


def test_sqlite_persiste_apos_reabrir(monkeypatch, tmp_path):
    consulta = Mock(return_value={"status": "CONCLUIDO", "descricao": "Finalizada"})
    monkeypatch.setattr(main, "consultar_status_api", consulta)

    banco = tmp_path / "teste.sqlite"
    config = {"configurable": {"thread_id": "teste-persistencia"}}

    with SqliteSaver.from_conn_string(str(banco)) as memoria:
        grafo = main.construtor.compile(checkpointer=memoria)
        grafo.invoke({
            "codigo": "RPA-101",
            "status": "",
            "descricao": "",
            "erro": "",
            "resultado": ""
        }, config=config)

    with SqliteSaver.from_conn_string(str(banco)) as memoria:
        grafo = main.construtor.compile(checkpointer=memoria)
        estado = grafo.get_state(config)

    assert estado.values["status"] == "CONCLUIDO"
    assert "concluída com sucesso" in estado.values["resultado"]
    consulta.assert_called_once()
