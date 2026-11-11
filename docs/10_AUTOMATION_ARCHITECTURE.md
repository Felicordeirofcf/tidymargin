# 10 — Arquitetura de automação (agentes)

Código: `agents/`. Execução **sob demanda**. Não há serviço rodando em segundo plano.

```
python3 agents/run_agents.py            # CEO: roda QA, vendas, finanças, suporte e conteúdo + painel
python3 agents/run_agents.py <agente>   # ceo, market_research, product_manager, content_marketing,
                                        # sales_analyst, customer_support, financial_controller, quality_monitor
python3 agents/run_agents.py dashboard
```

| # | Agente | Lê | Faz | Nunca faz |
|---|---|---|---|---|
| 1 | **CEO** | resultados dos outros | Coordena, prioriza (bloqueios → receita → crescimento) e recomenda | Assumir despesas |
| 2 | **Market Research** | `competitors.csv` | Visita páginas **públicas** só se o `robots.txt` permitir, com até 15 requisições, 3 s de intervalo e timeout. Registra título e preços visíveis para conferência humana. | Contornar bloqueios, usar dados privados, tratar avaliações como vendas |
| 3 | **Product Manager** | testes, suporte | Roda a suíte de testes, bloqueia upload se falhar, organiza o backlog | Publicar arquivos |
| 4 | **Content Marketing** | `content_calendar.csv` | Detecta alegações proibidas (garantia, renda, depoimento, estrelas) e propõe as próximas 3 publicações | Postar (não existe integração autorizada) |
| 5 | **Sales Analyst** | `sales.csv`, `traffic.csv` | Separa pedidos, pagamentos confirmados, pendentes, reembolsos e chargebacks. Calcula receita, taxas, ticket médio, conversão, origem e diagnósticos. | Inventar dados: sem arquivo = "no data" |
| 6 | **Customer Support** | `support_inbox.csv` | Classifica mensagens, escreve rascunhos (download, Sheets, versão do Excel, uso, upgrade) e **escala** reembolso, chargeback, questões jurídicas e clientes irritados | Enviar e-mail, fazer reembolso |
| 7 | **Financial Controller** | `sales.csv`, `finance.json` | Receita líquida, reserva para reembolso (10% dos últimos 30 dias), reserva de imposto (% definido pelo contador), saldo livre e **proposta** de reinvestimento | Movimentar dinheiro |
| 8 | **Quality Monitor** | ZIPs, site, config | Testa a integridade dos ZIPs e das abas, links internos, completude da config e status HTTP das URLs próprias (site/checkout) | Alterar a loja |

## Proteções (`agents/common.py`)
- **Permissões mínimas:** cada agente declara as ações que pode fazer. As ações críticas são `spend_money`, `refund`, `send_email`, `publish_content`, `change_price`, `delete_data`, `move_money` e `create_account`. Elas são **proibidas no código**: o agente só pode escrevê-las em `reports/PENDING_APPROVALS.md` para você decidir.
- **Limites:** 120 s por agente, 50.000 linhas por arquivo, 15 requisições externas.
- **Tratamento de erros:** a falha de um agente vira um relatório "PROBLEM" e não derruba os outros.
- **Logs** em JSON lines (`agents/logs/`), com e-mails mascarados (hash).
- **Dados de clientes** (`sales.csv`, `support_inbox.csv`, rascunhos) ficam fora do Git (`.gitignore`).

## Saídas
- `reports/agent_runs/AAAA-MM-DD-<agente>.md`
- `reports/PENDING_APPROVALS.md`
- `reports/support_drafts/`
- `analytics/dashboard.html` (painel de controle)

## Agendamento (opcional, não ativado)
Para rodar sem você, seria possível usar um cron do GitHub Actions, grátis dentro dos limites. **Não foi ativado**, por duas razões: os dados de vendas exigem o export manual da Payhip (não há API gratuita confirmada) e você pediu controle sobre as ações. Se quiser, o QA de links pode ser agendado depois.

## Painel de controle
`analytics/dashboard.html` mostra:
- visitantes, cliques em compra, vendas e conversão;
- receita bruta, taxas e receita líquida;
- reembolsos, chargebacks, produtos vendidos e ticket médio;
- origem do tráfego e conteúdos publicados;
- saldo livre para reinvestimento.

Ele não confunde pedido com pagamento, nem receita líquida com lucro após impostos.
