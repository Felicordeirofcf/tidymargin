# TidyMargin — Global AI Commerce

Empresa digital, com investimento inicial de US$ 0, que vende a consumidores dos EUA o **TidyMargin Cleaning Business Profit Kit**: planilhas (Excel e Google Sheets) para donos de empresas de limpeza calcularem preços com lucro e controlarem clientes, agenda, faturas e resultado.

> Projeto isolado nesta pasta. Nenhum arquivo da loja Samba Vest foi alterado.

## Comece por aqui
1. **Relatório final e pendências:** [docs/15_FINAL_DELIVERY_REPORT.md](docs/15_FINAL_DELIVERY_REPORT.md)
2. **O que você precisa fazer para lançar:** [docs/12_LAUNCH_CHECKLIST.md](docs/12_LAUNCH_CHECKLIST.md) e [docs/07_STORE_SETUP.md](docs/07_STORE_SETUP.md)
3. **Arquivos para subir na Payhip:** `products/release/` (ZIPs), `brand/covers/` (capas), `store/PAYHIP_LISTINGS.md` (textos)
4. **Site pronto:** `website/dist/` → [deployment/DEPLOY.md](deployment/DEPLOY.md)
5. **Marketing:** [marketing/CONTENT_CALENDAR_30_DAYS.md](marketing/CONTENT_CALENDAR_30_DAYS.md) + `brand/social/`

## Relatórios
- [01 Pesquisa de mercado](docs/01_MARKET_RESEARCH.md)
- [02 Estratégia](docs/02_BUSINESS_STRATEGY.md)
- [03 Marca](docs/03_BRAND_IDENTITY.md)
- [04 Produto](docs/04_PRODUCT_SPECIFICATION.md)
- [05 Arquitetura](docs/05_TECHNICAL_ARCHITECTURE.md)
- [06 Testes](docs/06_PRODUCT_TESTS.md)
- [07 Loja](docs/07_STORE_SETUP.md)
- [08 Pagamentos](docs/08_PAYMENT_CONFIGURATION.md)
- [09 Marketing](docs/09_MARKETING_PLAN.md)
- [10 Automação](docs/10_AUTOMATION_ARCHITECTURE.md)
- [11 Financeiro](docs/11_FINANCIAL_MODEL.md)
- [12 Checklist](docs/12_LAUNCH_CHECKLIST.md)
- [13 Operações](docs/13_OPERATIONS_MANUAL.md)
- [14 Roadmap](docs/14_GROWTH_ROADMAP.md)
- [15 Entrega final](docs/15_FINAL_DELIVERY_REPORT.md)

Pesquisa detalhada com fontes: [docs/market-research/](docs/market-research/). Outros documentos: [COSTS.md](COSTS.md), [SECURITY.md](SECURITY.md).

## Comandos
```bash
./build_all.sh                       # reconstrói planilhas, imagens, PDFs, ZIPs, site + roda 39 testes + teste do site
python3 agents/run_agents.py         # roda os agentes (CEO) e gera analytics/dashboard.html
python3 kit/build_site.py            # regenera o site após editar deployment/store_config.json
```
