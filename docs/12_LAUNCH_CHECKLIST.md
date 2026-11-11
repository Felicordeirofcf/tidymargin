# 12 — Checklist de lançamento

Legenda: ✅ concluído e testado · 🟡 implementado, não testado · 🔒 pendente da sua ação ou autorização · ⛔ bloqueado por terceiros

## Produto
- ✅ 3 tiers + exemplo + ferramenta grátis (`products/`)
- ✅ Fórmulas testadas: 39 testes, recálculo real, zero erros
- ✅ PDFs (User Guide, Pricing Playbook) e ZIPs de release
- 🟡 Abrir no Excel real e no Google Sheets real: faça você no 1º dia (10 min). Suba o `Complete-EXAMPLE.xlsx` no Google Drive e confira as abas Price Calculator e Monthly Summary.

## Marca
- ✅ Nome, logo, paleta, capas, pins e thumbnails
- 🔒 Busca de marca no USPTO e no INPI antes de investir (opcional, grátis)

## Contas (você, cerca de 1 a 2 h)
- 🔒 Gmail da marca + 2FA
- 🔒 Stripe pessoa física (CPF), nome público "TidyMargin", banco no mesmo CPF + 2FA (o PayPal Empresarial exige CNPJ)
- ⛔ Verificação da Stripe (KYC)
- 🔒 Payhip Free + conectar Stripe + moeda USD + 2FA
- 🔒 Cloudflare (Pages + Web Analytics) + 2FA

## Loja
- 🔒 Criar os 4 produtos, subir os ZIPs, capas e capturas, colar os textos (`store/PAYHIP_LISTINGS.md`)
- 🔒 Colar as políticas (privacidade, termos, reembolso) e o e-mail de suporte
- 🔒 Teste: baixar o produto grátis com outro e-mail
- 🔒 Teste opcional de checkout pago (cupom 100% ou compra de US$ 9 + reembolso), **só com a sua autorização**
- 🔒 Copiar os links para `deployment/store_config.json` e rodar `python3 kit/build_site.py`

## Site
- ✅ Site gerado e testado (desktop e mobile, links, imagens, acessibilidade básica)
- 🔒 Publicar no Cloudflare Pages (`deployment/DEPLOY.md`) e preencher `site_url`
- 🔒 Ativar o Web Analytics e colar o token

## Marketing
- ✅ Calendário de 30 dias, 3 artigos, imagens
- 🔒 Criar o Pinterest Business e o canal do YouTube com o Gmail da marca (sem rosto)
- 🔒 Publicar o dia 1

## Operação
- ✅ Agentes, painel, modelos de resposta, procedimentos de erro
- 🔒 Definir `tax_reserve_pct` com um contador

## Estados atuais
| Estado | Status |
|---|---|
| Produto pronto | ✅ |
| Loja pronta para configuração | ✅ |
| Loja publicada | 🔒 |
| Pagamentos habilitados | ⛔/🔒 |
| Loja apta a receber pedidos | 🔒 |
| Primeira venda concluída | ❌ nenhuma venda registrada |
