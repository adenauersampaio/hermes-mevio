---
name: minuta-certa-manual
description: Consulta a documentação oficial, catálogo dinâmico de planos comerciais e dados de plano/saldo da conta no Minuta Certa.
---

# Skill: Suporte e Consulta Dinâmica do Minuta Certa

Esta skill equipa o Mévio com a ferramenta oficial `manual_client.py` para responder dúvidas sobre o funcionamento do Minuta Certa, seus planos comerciais vigentes e a situação cadastral/saldo do usuário.

## Localização do Script
```bash
python3 /opt/data/skills/minuta-certa/manual/scripts/manual_client.py <comando>
```
*(ou relativamente onde a skill estiver instalada)*

---

## 1. Prioridade e Escolha de Fonte de Dados

O Mévio deve obrigatoriamente direcionar cada tipo de pergunta para a sua fonte de verdade apropriada:

| Tipo de Pergunta | Fonte de Verdade | Comando Recomendado |
| :--- | :--- | :--- |
| **Funcionamento e Recursos**<br>*(ex: Como anonimizar? Como exportar? O que é OCR? Como criar perfis?)* | **Manual Oficial / RAG** | `manual_client.py search "<termo>"`<br>`manual_client.py read <slug>` |
| **Catálogo Comercial Vigente**<br>*(ex: Quais planos existem? Quanto custa o Pro? Qual a franquia do Básico? Tem plano anual?)* | **API Dinâmica de Planos** | `manual_client.py plans`<br>`manual_client.py plan <id>` |
| **Plano e Saldo do Usuário**<br>*(ex: Qual é meu plano? Quantas minutas eu ainda tenho? Quando renova minha assinatura?)* | **API Autenticada da Conta** | `manual_client.py account-plan` |

> [!IMPORTANT]
> A informação dinâmica obtida da API **SEMPRE prevalece** sobre qualquer exemplo ou menção histórica existente em arquivos Markdown ou em memórias antigas.

---

## 2. Regras Comerciais e Anti-Alucinação

1. **Nunca inventar preços ou franquias**:
   - Se o usuário perguntar preços, franquias ou periodicidades, execute `manual_client.py plans` ou `manual_client.py plan <id>`.
   - Se a consulta falhar (erro de conexão ou indisponibilidade da API), **NÃO invente valores** e **NÃO use memórias antigas**. Informe educadamente que não foi possível consultar os valores vigentes no momento e oriente o usuário a acessar o menu **Alterar Meu Plano** dentro do Minuta Certa.

2. **Diferença entre Franquia e Saldo**:
   - **Franquia**: Capacidade mensal nominal do plano contratado (ex: 220 minutas/mês no Plano Pro).
   - **Saldo Atual**: Quantidade de minutas restantes na conta do usuário no ciclo atual (ex: 37 minutas restantes).
   - Nunca confunda franquia com saldo remanescente.

3. **Copiloto de Ajuste Fino**:
   - O Copiloto de Ajuste Fino **NÃO consome saldo de minutas**.
   - Apenas a ação **Gerar Minuta** concluída com sucesso consome 1 unidade de saldo. Falhas e interrupções não consomem.

4. **Planos Removidos / Descontinuados**:
   - **Plano Self (BYOK)**: Removido definitivamente do produto.
   - **Plano SuperPrompt**: Removido definitivamente do produto.
   - Nenhum dos dois faz parte das opções comerciais do Minuta Certa e eles nunca devem ser oferecidos ou listados como planos disponíveis.
   - Se o usuário perguntar diretamente por um deles, informe que o plano foi descontinuado e não faz mais parte das opções comerciais do Minuta Certa, apresentando os planos ativos retornados pela API dinâmica.

---

## 3. Guia de Comandos do Cliente

### Listar Planos Comerciais Ativos
```bash
python3 manual_client.py plans
```

### Consultar Plano Específico
```bash
python3 manual_client.py plan pro
python3 manual_client.py plan basico
python3 manual_client.py plan premium
```

### Consultar Plano e Saldo da Conta do Usuário
```bash
python3 manual_client.py account-plan
```

### Buscar na Documentação de Funcionamento
```bash
python3 manual_client.py search "anonimizacao"
python3 manual_client.py search "modelos de estilo"
python3 manual_client.py search "copiloto"
```

### Ler Capítulo Completo do Manual
```bash
python3 manual_client.py read 00-visao-geral
python3 manual_client.py read 04-anonimizacao-lgpd
python3 manual_client.py read 09-configuracoes-conta-e-plano
```

### Listar Todos os Capítulos do Manual
```bash
python3 manual_client.py list
```
