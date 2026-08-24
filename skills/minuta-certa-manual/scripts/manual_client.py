#!/usr/bin/env python3
"""
Cliente interno para o Mévio consultar documentação, catálogo de planos
e dados da conta diretamente da API do Minuta Certa.

Comandos:
  manual_client.py plans
  manual_client.py plan <id>
  manual_client.py account-plan [--email <email>]
  manual_client.py list
  manual_client.py read <slug>
  manual_client.py search "<termo>"

Variáveis de ambiente:
  MINUTA_CERTA_API_URL / API_URL : URL base da API (default: http://localhost:3000)
  MEVIO_INTERNAL_API_TOKEN / API_TOKEN : Token de autenticação Bearer
  USER_EMAIL : E-mail padrão do usuário para consulta de conta
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error


def get_base_url() -> str:
    legacy_url = os.getenv("MEVIO_MANUAL_BASE_URL", "").replace("/internal/ai/manual", "").strip()
    url = (
        os.getenv("MINUTA_CERTA_API_URL")
        or os.getenv("API_URL")
        or legacy_url
        or "https://minutacerta.com.br"
    )
    return url.rstrip("/")


def get_api_token() -> str:
    token = os.getenv("MEVIO_INTERNAL_API_TOKEN") or os.getenv("API_TOKEN") or ""
    return token.strip()


def make_request(path: str, query_params: dict = None, extra_headers: dict = None) -> dict:
    base_url = get_base_url()
    token = get_api_token()

    if not token:
        print("ERRO DE CONFIGURAÇÃO: MEVIO_INTERNAL_API_TOKEN não definido.", file=sys.stderr)
        print("Defina a variável de ambiente MEVIO_INTERNAL_API_TOKEN no container.", file=sys.stderr)
        sys.exit(2)

    url = f"{base_url}{path}"
    if query_params:
        encoded_params = urllib.parse.urlencode({k: v for k, v in query_params.items() if v is not None})
        if encoded_params:
            url = f"{url}?{encoded_params}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "MevioAgent/2.0",
    }
    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8")
            parsed_err = json.loads(err_body)
            err_msg = parsed_err.get("error", err_body)
        except Exception:
            err_msg = err_body or str(e)
        
        print(f"ERRO HTTP {e.code}: {err_msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERRO DE CONEXÃO: Não foi possível conectar ao Minuta Certa em {base_url}.", file=sys.stderr)
        print(f"Detalhe: {e.reason}", file=sys.stderr)
        print("Aviso ao Mévio: Não invente dados comerciais quando a API estiver indisponível.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERRO INESPERADO: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_plans(args):
    data = make_request("/internal/ai/plans")
    planos = data.get("planos", [])

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=== CATÁLOGO DINÂMICO DE PLANOS (Minuta Certa) ===")
    print(f"Consultado em: {data.get('consultado_em', 'N/D')}")
    print(f"Total de opções disponíveis: {len(planos)}\n")

    for p in planos:
        destaque = " [RECOMENDADO]" if p.get("destaque") else ""
        print(f"• ID: {p.get('id')} | Nome: {p.get('nome')}{destaque}")
        print(f"  Preço: {p.get('preco')}")
        print(f"  Franquia: {p.get('franquia_minutas')} minutas/mês")
        print(f"  Descrição: {p.get('descricao')}")
        
        precos_per = p.get("precos_por_periodicidade", {})
        if len(precos_per) > 1:
            per_strs = [f"{k.capitalize()}: {v}" for k, v in precos_per.items()]
            print(f"  Opções de periodicidade: {', '.join(per_strs)}")
        
        beneficios = p.get("beneficios", [])
        if beneficios:
            print(f"  Benefícios: {', '.join(beneficios)}")
        if p.get("observacoes"):
            print(f"  Obs: {p.get('observacoes')}")
        print()


def cmd_plan(args):
    plan_id = args.plan_id.strip().lower()
    data = make_request(f"/internal/ai/plans/{plan_id}")

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f"=== DETALHES DO PLANO: {data.get('nome', plan_id)} ===")
    print(f"ID: {data.get('id')}")
    print(f"Status: {data.get('status')} (Disponível: {'Sim' if data.get('disponivel_para_contratacao') else 'Não'})")
    print(f"Preço: {data.get('preco')}")
    print(f"Franquia: {data.get('franquia_minutas')} minutas")
    print(f"Descrição: {data.get('descricao')}")

    precos_per = data.get("precos_por_periodicidade", {})
    if precos_per:
        print("Periodicidades:")
        for k, v in precos_per.items():
            print(f"  - {k.capitalize()}: {v}")

    beneficios = data.get("beneficios", [])
    if beneficios:
        print("Recursos inclusos:")
        for b in beneficios:
            print(f"  - {b}")
    if data.get("observacoes"):
        print(f"Observações: {data.get('observacoes')}")


def cmd_account_plan(args):
    email = args.email or os.getenv("USER_EMAIL") or ""
    email = email.strip().lower()

    if not email:
        print("ERRO: E-mail do usuário não especificado.", file=sys.stderr)
        print("Passe --email <email> ou defina USER_EMAIL no ambiente.", file=sys.stderr)
        sys.exit(1)

    data = make_request("/internal/ai/account/plan", extra_headers={"x-user-email": email})

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=== DADOS DO PLANO DO USUÁRIO ===")
    print(f"Usuário: {data.get('nome')} ({data.get('email')})")
    print(f"Plano atual: {data.get('nome_plano')} (ID: {data.get('plano_id')})")
    print(f"Status da conta: {data.get('status_conta')} | Assinatura: {data.get('status_assinatura')}")
    print(f"Franquia do plano: {data.get('franquia_minutas')} minutas")
    print(f"Saldo restante: {data.get('saldo_minutas')} minutas")
    print(f"Minutas consumidas: {data.get('minutas_consumidas')}")
    print(f"Tipo de cobrança: {data.get('tipo_cobranca')}")
    if data.get("data_renovacao"):
        print(f"Data de renovação/fim: {data.get('data_renovacao')}")
    print(f"Consultado em: {data.get('consultado_em')}")


def cmd_list(args):
    data = make_request("/internal/ai/manual")
    docs = data.get("documents", [])

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print("=== ÍNDICE DO MANUAL DO MINUTA CERTA ===")
    for doc in docs:
        print(f"• [{doc.get('slug')}] {doc.get('title')}")


def cmd_read(args):
    slug = args.slug.strip()
    data = make_request(f"/internal/ai/manual/{slug}")

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f"=== {data.get('title', slug)} ===\n")
    print(data.get("content", ""))


def cmd_search(args):
    query = args.query.strip()
    data = make_request("/internal/ai/manual/search", query_params={"q": query, "limit": args.limit})
    results = data.get("results", [])

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    print(f"=== RESULTADOS DA BUSCA POR: '{query}' ({len(results)} encontrados) ===")
    for r in results:
        print(f"\n📄 {r.get('title')} (slug: {r.get('slug')})")
        print(f"   Trecho: {r.get('excerpt')}")


def main():
    parser = argparse.ArgumentParser(
        description="Cliente de consulta ao manual e catálogo dinâmico de planos do Minuta Certa para o Mévio."
    )
    parser.add_argument("--json", action="store_true", help="Retorna saída bruta formatada em JSON")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando: plans
    p_plans = subparsers.add_parser("plans", help="Consulta catálogo dinâmico de planos comerciais")
    p_plans.set_defaults(func=cmd_plans)

    # Subcomando: plan
    p_plan = subparsers.add_parser("plan", help="Consulta detalhes de um plano específico")
    p_plan.add_argument("plan_id", help="ID do plano (ex: basico, pro, premium)")
    p_plan.set_defaults(func=cmd_plan)

    # Subcomando: account-plan
    p_account = subparsers.add_parser("account-plan", help="Consulta plano e saldo do usuário atual")
    p_account.add_argument("--email", help="E-mail do usuário para identificação de contexto")
    p_account.set_defaults(func=cmd_account_plan)

    # Subcomando: list / index
    p_list = subparsers.add_parser("list", aliases=["index"], help="Lista capítulos da documentação")
    p_list.set_defaults(func=cmd_list)

    # Subcomando: read
    p_read = subparsers.add_parser("read", help="Lê conteúdo completo de um capítulo do manual")
    p_read.add_argument("slug", help="Identificador do documento (ex: 00-visao-geral)")
    p_read.set_defaults(func=cmd_read)

    # Subcomando: search
    p_search = subparsers.add_parser("search", help="Busca termos no manual")
    p_search.add_argument("query", help="Texto ou termo a pesquisar")
    p_search.add_argument("--limit", type=int, default=5, help="Limite de resultados (padrão: 5)")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
