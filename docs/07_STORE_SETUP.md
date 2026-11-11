# 07 — Configuração da loja (Payhip)

## Plataforma escolhida: **Payhip (plano Free)**
Fonte: `market-research/PLATFORM_RESEARCH.md`. Os dados vieram de trechos de busca de 2026-11-11 e **devem ser reconferidos** nas páginas oficiais quando você criar a conta.

| Critério | Payhip Free | Alternativa mais próxima (Gumroad) |
|---|---|---|
| Mensalidade | US$ 0 | US$ 0 |
| Taxa por venda | 5% (+ taxa do PayPal/Stripe) | 10% + US$ 0,50 (30% em vendas pelo Discover) |
| Vendedor do Brasil | Brasil listado para PayPal e Stripe | Recebimento no Brasil não confirmado (o PayPal Connect não é oferecido no BR) |
| Entrega automática | Sim | Sim |
| Checkout em USD | Sim | Sim |
| Sales tax EUA / VAT UE | A Payhip trata (EUA desde 1º/jul/2026) | O Gumroad trata (merchant of record) |
| Páginas próprias, cupons, afiliados | Sim, no plano Free | Parcial |

**Por que a Payhip:** é a única opção com caminho de recebimento no Brasil confirmado. O dinheiro cai direto no seu PayPal, sem retenção pela plataforma.

## Estados da loja (não são equivalentes)
| Estado | Situação em 2026-11-11 |
|---|---|
| Produto pronto | ✅ CONCLUÍDO E TESTADO (`products/release/`) |
| Loja pronta para configuração (textos, imagens, políticas, arquivos) | ✅ CONCLUÍDO (`store/PAYHIP_LISTINGS.md`, `brand/covers/`, `website/dist/*.html`) |
| Loja publicada | ⏳ PENDENTE DE AUTORIZAÇÃO: precisa da sua conta |
| Pagamentos habilitados | ⏳ BLOQUEADO POR TERCEIROS: verificação do PayPal (KYC) |
| Loja apta a receber pedidos | ⏳ depende dos dois itens acima e da compra-teste |
| Primeira venda concluída | ❌ não ocorreu, nenhuma venda foi registrada |

## Passo a passo para você (cerca de 1 a 2 horas)
**Sua identidade fica privada.** A Payhip e o PayPal pedem seus dados reais (CPF, banco) só para verificação. Na loja pública aparece apenas **TidyMargin**.

1. **Gmail de suporte:** crie um Gmail novo só para a marca, por exemplo `tidymargin.support@gmail.com` (é grátis). Use-o para a Payhip, o PayPal Business e a Cloudflare.
2. **Processador de pagamento (sem CNPJ):** o PayPal **Empresarial** no Brasil exige CNPJ. Situação em 2026-11-11: o dono não tem CNPJ, então:
   - **Recomendado: Stripe, pessoa física (CPF).** Crie a conta em stripe.com (país Brasil, tipo Individual), com conta bancária no mesmo CPF. Defina o nome público como **TidyMargin**, o descritor da fatura como **TIDYMARGIN** e o e-mail de suporte como tidymargin.help@gmail.com. Confira no painel as tarifas de cartão internacional e de conversão.
   - **Reserva: PayPal Conta Pessoal (CPF).** O comprador pode ver o seu nome no comprovante.
   - **Formalização (MEI):** é uma decisão do dono com um contador. Tem custo mensal (DAS).
   - **Nunca** use CNPJ inventado ou de terceiros.
3. **Payhip:** em payhip.com crie a conta Free com o Gmail da marca. Depois:
   - em Settings > Payments, conecte a Stripe (ou o PayPal);
   - confira a moeda USD;
   - em Store name e branding, use os textos de `store/PAYHIP_LISTINGS.md` e o logo `brand/logo/icon-512.png`.
4. **Produtos:** crie 4 produtos digitais, enviando os ZIPs de `products/release/`, as capas de `brand/covers/` e as capturas de `brand/screenshots/` como imagens extras. Cole títulos, descrições, tags e FAQ de `store/PAYHIP_LISTINGS.md`.
   - Preços: Free US$ 0, Starter US$ 9, Complete US$ 19, Premium US$ 29.
5. **Políticas:** cole o conteúdo de `website/dist/privacy.html`, `terms.html` e `refund.html` nas páginas de política da Payhip.
6. **Teste de entrega:** baixe o produto **grátis** com outro e-mail seu e confira o e-mail e o download.
7. **Teste de checkout pago (opcional, com a sua autorização):** crie um cupom de 100% (preço US$ 0) só para você e "compre" o Starter. Valide a entrega e depois apague o cupom. Uma compra real de US$ 9 seguida de reembolso também testa o PayPal, mas tem custo de taxa. Decida você.
8. **Links:** copie os links de checkout de cada produto para `deployment/store_config.json` e rode `python3 kit/build_site.py`.
9. **Site:** publique `website/dist/` no Cloudflare Pages (ver `deployment/DEPLOY.md`).

## Fluxo de entrega (nativo da Payhip)
1. O cliente clica em "Buy".
2. Faz o checkout na Payhip (PayPal ou cartão via PayPal).
3. O PayPal confirma o pagamento.
4. A Payhip mostra o download e envia um e-mail com o link.
5. O pedido aparece em Payhip > Sales.
6. Você exporta o CSV para `analytics/data/sales.csv`.
7. Roda os agentes.

## Tratamento de erros
| Situação | Procedimento |
|---|---|
| Pagamento recusado | A Payhip/PayPal mostra o erro ao cliente. Não há pedido. Se ele escrever, sugira outro cartão ou o PayPal. |
| Pagamento pendente (eCheck PayPal) | Não conta como venda (o agente separa). A entrega acontece quando o PayPal confirmar. |
| Pagamento duplicado | Reembolse o duplicado em Payhip > Sales > Refund (é você quem faz). |
| Reembolso | Política de 14 dias. O agente só prepara a resposta. Você executa na Payhip. |
| Chargeback | Responda no PayPal Resolution Center com o comprovante de download da Payhip. Prioridade máxima. |
| Link expirado / limite de downloads | Payhip > Sales > pedido > reenviar link. Ajuste o limite de downloads no produto. |
| Falha de entrega / e-mail não chegou | Peça para verificar o spam e reenvie pelo painel. |
| Cliente não consegue abrir | Use os modelos de resposta (Excel antigo → Excel Web ou Sheets; celular → computador). |
