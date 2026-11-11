# Pesquisa de Plataformas e Infraestrutura Gratuita — Templates Excel/Google Sheets (vendedor PF no Brasil → consumidores nos EUA, em USD)

Data da pesquisa: 2026-11-11. Orçamento: US$ 0.

## 0. Método e limitação importante (leia primeiro)

- Nesta sessão, o **WebFetch foi bloqueado pela rede** (payhip.com, gumroad.com, docs.github.com e vercel.com retornaram `ENOTFOUND`, fora da allowlist da sessão). Por isso, **nenhuma página foi lida na íntegra**.
- **Todos os fatos abaixo vêm de snippets/resumos do WebSearch** (verificado 2026-11-11). Cada item indica a URL que apareceu nos resultados. Onde o snippet era de fonte oficial, isso é dito; onde era de terceiros, também.
- "não confirmado" = não encontrei a informação em fonte oficial nem em snippet confiável.
- **Antes de lançar, o dono deve abrir as URLs oficiais listadas e reconfirmar as tarifas** (especialmente PayPal Brasil e Stripe Brasil). Nenhuma tarifa aqui foi inventada; onde há conflito entre fontes, ele está registrado.

Legenda de evidência:
- **[snippet oficial]** = trecho de página do próprio fornecedor, visto via WebSearch (verificado 2026-11-11).
- **[snippet terceiro]** = trecho de blog/review/calculadora de terceiros (verificado 2026-11-11). Menor confiança.

---

## 1. Payhip (plano Free)

| Item | Resultado | Fonte / evidência |
|---|---|---|
| Mensalidade | US$ 0 ("Free Forever"). Plus US$ 29/mês (taxa 2%); Pro US$ 99/mês (taxa 0%). | https://help.payhip.com/article/102-payhip-pricing-plans [snippet oficial] |
| Taxa de transação no Free | **5% por venda** (taxa do Payhip), além das taxas do processador | mesmo artigo [snippet oficial] |
| Recursos no Free | Payhip afirma que todos os recursos estão em todos os planos (produtos e receita ilimitados) | https://help.payhip.com/article/235-nfaa-x-payhip-help-center [snippet oficial] |
| Processadores | PayPal e Stripe (também Mercado Pago e outros gateways regionais). Basta conectar ao menos um. | https://help.payhip.com/article/64-how-do-i-sell-physical-products (Connect Your PayPal), https://help.payhip.com/article/65-connecting-your-stripe-account, https://help.payhip.com/article/343-connecting-your-mercado-pago-account [snippet oficial] |
| Brasil suportado? | **Brasil aparece na lista** de países do PayPal ("over 200 countries including … Brazil …") e do Stripe ("over 40 countries including … Brazil") nas páginas de ajuda do Payhip | mesmas URLs acima [snippet oficial] |
| Checkout em USD | Moeda padrão da loja é **USD**; alterável em Account Settings > Payment Details. Uma moeda por loja. | https://help.payhip.com/article/234-store-language-and-currency [snippet oficial] |
| Entrega digital automática | Sim — comprador recebe e-mail com link para a página de download | https://help.payhip.com/article/132-how-payhip-works [snippet oficial] |
| Limite de arquivo / armazenamento | 5 GB por arquivo; página de marketing diz sem limite de armazenamento/banda | https://help.payhip.com/article/59-adding-a-digital-product, https://payhip.com/ejunkie-alternative [snippet oficial] |
| Limite de downloads | Padrão de **3 tentativas de download** por arquivo (ajustável segundo guia de terceiro). Expiração de link: **não confirmado** | https://payhip.com/sell-digital-assets [snippet oficial]; https://www.bitdoze.com/md/sell-digital-products-payhip.md [snippet terceiro] |
| Reembolsos | Comprador contata o dono da loja; decisão é do vendedor. Payhip recomenda publicar política de reembolso e termos para se proteger de chargebacks | https://help.payhip.com/article/281-refund-request, https://help.payhip.com/article/287-protect-yourself-against-chargebacks [snippet oficial] |
| Repasse (payout) | Dinheiro vai para a conta PayPal/Stripe conectada; prazo segue o processador (Stripe 2–7 dias rolling; PayPal ~imediato — terceiro, não confirmado oficialmente) | https://learnwithhasan.com/payment-gateways/payhip/ [snippet terceiro] |
| IVA UE/UK | Payhip **cuida** do VAT digital UE/UK (calcula, cobra e recolhe trimestralmente) | https://payhip.com/eu-vat, https://help.payhip.com/article/127-digital-eu-vat [snippet oficial] |
| Sales tax EUA | "From July 1st 2026 we are now handling sales tax in the US on your behalf" — Payhip responsável por cobrar e recolher, sem custo extra | https://help.payhip.com/article/389-sales-tax-in-us-and-canada-faq [snippet oficial] |
| Itens proibidos | PLR/MRR, esquemas de enriquecimento rápido, pornografia, violação de direitos autorais, file-sharing, jogos de azar, cartões virtuais etc.; também é preciso cumprir termos do PayPal e Stripe. Violação = conta excluída sem aviso | https://help.payhip.com/article/205-what-products-are-not-allowed-on-payhip [snippet oficial] |
| Páginas personalizadas (privacidade, termos, reembolso) | Sim — help center descreve criação de páginas customizadas para termos e política de reembolso | https://help.payhip.com/article/287-protect-yourself-against-chargebacks [snippet oficial] |
| Cupons | Sim (códigos únicos em massa, limite de uso, gasto mínimo) | https://help.payhip.com/article/386-changelog [snippet oficial] |
| Programa de afiliados | Sim (vendedor pode criar o próprio) | https://payhip.com/sellfy-alternative [snippet oficial] |
| E-mail aos compradores | E-mail de suporte exibido no recibo; tópicos de "Email Updates" e consentimento. Ferramenta de e-mail marketing: fontes de terceiros divergem → **não confirmado** | https://help.payhip.com/category/42-customers [snippet oficial] |

**Atenção:** a política de "templates" de terceiros/PLR é proibida — os templates precisam ser de autoria própria.

---

## 2. Gumroad

| Item | Resultado | Fonte |
|---|---|---|
| Taxa venda direta | **10% + US$ 0,50** por transação | https://gumroad.com/pricing (conforme snippets); https://checkoutpage.com/blog/gumroad-fees [snippet terceiro] |
| Processamento de cartão | **Conflito**: página de preços diz 10% + 50¢; segundo resumo de busca, o help center diz que isso **exclui** 2,9% + 30¢ de processamento | resumo de busca citando gumroad.com/pricing e help center [snippet terceiro/agregado] |
| Discover (marketplace) | **30%** sobre vendas via Discover | https://dodopayments.com/blogs/gumroad-fees-explained [snippet terceiro] |
| Merchant of Record | "Gumroad now acts as the Merchant of Record for all sales … handle all sales tax collection and remittance worldwide"; configurações de tax desativadas a partir de 1/jan/2025. Página de preços qualifica: "only in regions where we have tax obligations" | https://gumroad.com/help/article/121-sales-tax-on-gumroad, https://gumroad.com/taxes, https://gumroad.com/pricing [snippet oficial] |
| Payout para Brasil | Gumroad paga por **depósito bancário local** na maioria dos países e por **PayPal** onde não há banco. **PayPal Connect não está disponível para o Brasil** ("except Algeria, Brazil, Egypt, India …"). Se Brasil tem payout bancário: **não confirmado** | https://gumroad.com/help/article/13-getting-paid, https://gumroad.com/help/article/275-paypal-connect [snippet oficial] |
| Taxa de payout PayPal | Um terceiro cita 2% — **não confirmado** oficialmente | https://wise.com/us/blog/gumroad-fees [snippet terceiro] |
| Payout mínimo | **Conflito / não confirmado** ($10 no código aberto; outras fontes citam $100) | https://mintlify.com/antiwork/gumroad/payments/payouts [snippet terceiro] |
| Calendário | Pagamentos às sextas, incluindo vendas até a sexta anterior; **retenção mínima de 7 dias** | https://gumroad.com/help/article/13-getting-paid, https://gumroad.com/help/article/281-payout-delays [snippet oficial] |

---

## 3. Alternativas (resumo)

| Plataforma | Custo fixo | Taxa | Observação para vendedor PF no Brasil | Fonte |
|---|---|---|---|---|
| **Lemon Squeezy** | US$ 0 | 5% + 50¢ (com possíveis adicionais: +1,5% cartão internacional, +1,5% PayPal — terceiro) | MoR. Payouts por banco/PayPal 2x/mês; ">110 países para payouts" — **Brasil não confirmado**. Terceiro relata migração de merchants para Stripe Managed Payments em 2026 | https://www.lemonsqueezy.com/paddle-alternative [snippet oficial]; https://dodopayments.com/blogs/lemonsqueezy-review, https://learnwithhasan.com/payment-gateways/country/brazil/ [snippet terceiro] |
| **Etsy** | **US$ 0,20 por anúncio** (vale 4 meses) → **viola orçamento US$ 0**. Taxa de abertura de loja (US$ 15–29) é relatada por alguns terceiros e negada por outros → não confirmado | — | Elegibilidade do Brasil: **não confirmada** | https://help.etsy.com/hc/en-us/articles/360035902374-Etsy-Fee-Basics, https://craftybase.com/blog/the-complete-guide-to-etsy-fees [snippets] |
| **Ko-fi** | US$ 0 (Gold ~US$ 12/mês) | **5%** sobre vendas da loja no plano grátis + processador | Usa PayPal/Stripe do criador | https://help.ko-fi.com/hc/en-us/articles/360002506494-Does-Ko-fi-Take-a-Fee [snippet oficial]; schoolmaker.com [terceiro] |
| **Polar.sh** | US$ 0 | Conflito: 4% + 40¢ (antigo) vs 5% + 50¢ (2026, terceiros) + possíveis adicionais | MoR; payouts via Stripe Connect Express — **Brasil não confirmado** | https://polar.sh/docs/fees, https://polar.sh/blog/introducing-polar-plans [snippet oficial]; dodopayments.com [terceiro] |
| **Sellfy** | **Pago**: Starter ~US$ 29/mês (mensal) ou ~US$ 22/mês (anual); sem plano grátis, trial 14 dias | 0% | Fora do orçamento | https://sellfy.com/pricing.md [snippet oficial] |
| **Stan Store** | Pago (preço **não confirmado** nesta pesquisa) | — | Fora do orçamento | — |
| **Shopify** | **Pago**: Basic ~US$ 39/mês (mensal) / ~US$ 29/mês (anual) | — | Fora do orçamento | https://www.nerdwallet.com/article/small-business/shopify-pricing [snippet terceiro] |

---

## 4. PayPal e Stripe para pessoa física no Brasil

### PayPal Brasil
- **Tarifa de venda (transações comerciais) doméstica: 4,79% + tarifa fixa**; para recebimentos internacionais, soma-se **+1,61%** → **~6,40% + tarifa fixa**. Página oficial com "Última atualização: 16 de julho de 2025". Tarifa fixa em USD = **US$ 0,30** segundo fontes secundárias (o trecho oficial foi cortado antes da linha do dólar). Fonte: https://www.paypal.com/br/webapps/mpp/merchant-fees [snippet oficial]; https://tecnoblog.net/responde/como-funciona-o-paypal/ [snippet terceiro] — verificado 2026-11-11.
- **Conversão de moeda:** margem de **3,50%** acima da taxa de câmbio base para pagamentos recebidos em outra moeda (4,50% para demais conversões). Fonte: https://paypal.com/br/webapps/mpp/paypal-fees [snippet oficial] — verificado 2026-11-11.
- **Saque para banco brasileiro:** sem tarifa no modo padrão, até 3 dias úteis; conta bancária com mesmo CPF/CNPJ; Pix não disponível para saque. Fonte: https://www.paypal.com/br/cshelp/article/como-fazer-para-transferir-saldo-da-minha-conta-do-paypal-help394 [snippet oficial]; https://wise.com/br/blog/transferir-dinheiro-paypal-banco-do-brasil [snippet terceiro].
- **Conta pessoal vs. empresarial:** diferença de tarifa entre os tipos para recebimento internacional — **não confirmado**. O Payhip diz que vendedores fora dos países listados precisam de conta Business (Brasil está listado).

### Stripe Brasil
- **Conta pessoa física com CPF é possível**: "o CNPJ é opcional para o formulário de conta de pessoa física"; CPF obrigatório e residente no país; conta bancária no Brasil em **BRL** com o mesmo CPF/CNPJ. Fonte: https://support.stripe.com/questions/brazil-specific-information-to-open-a-stripe-account [snippet oficial] — verificado 2026-11-11.
- **Cobrar em USD e liquidar em BRL:** Stripe converte para a moeda de liquidação quando diferem (https://docs.stripe.com/currencies/conversions [snippet oficial]); **tarifa de conversão para conta BR: não confirmada**.
- **Tarifa de cartão:** só terceiros: 3,99% + R$ 0,39 (nacional) + 2% (cartão internacional) — **não confirmado oficialmente** (https://launchmystore.io/br/tools/stripe-fee-calculator [snippet terceiro]).

### Tributos (apenas temas para o contador — sem conclusões legais)
Levar ao contador: **IOF** sobre câmbio na conversão USD→BRL; **Carnê-Leão** (rendimentos recebidos do exterior por PF); enquadramento como **exportação de serviços/produtos digitais**; viabilidade de **MEI** (atividade permitida?) vs. permanecer PF; obrigações acessórias. **Consulte um contador.**

---

## 5. Sales tax dos EUA sobre produtos digitais

| Plataforma | Quem cobra/recolhe | Fonte |
|---|---|---|
| Payhip | Desde 1/jul/2026, **Payhip** cobra e recolhe sales tax dos EUA em nome do vendedor (sem custo extra). Também cuida de VAT UE/UK. (Artigo antigo dizia que não recolhia fora da UE — o artigo de 2026 é o mais recente.) | https://help.payhip.com/article/389-sales-tax-in-us-and-canada-faq, https://help.payhip.com/article/174-taxes-for-digital-products [snippet oficial] |
| Gumroad | **Gumroad é Merchant of Record** e cobra/recolhe sales tax ("only in regions where we have tax obligations", segundo página de preços) | https://gumroad.com/help/article/121-sales-tax-on-gumroad, https://gumroad.com/pricing [snippet oficial] |

Se o imposto é somado ao preço ou embutido: **não confirmado** — nos cálculos abaixo, assume-se imposto cobrado à parte do comprador (não afeta o líquido).

---

## 6. Hospedagem gratuita da landing page (uso comercial)

| Serviço | Uso comercial? | Limites | Fonte |
|---|---|---|---|
| GitHub Pages | **Arriscado/proibido**: "not intended for or allowed to be used as a free web hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS)". Também não usar para senhas/cartões. | Limites de tamanho/banda: não lidos (página bloqueada) → não confirmado | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits [snippet oficial] |
| Cloudflare Pages (Free) | Permitido segundo agregadores; **texto dos termos da Cloudflare não confirmado** | 500 builds/mês, 1 build simultâneo [oficial]; banda ilimitada [terceiros] | https://developers.cloudflare.com/pages/platform/limits [snippet oficial]; https://hostfleet.pages.dev/cf-pages-vs-vercel-vs-netlify-2026/ [terceiro] |
| Netlify (Free) | Permitido segundo terceiros (não confirmado em página oficial) | 300 créditos/mês com limite rígido; deploy de produção ~15 créditos (terceiro) | https://netli.fyi/blog/netlify-free-plan-limits-2026 [snippet terceiro] |
| Vercel Hobby | **Não permitido**: "Hobby teams are restricted to non-commercial personal use only" | — | https://vercel.com/docs/limits/fair-use-guidelines, https://vercel.com/terms [snippet oficial] |

**Recomendação:** **Cloudflare Pages** (subdomínio grátis `*.pages.dev`), com a ressalva de reconfirmar os termos. Alternativa de risco zero: usar a **própria loja Payhip** (com páginas customizadas) como landing page, sem hospedagem externa. Evitar GitHub Pages e Vercel Hobby para página de vendas.

---

## 7. Analytics gratuito

| Ferramenta | Grátis? | Cookies | Observação | Fonte |
|---|---|---|---|---|
| Cloudflare Web Analytics | Sim ("privacy-first … no cost") | Divulgado como sem cookies; review técnica de 2020 contestou (pode estar desatualizada) | Básico: pageviews, páginas, referrers; ~6 meses de histórico (terceiro) | https://cloudflare.com/web-analytics [snippet oficial]; https://www.ctrl.blog/entry/review-cloudflare-analytics/ [terceiro] |
| GoatCounter | Grátis **apenas para uso não comercial** no hospedado; comercial pago (valores conflitantes: US$ 5 a 15/mês) ou self-host | Sem cookies (geral) | Uso comercial hospedado ≠ US$ 0 | https://goatcounter.com/ e agregadores [snippet] |
| Google Analytics 4 | Grátis (conhecimento geral; não verificado nesta pesquisa) | Usa cookies → exige considerações de consentimento (banner) | Mais complexo | não verificado nesta sessão |

**Recomendação:** **Cloudflare Web Analytics** (combina com Cloudflare Pages). As estatísticas de vendas ficam no painel do Payhip.

---

## 8. E-mail de suporte gratuito

- **Gmail grátis** (ex.: um endereço dedicado à marca) — custo US$ 0; sem domínio próprio.
- **Zoho Mail Forever Free**: até 5 usuários, 1 domínio próprio, 5 GB/usuário, só web/mobile (sem IMAP/POP), disponibilidade regional variável — **exige domínio próprio = custo** → fora do orçamento por ora. Fonte: https://www.zoho.com/mail/zohomail-pricing.html [snippet oficial/terceiros].
- **Payhip**: e-mail de suporte do vendedor exibido no recibo do comprador (https://help.payhip.com/category/42-customers [snippet oficial]).

**Recomendação:** Gmail dedicado + configurá-lo como e-mail de suporte no Payhip.

---

## 9. Tabela comparativa

| Critério | Payhip Free | Gumroad | Lemon Squeezy | Ko-fi Free | Etsy |
|---|---|---|---|---|---|
| Custo fixo | US$ 0 | US$ 0 | US$ 0 | US$ 0 | US$ 0,20/anúncio ✗ |
| Taxa da plataforma | 5% | 10% + 50¢ (30% Discover) | 5% + 50¢ (+adicionais) | 5% | não pesquisado em detalhe |
| Processador | PayPal/Stripe do próprio vendedor | Gumroad processa | LS processa (MoR) | PayPal/Stripe do vendedor | Etsy Payments |
| Brasil confirmado | Sim (lista PayPal e Stripe do Payhip) | Payout para BR **incerto**; PayPal Connect excluído para BR | **Não confirmado** | provável (via PayPal), não verificado | não confirmado |
| Retenção/payout | Direto ao processador | 7 dias + sextas; mínimo incerto | 2x/mês | direto | — |
| Sales tax EUA | Payhip (desde jul/2026) | Gumroad (MoR) | LS (MoR) | não confirmado | Etsy (marketplace) — não verificado |
| VAT UE/UK | Payhip | Gumroad | LS | não confirmado | — |
| Páginas de política, cupons, afiliados | Sim | Parcial (não pesquisado) | — | — | — |

---

## 10. Recomendação final: **Payhip (plano Free) + PayPal Brasil** (Stripe Brasil como segundo processador, após confirmar tarifas)

Motivos baseados em evidência:
1. **US$ 0 fixo** e **5%** por venda (metade da taxa percentual do Gumroad).
2. **Brasil está explicitamente listado** nas páginas de PayPal e Stripe do Payhip — único caminho com suporte ao Brasil confirmado em fonte oficial. No Gumroad, PayPal Connect exclui o Brasil e o payout bancário para BR não foi confirmado.
3. Dinheiro vai **direto** para o PayPal/Stripe do vendedor (sem retenção de 7 dias nem payout mínimo da plataforma).
4. Payhip cuida de **VAT UE/UK** e, desde 1/jul/2026, de **sales tax dos EUA**.
5. Free inclui páginas customizadas (privacidade, termos, reembolso), cupons, afiliados, entrega automática, checkout em USD.

Observação honesta: no cenário "Gumroad sem taxa de cartão adicional", o líquido do Gumroad em US$ 19/29 fica alguns centavos acima do Payhip+PayPal (ver tabela). A escolha pelo Payhip se deve à **viabilidade de recebimento no Brasil** e ao controle do dinheiro, não só ao valor por venda.

---

## 11. Cálculo do líquido por venda (USD)

### Premissas
- Comprador nos EUA paga em USD com cartão/PayPal; impostos (sales tax) cobrados à parte pela plataforma, fora do cálculo.
- **Payhip + PayPal Brasil:** Payhip 5% (oficial); PayPal BR internacional **6,40% + US$ 0,30** (4,79% + 1,61% oficial; US$ 0,30 de fonte secundária). Taxas percentuais calculadas sobre o preço bruto.
- **Gumroad G1:** 10% + US$ 0,50 apenas. **Gumroad G2:** 10% + US$ 0,50 + 2,9% + US$ 0,30 (cenário do help center citado). **Não inclui** a possível taxa de 2% de payout PayPal (não confirmada) nem tarifas de recebimento no PayPal BR do payout (não confirmadas).
- **Conversão USD→BRL:** margem PayPal de **3,50%** (oficial) aplicada ao líquido em USD na coluna "após conversão". Exclui IOF e tributos (consultar contador).
- Stripe Brasil: tarifas oficiais **não confirmadas** → não calculado.

| Preço | Payhip+PayPal (USD) | Payhip+PayPal após conversão 3,5% | Gumroad G1 (USD) | G1 após conv. | Gumroad G2 (USD) | G2 após conv. |
|---|---|---|---|---|---|---|
| US$ 9 | 9 − 0,45 − 0,876 = **7,67** | **7,41** | 9 − 0,90 − 0,50 = **7,60** | 7,33 | 7,60 − 0,561 = **7,04** | 6,79 |
| US$ 19 | 19 − 0,95 − 1,516 = **16,53** | **15,96** | **16,60** | 16,02 | **15,75** | 15,20 |
| US$ 29 | 29 − 1,45 − 2,156 = **25,39** | **24,51** | **25,60** | 24,70 | **24,46** | 23,60 |

Custo total efetivo Payhip+PayPal (antes da conversão): 14,7% (US$ 9), 13,0% (US$ 19), 12,4% (US$ 29).

---

## 12. Passos humanos (o dono precisa fazer)

1. **PayPal Brasil**: criar/usar conta (avaliar Pessoal vs Empresarial; Payhip exige Business só fora dos países listados), confirmar CPF, vincular conta bancária com o **mesmo CPF**, verificar a tabela atual em https://www.paypal.com/br/webapps/mpp/merchant-fees (linha do USD fixo).
2. (Opcional) **Stripe Brasil**: abrir conta PF com CPF, conta bancária BRL no mesmo CPF, completar KYC; conferir no painel a tarifa de cartão internacional e de conversão.
3. **Payhip**: criar conta Free, conectar PayPal (e/ou Stripe), confirmar moeda USD em Account Settings > Payment Details.
4. Criar no Payhip as páginas de **Privacy Policy, Terms, Refund Policy**; definir e-mail de suporte.
5. Fazer upload dos templates (autoria própria; nada de PLR/MRR), revisar limite de downloads.
6. Fazer **compra-teste** (cupom 100% ou valor mínimo) para validar entrega e repasse; reembolsar.
7. Criar conta **Cloudflare** → Pages (landing) + Web Analytics.
8. Criar Gmail dedicado ao suporte.
9. **Consultar contador** sobre IOF, Carnê-Leão, exportação de serviços, MEI vs PF.
10. Reabrir todas as URLs oficiais deste documento e reconfirmar valores (pesquisa feita só via snippets).

---

## 13. Limites e riscos

- **Evidência apenas por snippets** (WebFetch bloqueado). Reconfirmar tudo antes de precificar.
- **Tarifa fixa US$ 0,30 do PayPal BR** e tarifas do **Stripe BR** não confirmadas em página oficial completa.
- PayPal pode reter/limitar contas novas; risco de disputas/chargebacks (produto digital) — política de reembolso clara é essencial.
- Payhip pode excluir conta sem aviso por violação (PLR/MRR, direitos autorais).
- Sales tax EUA no Payhip é recurso novo (jul/2026); artigos antigos conflitam.
- Cloudflare Pages: permissão de uso comercial confirmada só por terceiros. GitHub Pages proíbe sites "primarily directed at facilitating commercial transactions"; Vercel Hobby proíbe uso comercial.
- Sem domínio próprio (custo), a marca fica em subdomínios (`payhip.com/...`, `*.pages.dev`) e e-mail Gmail.
- Câmbio e IOF reduzem o líquido em BRL; obrigações fiscais brasileiras são responsabilidade do vendedor — consultar contador.
