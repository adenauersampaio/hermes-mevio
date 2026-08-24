#!/bin/bash
#
# Credential helper do git para este repositório.
#
# Existe para que a URL do remote não precise carregar usuário e token. Token
# embutido na URL aparece na lista de processos, vaza em qualquer `git remote -v`
# e fica gravado em texto puro no .git/config — que não é versionado, mas
# tampouco é protegido.
#
# Este arquivo NÃO contém segredo: ele lê GITHUB_USER e GITHUB_TOKEN do .env
# (com .env.local tendo precedência, como no git-commit.sh). Por isso pode ser
# versionado à vontade.
#
# Ligado ao git por:
#   git config credential.https://github.com.helper "$(pwd)/scripts/credencial-github.sh"

set -euo pipefail

# Só a operação de leitura interessa. `store` e `erase` são ignoradas em
# silêncio: quem guarda a credencial é o .env, e não o git.
[ "${1:-}" = "get" ] || exit 0

# Resolve a raiz a partir da localização deste arquivo, e não do diretório de
# trabalho: o git invoca o helper de onde bem entender.
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ler_var() {
  local chave="$1" arquivo="$2"
  [ -f "$arquivo" ] || return 0
  sed -n "s/^[[:space:]]*${chave}=//p" "$arquivo" | tail -1 \
    | sed -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/"
}

USUARIO="${GITHUB_USER:-$(ler_var GITHUB_USER "$RAIZ/.env.local")}"
USUARIO="${USUARIO:-$(ler_var GITHUB_USER "$RAIZ/.env")}"
TOKEN="${GITHUB_TOKEN:-$(ler_var GITHUB_TOKEN "$RAIZ/.env.local")}"
TOKEN="${TOKEN:-$(ler_var GITHUB_TOKEN "$RAIZ/.env")}"

# Sem credencial, sai calado: o git segue para o próximo helper ou pergunta.
[ -n "$USUARIO" ] && [ -n "$TOKEN" ] || exit 0

echo "username=$USUARIO"
echo "password=$TOKEN"
