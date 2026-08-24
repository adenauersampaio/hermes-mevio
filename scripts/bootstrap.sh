#!/bin/bash
set -e

DATA_DIR="${HERMES_DATA_DIR:-/opt/data}"
DEFAULTS_DIR="/opt/hermes-defaults"

echo "[Mévio Bootstrap] Inicializando ambiente do agente..."

# 1. Garante que os diretórios necessários existam no volume persistente
mkdir -p "$DATA_DIR/skills/minuta-certa/manual/scripts"
mkdir -p "$DATA_DIR/skills/minuta-certa/manual"

# 2. Sincroniza a skill e o cliente Python (atualização segura)
if [ -d "$DEFAULTS_DIR/skills/minuta-certa-manual" ]; then
  echo "[Mévio Bootstrap] Sincronizando skill minuta-certa-manual..."
  cp -f "$DEFAULTS_DIR/skills/minuta-certa-manual/SKILL.md" "$DATA_DIR/skills/minuta-certa/manual/SKILL.md"
  cp -f "$DEFAULTS_DIR/skills/minuta-certa-manual/scripts/manual_client.py" "$DATA_DIR/skills/minuta-certa/manual/scripts/manual_client.py"
  chmod +x "$DATA_DIR/skills/minuta-certa/manual/scripts/manual_client.py"
fi

# 3. Inicializa SOUL.md e USER.md caso não existam no volume (preserva customizações locais)
if [ ! -f "$DATA_DIR/SOUL.md" ] && [ -f "$DEFAULTS_DIR/templates/SOUL.md" ]; then
  echo "[Mévio Bootstrap] Instalando SOUL.md inicial..."
  cp "$DEFAULTS_DIR/templates/SOUL.md" "$DATA_DIR/SOUL.md"
fi

if [ ! -f "$DATA_DIR/USER.md" ] && [ -f "$DEFAULTS_DIR/templates/USER.md" ]; then
  echo "[Mévio Bootstrap] Instalando USER.md inicial..."
  cp "$DEFAULTS_DIR/templates/USER.md" "$DATA_DIR/USER.md"
fi

echo "[Mévio Bootstrap] Inicialização concluída com sucesso. Iniciando agente..."

# Devolve o controle ao entrypoint da imagem base, SEMPRE.
#
# Aqui morava `exec hermes` quando não havia argumentos — e isso teria
# derrubado o contêiner no primeiro build de verdade. O CMD da imagem base é
# vazio, então esse ramo era o que ia rodar; `hermes` não está no PATH desta
# altura (só entra depois que o /init do s6 semeia o ambiente), e mesmo que
# estivesse, executá-lo direto pularia o `/init` inteiro: sem s6, sem painel,
# sem gateway de mensageria, sem a ponte HTTP.
#
# `entrypoint-dispatch.sh` é quem decide entre `/init` (o caminho normal, com a
# árvore de supervisão completa) e o modo degradado de runtimes que não dão
# PID 1 à imagem. Com `exec`, ele herda o PID 1 e essa decisão continua certa.
exec /opt/hermes/docker/entrypoint-dispatch.sh "$@"
