# 13 — Manual de operações

## Rotina semanal (cerca de 30 min, além do conteúdo diário)
1. Payhip > Sales > **Export CSV** → ajuste as colunas para `date,order_id,product,status,gross_usd,fees_usd,source,country` → salve em `analytics/data/sales.csv`.
2. Cloudflare Web Analytics → copie as visitas por origem para `analytics/data/traffic.csv`. Os cliques de compra aparecem na Payhip (visitas ao produto).
3. Cole as mensagens de suporte da semana em `analytics/data/support_inbox.csv` (opcional).
4. Rode `python3 agents/run_agents.py`.
5. Leia `reports/agent_runs/` e `reports/PENDING_APPROVALS.md` e abra `analytics/dashboard.html`.
6. Responda aos clientes (os rascunhos ficam em `reports/support_drafts/`) e execute você mesmo o que aprovar.

## Suporte ao cliente
- **Canal:** e-mail (o Gmail da marca), configurado na Payhip.
- **Prazo publicado:** até 2 dias úteis.
- **Central de ajuda:** `website/dist/help.html` (download, Excel, Sheets, uso, problemas, reembolso, contato).
- **Modelos de resposta:** download, Google Sheets, versão do Excel, como usar, upgrade (`agents/team.py`, TEMPLATES).
- **Encaminhar para você (o agente não responde):** reembolso, chargeback, questão jurídica, cliente irritado e tudo que não se encaixa nas categorias.
- **Nunca** peça senha ou cartão ao cliente.
- **Nunca** envie mensagens comerciais não solicitadas.

## Reembolso (você executa)
Payhip > Sales > pedido > Refund. Registre o status `refunded` no `sales.csv`.

## Diagnóstico quando há visitas e nenhuma venda
Mude **uma coisa de cada vez**, com hipótese e prazo. Não mexa no preço sem critério.

| Sintoma | Hipótese | Teste |
|---|---|---|
| Visitas, mas poucos cliques no "Buy" | Oferta pouco clara ou desconfiança | Vídeo de 60 s na página do produto, mais capturas, FAQ mais visível |
| Cliques, mas nenhuma venda | Problema no checkout ou preço inesperado | Faça você o checkout grátis ou com cupom; compare o preço com 3 concorrentes |
| Muitos downloads grátis, poucas vendas | Upsell fraco | E-mail de boas-vindas da Payhip com um cupom de 20% por 7 dias |
| Tráfego de baixa qualidade | Canal errado | Compare a conversão por origem no painel e corte o pior canal |
| Reembolsos acima de 10% | Expectativa errada | Leia os motivos e ajuste a descrição e as capturas |

## Atualização do produto
1. Edite `kit/`.
2. Rode `./build_all.sh` (todos os testes precisam passar).
3. Suba o ZIP novo na Payhip (Edit product > replace file). A Payhip permite avisar os compradores da atualização.
4. Aumente `VERSION` em `kit/brand.py`.

## Backup
Tudo fica no Git: código, produtos e documentação. Os dados de vendas e de clientes ficam fora do Git. Guarde-os no seu Google Drive.
