FROM nousresearch/hermes-agent:latest

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       nano \
       curl \
       git \
       python3 \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório de padrões para sincronização segura no bootstrap
RUN mkdir -p /opt/hermes-defaults/skills/minuta-certa-manual \
             /opt/hermes-defaults/templates \
             /opt/hermes-defaults/scripts

COPY skills /opt/hermes-defaults/skills/
COPY templates /opt/hermes-defaults/templates/
COPY scripts /opt/hermes-defaults/scripts/

RUN chmod +x /opt/hermes-defaults/scripts/bootstrap.sh \
    && chmod +x /opt/hermes-defaults/scripts/ponte_http.py \
    && chmod +x /opt/hermes-defaults/skills/minuta-certa-manual/scripts/manual_client.py \
    && chown -R hermes:hermes /opt/hermes-defaults

# Ponte HTTP: serviço supervisionado pelo s6, registrado no bundle `user` da
# imagem base (ao lado de `dashboard` e `main-hermes`). Vai para /etc, e não
# para /opt/data, porque o volume persistente sobrepõe o que for embutido
# ali — e porque um serviço é parte da imagem, não dado do agente. O s6-overlay
# compila a base de serviços na subida do contêiner, então basta depositar os
# arquivos-fonte aqui.
COPY s6/ponte-mevio /etc/s6-overlay/s6-rc.d/ponte-mevio
RUN mkdir -p /etc/s6-overlay/s6-rc.d/ponte-mevio/dependencies.d \
    && touch /etc/s6-overlay/s6-rc.d/ponte-mevio/dependencies.d/base \
    && touch /etc/s6-overlay/s6-rc.d/user/contents.d/ponte-mevio \
    && chmod +x /etc/s6-overlay/s6-rc.d/ponte-mevio/run \
                /etc/s6-overlay/s6-rc.d/ponte-mevio/finish

USER hermes

ENTRYPOINT ["/opt/hermes-defaults/scripts/bootstrap.sh"]
