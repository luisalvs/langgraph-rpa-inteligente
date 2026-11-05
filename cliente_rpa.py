
import re
import httpx


API_BASE = "http://127.0.0.1:8002"


def consultar_status_api(codigo: str) -> dict:

    codigo = codigo.strip().upper()

    if not re.fullmatch(r"RPA-\d{3}", codigo):
        return {
            "codigo": codigo,
            "status": "CODIGO_INVALIDO",
            "erro": "Formato esperado: RPA-101."
        }

    url = f"{API_BASE}/rpas/{codigo}"

    try:
        resposta = httpx.get(url, timeout=5.0)

        print(f"[HTTPX] Status HTTP: {resposta.status_code}")

        if resposta.status_code == 404:
            return {
                "codigo": codigo,
                "status": "NAO_ENCONTRADO"
            }

        resposta.raise_for_status()

        dados = resposta.json()

        if not isinstance(dados, dict):
            return {
                "codigo": codigo,
                "status": "FALHA_API",
                "erro": "Resposta da API não é um objeto JSON."
            }

        if not isinstance(dados.get("status"), str):
            return {
                "codigo": codigo,
                "status": "FALHA_API",
                "erro": "Resposta sem status válido."
            }

        return dados

    except httpx.TimeoutException:
        return {
            "codigo": codigo,
            "status": "FALHA_API",
            "erro": "Timeout ao consultar a API."
        }

    except httpx.HTTPStatusError as erro:
        return {
            "codigo": codigo,
            "status": "FALHA_API",
            "erro": f"Erro HTTP {erro.response.status_code}."
        }

    except httpx.RequestError:
        return {
            "codigo": codigo,
            "status": "FALHA_API",
            "erro": "Falha de conexão com a API."
        }

    except ValueError:
        return {
            "codigo": codigo,
            "status": "FALHA_API",
            "erro": "JSON inválido retornado pela API."
        }
