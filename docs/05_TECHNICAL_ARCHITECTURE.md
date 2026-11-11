# 05 — Arquitetura técnica

```
global-ai-commerce/
├── kit/                     # código-fonte dos produtos
│   ├── pricing.py           # motor de cálculo (fonte da verdade, testado)
│   ├── build_workbooks.py   # gera os .xlsx (openpyxl) — 3 tiers + exemplo + grátis
│   ├── sample_data.py       # dados fictícios dos arquivos EXAMPLE
│   ├── brand.py             # nome, cores, versão
│   ├── render_previews.py   # capturas de tela reais (LibreOffice → PDF → PNG)
│   ├── make_brand_assets.py # HTML das capas/pins → brand/render.cjs (Chromium)
│   ├── make_guides.py       # PDFs (reportlab) + ZIPs de release
│   └── build_site.py        # site estático → website/dist
├── products/{starter,complete,premium,free}/  # planilhas
├── products/guides/         # fontes .md + PDFs
├── products/release/        # ZIPs para upload na Payhip
├── brand/                   # logo, capas, social, screenshots
├── website/content/*.md     # artigos; website/dist = site pronto
├── marketing/               # calendário de 30 dias (py → csv/md)
├── store/PAYHIP_LISTINGS.md # textos dos produtos
├── agents/                  # 8 agentes + painel
├── analytics/               # dados de entrada (git-ignored) + dashboard.html
├── deployment/              # store_config.json, guias de deploy
├── tests/                   # 39 testes (unittest) + site_check.cjs
├── reports/                 # relatórios dos agentes
└── build_all.sh             # reconstrói tudo e roda os testes
```

## Decisões
| Decisão | Motivo |
|---|---|
| Venda e entrega pela **Payhip** (nativo) | US$ 0/mês, entrega automática, impostos de venda tratados pela plataforma, aceita vendedor do Brasil via PayPal/Stripe. Não construímos um checkout próprio, para evitar custo e risco. |
| Site **estático** (HTML/CSS, sem JS) | Grátis em qualquer host, rápido, seguro e sem dependências. O botão de compra leva ao checkout da Payhip. |
| Hospedagem recomendada: **Cloudflare Pages** (free) | O plano free permite uso comercial (fonte de terceiros, a confirmar). O GitHub Pages proíbe sites de vendas e o Vercel Hobby é não comercial. Ver `deployment/DEPLOY.md`. |
| Analytics: **Cloudflare Web Analytics** | Grátis e sem cookies, então dispensa banner de cookies. Só carrega se houver token. |
| Planilhas geradas por **código** | Reprodutível, testável, versionável. Uma mudança de fórmula vira um diff. |
| Agentes **sob demanda** (CLI) | Custo zero, sem servidor e sem autonomia irrestrita. |
| Banco de dados: **nenhum** | Por enquanto não há necessidade. Os dados de vendas vêm do export da Payhip. O Supabase só se justifica com volume real. |

## Por que fica dentro deste repositório
O repositório disponível é o da loja Samba Vest. O projeto novo foi isolado em `global-ai-commerce/`, sem alterar nenhum arquivo da Samba Vest:
- Os scripts são Python/CJS. Não há arquivos `.ts`, que entrariam no `tsconfig` do Next.
- O site é HTML puro, fora do build do Next.

**Recomendação:** mover para um repositório próprio quando quiser. Basta copiar a pasta.

## Dependências
Todas gratuitas e de código aberto:
- Python 3.11 ou superior;
- openpyxl, reportlab, pypdfium2 e Pillow;
- LibreOffice, para os testes e as capturas de tela;
- Node 18 ou superior, com Playwright e Chromium, para as imagens e o teste do site.

Para reconstruir tudo: `./build_all.sh`.
