# 08 — Configuração de pagamentos

**Nenhum pagamento real está ativo.** Só declare "pagamentos habilitados" depois que o PayPal aprovar a conta e uma compra-teste for concluída.

## Atualização (2026-11-11): sem CNPJ
O PayPal Empresarial no Brasil pede CNPJ. Caminho principal: **Stripe, pessoa física com CPF** (a Payhip aceita Stripe no Brasil), com o nome público e o descritor da fatura "TidyMargin". As tarifas da Stripe para cartão internacional e conversão **ainda não foram confirmadas**: confira no painel e atualize o cálculo abaixo, que usa o PayPal como referência. Reserva: PayPal Conta Pessoal.

## Fluxo do dinheiro
Cliente (USD) → Payhip (retém 5%) → PayPal Brasil (tarifa de recebimento internacional) → saldo em USD → saque para o banco brasileiro com conversão (spread) → BRL.

## Tarifas (trechos de busca de 2026-11-11, reconferir em paypal.com/br/webapps/mpp/merchant-fees)
- **Payhip Free:** 5% por venda (help.payhip.com/article/102-payhip-pricing-plans).
- **PayPal BR, venda internacional:** cerca de 6,40% + tarifa fixa. Os US$ 0,30 da tarifa fixa vêm só de fonte secundária.
- **Conversão de moeda:** margem de cerca de 3,50%.
- **IOF e impostos brasileiros:** não incluídos. Consulte um contador.

## Líquido estimado por venda
O cálculo inclui a Payhip, o PayPal e a conversão de 3,5%. Não inclui IOF nem impostos.
| Preço | Líquido estimado (USD) | % que sobra |
|---|---|---|
| US$ 9 | ≈ 7,41 | 82% |
| US$ 19 | ≈ 15,96 | 84% |
| US$ 29 | ≈ 24,51 | 85% |

## Configuração segura
- Nunca coloque senhas, tokens ou documentos em arquivos do repositório. `store_config.json` só aceita links públicos.
- Ative a verificação em duas etapas (2FA) na Payhip, no PayPal, na Cloudflare e no Gmail.
- A conta PayPal e a conta bancária devem estar no **mesmo CPF**.
- Não tente contornar restrições geográficas ou bancárias. Se o PayPal negar a conta, a alternativa documentada é o Stripe Brasil, com CPF (Payhip suporta), depois de conferir as tarifas.

## Recebimento e saque
- O dinheiro entra no saldo do PayPal pouco depois da venda. O PayPal pode reter fundos de contas novas.
- Para sacar, use "Transferir para o banco". Confira a cotação antes.
- **Reembolsos** saem do saldo do PayPal. Mantenha a reserva de 10% (o agente financeiro calcula).

## Impostos (consulte um contador; isto não é orientação fiscal)
- **Nos EUA:** a Payhip calcula e recolhe o sales tax dos estados (desde jul/2026) e o VAT da UE/UK.
- **No Brasil:** temas para levar ao contador: Carnê-Leão (renda do exterior para PF), MEI ou outra formalização, exportação de serviços e IOF. **Não foi aberta nenhuma empresa** e nenhum registro foi inventado.
