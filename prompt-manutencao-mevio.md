Implemente no projeto **Minuta Certa** a consulta dinâmica de planos comerciais pelo **Mévio**, utilizando como fonte de verdade os dados atuais do próprio sistema.

## Objetivo

Quero que o Mévio consiga responder corretamente, em tempo real, perguntas como:

* Quais planos estão disponíveis atualmente?
* Quanto custa o Plano Básico?
* Qual a franquia do Plano Pro?
* Existe plano anual?
* Qual plano tem mais minutas?
* Um determinado plano ainda pode ser contratado?
* Qual é o meu plano atual?
* Quantas minutas eu ainda tenho?
* Quando minha assinatura renova?

A resposta do Mévio não deve depender de valores fixos no Markdown do manual.

## Regra principal

A **fonte de verdade comercial** deve ser o cadastro atual de planos utilizado pelo próprio Minuta Certa.

Não crie uma segunda tabela ou catálogo independente apenas para o Mévio.

Se já existe uma tabela `planos`, serviço, função ou endpoint que alimenta **Alterar Meu Plano**, reutilize essa mesma fonte.

## Planos removidos

Considere como regra de produto atual:

* **Plano Self: removido definitivamente**;
* **Plano SuperPrompt: removido definitivamente**;
* nenhum dos dois deve aparecer como plano disponível;
* nenhum dos dois deve ser recomendado pelo Mévio;
* nenhum dos dois deve constar na resposta normal do catálogo comercial.

Se ainda existirem resíduos desses planos em seed, fallback, constantes ou banco, não permita que o endpoint do Mévio os exponha como disponíveis.

## 1. Endpoint de catálogo para o Mévio

Implemente um endpoint interno autenticado, preferencialmente:

`GET /internal/ai/plans`

ou utilize o padrão de rotas internas já existente no projeto, se houver convenção melhor.

Esse endpoint deve retornar apenas dados necessários para atendimento.

A resposta deve incluir, quando existirem no cadastro:

* `id`;
* nome comercial;
* descrição;
* status;
* disponibilidade para nova contratação;
* franquia de minutas;
* preço;
* periodicidades;
* preços por periodicidade;
* destaque comercial;
* benefícios ou recursos exibidos na tela de planos;
* observações comerciais necessárias;
* data/hora da consulta ou atualização.

## 2. Fonte de verdade

Antes de implementar, identifique exatamente de onde a tela:

**Alterar Meu Plano**

obtém atualmente:

* nomes;
* preços;
* franquias;
* descrições;
* periodicidades;
* disponibilidade;
* destaque.

Reutilize essa fonte.

Se houver fallback local no frontend/backend, evite que ele se torne uma fonte comercial divergente para o Mévio.

Documente na implementação qual é a fonte considerada canônica.

## 3. Estados dos planos

Estruture o backend para distinguir pelo menos:

### Ativo

Plano disponível para novas contratações.

### Legado

Plano que não pode mais ser contratado, mas eventualmente ainda possui assinantes existentes.

### Removido

Plano definitivamente descontinuado e que não deve ser apresentado como alternativa comercial.

Mesmo que atualmente não existam planos legados, deixe a estrutura preparada para esse estado futuro.

Na resposta padrão de `GET /internal/ai/plans`, priorize os planos ativos.

Se houver necessidade de retornar planos legados, identifique-os claramente.

Planos removidos não devem aparecer para o Mévio como opções de contratação.

## 4. Regras para o Mévio

Atualize o cliente/ferramenta utilizada pelo Mévio para que perguntas comerciais sobre planos consultem primeiro a API dinâmica.

Exemplos:

### Pergunta

“Quais são os planos?”

O Mévio deve consultar a API e listar somente os planos atualmente disponíveis.

### Pergunta

“Quanto custa o Pro?”

O Mévio deve consultar os dados vigentes, e não usar preço gravado no Markdown.

### Pergunta

“Qual plano tem 220 minutas?”

Deve consultar o catálogo atual.

### Pergunta

“O Self ainda existe?”

Se um plano estiver classificado como removido e não fizer parte do catálogo retornado, o Mévio pode responder, com base na regra oficial de produto/documentação, que ele não é mais oferecido.

Não faça o Mévio inventar preços, franquias ou condições quando a API estiver indisponível.

## 5. Falha na consulta

Se o endpoint estiver indisponível:

* o Mévio não deve responder preços ou franquias a partir de memória antiga;
* deve informar que não conseguiu consultar as condições comerciais atualizadas;
* pode orientar o usuário a consultar **Alterar Meu Plano** dentro do Minuta Certa.

Não utilize valores estáticos do manual como fallback para preços atuais.

## 6. Endpoint da conta do usuário

Além do catálogo geral, avalie e implemente, se compatível com a arquitetura atual, um endpoint interno autenticado para consultar o plano do usuário logado.

Sugestão:

`GET /internal/ai/account/plan`

A resposta pode incluir:

* plano atual;
* nome do plano;
* status da assinatura;
* saldo atual de minutas;
* franquia total;
* data de início;
* data de renovação;
* periodicidade;
* situação de pagamento, se apropriado para suporte.

Não inclua informações financeiras sensíveis desnecessárias, números de cartão ou dados do gateway de pagamento.

## 7. Segurança do endpoint da conta

O endpoint de plano da conta deve garantir que:

* o usuário só possa consultar os próprios dados;
* o token usado pelo Mévio não permita consultar contas arbitrárias;
* não seja possível passar `user_id` ou e-mail livremente para obter dados de terceiros;
* nenhuma informação sensível seja gravada em logs.

Siga o mesmo padrão de autenticação interna já utilizado pela API de documentação do Mévio, adaptando-o quando necessário.

## 8. Integração com o cliente do Mévio

O Mévio atualmente consulta documentação do Minuta Certa por meio do cliente interno utilizado pela skill `minuta-certa-manual`.

Amplie a integração de forma organizada.

Pode ser criado, por exemplo:

* comando para listar planos atuais;
* comando para consultar um plano específico;
* comando para consultar o plano/saldo da conta atual.

Evite exigir que o Mévio utilize comandos genéricos de terminal além do necessário.

Se for possível acrescentar essas funções ao cliente Python já existente, prefira centralizar ali.

Exemplos conceituais:

`manual_client.py plans`

`manual_client.py plan pro`

`manual_client.py account-plan`

Adapte os nomes ao padrão real do projeto.

## 9. Uso pelo RAG / SOUL / Skill

Atualize a documentação/instruções internas do Mévio para definir a prioridade das fontes.

Para perguntas sobre:

### Uso do Minuta Certa

Consultar o manual/RAG.

### Preços, franquias e planos disponíveis

Consultar a API dinâmica de planos.

### Plano e saldo do usuário atual

Consultar o endpoint autenticado da conta.

A informação dinâmica deve prevalecer sobre qualquer exemplo ou valor antigo existente no Markdown.

## 10. Não misturar plano com saldo

Diferencie claramente:

* catálogo de planos;
* franquia do plano;
* saldo atual do usuário.

Exemplo:

O plano pode possuir franquia de 220 minutas, enquanto a conta do usuário pode ter apenas 37 restantes.

O Mévio deve compreender essa diferença.

## 11. Copiloto de Ajuste Fino

Considere como regra atual já implementada:

**O Copiloto de Ajuste Fino não consome saldo de minutas.**

Portanto, se o Mévio responder dúvidas sobre saldo, não deve contabilizar refinamentos do Copiloto como consumo.

Apenas gerações completas concluídas com sucesso consomem uma unidade de saldo, conforme a regra atual do produto.

## 12. Preços e periodicidades

Não codifique preços diretamente no cliente do Mévio.

Não codifique preços no `SOUL.md`.

Não codifique preços na skill.

Não utilize preços existentes no `09-configuracoes-conta-e-plano.md` como fonte comercial.

Sempre utilize o backend do Minuta Certa.

## 13. Cache

Se desejar adicionar cache para reduzir chamadas:

* utilize TTL curto;
* invalide ou expire automaticamente;
* preços e disponibilidade não podem permanecer indefinidamente em cache;
* não use cache do catálogo para saldo individual do usuário.

Explique se algum cache for implementado.

## 14. Testes obrigatórios

Depois da implementação, teste pelo menos:

### Catálogo

Perguntar ao Mévio:

“Quais são os planos disponíveis atualmente?”

Ele deve responder somente com planos ativos.

### Preço

“Quanto custa o Plano Pro?”

Deve refletir o cadastro atual do Minuta Certa.

### Franquia

“Quantas minutas tem o Plano Básico?”

Deve refletir o cadastro atual.

### Plano removido

“O Plano Self ainda está disponível?”

Não deve aparecer como opção de contratação.

### Outro plano removido

“Posso contratar o SuperPrompt?”

Não deve ser oferecido.

### Conta

“Qual é o meu plano?”

Deve retornar o plano da conta autenticada, se o endpoint estiver disponível.

### Saldo

“Quantas minutas ainda tenho?”

Deve consultar o saldo atual da conta, não a franquia máxima.

### Copiloto

“O Copiloto gasta minhas minutas?”

Resposta esperada:

“Não. O Copiloto de Ajuste Fino não consome saldo de minutas.”

### Falha

Simule indisponibilidade do endpoint de planos.

O Mévio deve informar que não conseguiu consultar as condições comerciais atualizadas e não deve inventar valores.

## 15. Compatibilidade com o manual

Não remova a documentação geral existente em:

`docs/manual/09-configuracoes-conta-e-plano.md`

O manual continua sendo útil para explicar:

* onde ficam os planos;
* como alterar plano;
* como funciona saldo;
* como acessar Configurações.

Mas valores dinâmicos devem vir da API.

## 16. Limpeza de referências removidas

Faça também uma busca por:

* `self`;
* `Plano Self`;
* `super-prompt`;
* `SuperPrompt`;
* `Plano Super Prompt`.

Liste todos os resíduos encontrados.

Não remova automaticamente código que possa ser necessário para integridade histórica sem antes avaliar dependências.

Porém:

* nenhum plano removido deve aparecer na contratação;
* nenhum plano removido deve ser exposto ao Mévio como opção atual;
* nenhum fallback comercial deve reintroduzir Self ou SuperPrompt.

## 17. Observabilidade

Adicione logs mínimos e seguros para diagnóstico da integração, por exemplo:

* consulta de catálogo bem-sucedida;
* falha no endpoint;
* quantidade de planos retornados.

Nunca grave:

* chaves;
* tokens;
* conteúdo de processos;
* dados pessoais desnecessários.

## Saída esperada

Primeiro faça a análise do código atual.

Depois implemente.

Ao final, apresente:

## IMPLEMENTADO

Liste:

* endpoints criados;
* arquivos alterados;
* cliente do Mévio alterado;
* skill/instruções alteradas;
* testes realizados.

## FONTE DE VERDADE

Explique qual tabela/serviço é a fonte canônica dos planos.

## PLANOS RETORNADOS NO TESTE

Mostre apenas:

* ID;
* nome;
* status;
* disponibilidade para contratação;

sem expor dados sensíveis.

## TESTES DO MÉVIO

Mostre as perguntas utilizadas e um resumo das respostas obtidas.

## PENDÊNCIAS

Liste qualquer decisão de produto ou problema encontrado.

Não altere preços nem franquias comerciais por iniciativa própria.
Não recrie o Plano Self.
Não recrie o SuperPrompt.

