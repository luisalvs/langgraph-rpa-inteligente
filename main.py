
import re
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from cliente_rpa import consultar_status_api
from diagnostico_ia import analisar_falha
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver

class EstadoRPA(TypedDict):
    codigo: str
    status: str
    descricao: str
    erro: str
    resultado: str


def validar_codigo(estado: EstadoRPA) -> dict:
    codigo = estado["codigo"].strip().upper()
    print(f"[VALIDAR] Código: {codigo}")

    if not re.fullmatch(r"RPA-\d{3}", codigo):
        return {"codigo": codigo, "erro": "Código inválido. Use o formato RPA-101."}

    return {"codigo": codigo, "erro": ""}


def consultar_api(estado: EstadoRPA) -> dict:
    codigo = estado["codigo"]
    print(f"[API] Consultando {codigo}")

    dados = consultar_status_api(codigo)

    return {
        "status": dados.get("status", "FALHA_API"),
        "descricao": dados.get("descricao", ""),
        "erro": dados.get("erro", "")
    }


def finalizar_rpa(estado: EstadoRPA) -> dict:
    print("[NODE] Finalizando processo")
    return {"resultado": f"A automação {estado['codigo']} foi concluída com sucesso."}


def acompanhar_rpa(estado: EstadoRPA) -> dict:
    print("[NODE] Acompanhando execução")
    return {"resultado": f"A automação {estado['codigo']} ainda está em execução."}


def investigar_rpa(estado: EstadoRPA) -> dict:
    print("[NODE] Investigando falha com IA")

    diagnostico = analisar_falha(
        codigo=estado["codigo"],
        descricao=estado["descricao"]
    )

    return {"resultado": diagnostico}

def aguardar_rpa(estado: EstadoRPA) -> dict:
    print("[NODE] Aguardando execução")
    return {"resultado": f"A automação {estado['codigo']} está aguardando o início do processamento."}


def rpa_nao_encontrada(estado: EstadoRPA) -> dict:
    print("[NODE] RPA não encontrada")
    return {"resultado": f"A automação {estado['codigo']} não foi encontrada."}


def falha_consulta(estado: EstadoRPA) -> dict:
    print("[NODE] Falha na consulta")
    return {"resultado": f"Não foi possível consultar {estado['codigo']}. Motivo: {estado['erro']}"}


def status_invalido(estado: EstadoRPA) -> dict:
    print("[NODE] Status desconhecido")
    return {"resultado": f"O status '{estado['status']}' não é reconhecido."}


def decidir_apos_validacao(estado: EstadoRPA) -> Literal["consultar", "falha"]:
    return "falha" if estado["erro"] else "consultar"


def decidir_caminho(estado: EstadoRPA) -> Literal[
    "finalizar", "acompanhar", "investigar", "aguardando", "nao_encontrada", "falha", "invalido"
]:
    caminhos = {
        "CONCLUIDO": "finalizar",
        "EM_EXECUCAO": "acompanhar",
        "ERRO": "investigar",
        "AGUARDANDO": "aguardando",
        "NAO_ENCONTRADO": "nao_encontrada",
        "CODIGO_INVALIDO": "falha",
        "FALHA_API": "falha"
    }
    return caminhos.get(estado["status"], "invalido")


construtor = StateGraph(EstadoRPA)

construtor.add_node("validar", validar_codigo)
construtor.add_node("consultar", consultar_api)
construtor.add_node("finalizar", finalizar_rpa)
construtor.add_node("acompanhar", acompanhar_rpa)
construtor.add_node("investigar", investigar_rpa)
construtor.add_node("aguardando", aguardar_rpa)
construtor.add_node("nao_encontrada", rpa_nao_encontrada)
construtor.add_node("falha", falha_consulta)
construtor.add_node("invalido", status_invalido)

construtor.add_edge(START, "validar")

construtor.add_conditional_edges("validar", decidir_apos_validacao, {
    "consultar": "consultar",
    "falha": "falha"
})

construtor.add_conditional_edges("consultar", decidir_caminho, {
    "finalizar": "finalizar",
    "acompanhar": "acompanhar",
    "investigar": "investigar",
    "aguardando": "aguardando",
    "nao_encontrada": "nao_encontrada",
    "falha": "falha",
    "invalido": "invalido"
})

for nome in ["finalizar", "acompanhar", "investigar", "aguardando", "nao_encontrada", "falha", "invalido"]:
    construtor.add_edge(nome, END)


def main():
    print("=" * 50)
    print("LANGGRAPH - MEMORIA E CHECKPOINTS")
    print("=" * 50)
    print("Digite 'historico' para consultar um estado salvo.")
    print("Digite 'sair' para encerrar.")

    while True:
        codigo = input("\nCódigo da RPA: ").strip().upper()

        if codigo == "SAIR":
            break

        if codigo == "HISTORICO":
            consultar_historico()
            continue

        if not codigo:
            continue

        config = {"configurable": {"thread_id": codigo}}

        resultado = grafo.invoke({
            "codigo": codigo,
            "status": "",
            "descricao": "",
            "erro": "",
            "resultado": ""
        }, config=config)

        print("\nRESPOSTA:")
        print(resultado["resultado"])

        estado_salvo = grafo.get_state(config)

        print("\n[MEMORIA] Checkpoint salvo")
        print(f"[MEMORIA] Thread: {codigo}")
        print(f"[MEMORIA] Status: {estado_salvo.values['status']}")


def consultar_historico():
    codigo = input("Código da RPA para consultar: ").strip().upper()
    config = {"configurable": {"thread_id": codigo}}

    estado = grafo.get_state(config)

    if not estado.values:
        print("Nenhum checkpoint encontrado para essa RPA.")
        return

    print("\n[ESTADO SALVO]")
    print(f"Código: {estado.values.get('codigo')}")
    print(f"Status: {estado.values.get('status')}")
    print(f"Descrição: {estado.values.get('descricao')}")
    print(f"Resultado: {estado.values.get('resultado')}")

    historico = list(grafo.get_state_history(config))
    print(f"\nCheckpoints registrados: {len(historico)}")
    print(f"Última atualização: {estado.created_at}")


if __name__ == "__main__":
    banco = Path(__file__).resolve().parent / "checkpoints.sqlite"
    
    with SqliteSaver.from_conn_string(str(banco)) as memoria:
        grafo = construtor.compile(checkpointer=memoria)
        main()
