# 11 — Modelo financeiro

## Custos atuais: **US$ 0**
Ver `../COSTS.md`. Não há nenhuma assinatura, domínio, anúncio, ferramenta paga ou teste com cobrança automática.

## Margem por venda (variável)
| Item | Starter US$ 9 | Complete US$ 19 | Premium US$ 29 |
|---|---|---|---|
| Payhip 5% | 0,45 | 0,95 | 1,45 |
| PayPal ~6,4% + ~0,30 (reconferir) | ~0,88 | ~1,52 | ~2,16 |
| Conversão ~3,5% | ~0,27 | ~0,58 | ~0,89 |
| **Líquido estimado** | **≈ 7,41** | **≈ 15,96** | **≈ 24,51** |

O custo de produção por unidade é zero: um arquivo digital, sem estoque. Os valores **não incluem** IOF nem impostos brasileiros.

## Cenários ilustrativos (NÃO são previsões)
São só simulações de quantas vendas cobririam um objetivo:
- Pagar um domínio (cerca de US$ 12 por ano) → 1 venda Complete.
- Cada 10 vendas com mix 30% Starter, 50% Complete e 20% Premium → líquido ≈ 10 × (0,3×7,41 + 0,5×15,96 + 0,2×24,51) ≈ **US$ 151**.

Nenhum faturamento é garantido. O primeiro número real virá de `analytics/data/sales.csv`.

## Regra de reinvestimento (implementada no agente financeiro)
1. Confirme que o pagamento chegou ao PayPal.
2. Valor líquido = receita − taxas − reembolsos.
3. Reserva para reembolso = 10% das vendas dos últimos 30 dias.
4. Reserva de impostos = % definido com o contador, em `finance.json`.
5. **Saldo livre** = líquido − reservas − o que já foi sacado ou gasto.
6. Proposta: 40% reserva de caixa, 20% correções, 20% melhoria do produto e 20% domínio ou pequenos testes.
7. **Você decide.** Nada é gasto automaticamente.

## Prioridades de reinvestimento
1. Reserva financeira.
2. Correção de problemas (do suporte e do QA).
3. Melhoria do produto (versão em espanhol, vídeo).
4. Produtos complementares (Airbnb turnover add-on, Lawn Care Kit).
5. Domínio próprio (cerca de US$ 10–15 por ano).
6. Conversão (mais capturas de tela, vídeo na página).
7. Pequenos testes de anúncio no Pinterest, **só com saldo livre e com a sua aprovação**.
8. Automação adicional.

## Riscos financeiros
- O PayPal pode reter fundos de contas novas.
- Variação cambial.
- Reembolsos ou chargebacks.
- Tarifas reais diferentes das pesquisadas. Reconferir.
- Obrigações fiscais no Brasil. Consulte um contador antes de sacar valores relevantes.
