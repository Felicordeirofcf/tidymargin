# 09 — Plano de marketing orgânico (US$ 0)

## Princípios
- **Faceless:** o dono não aparece. Vídeos são gravações de tela do arquivo EXAMPLE com texto na tela. Os pins e artigos usam imagens reais do produto.
- Conteúdo útil primeiro, produto quando fizer sentido.
- Nada de spam, compra de seguidores ou avaliações, depoimentos inventados ou promessa de renda. Isso é verificado pelo agente `content_marketing`.
- Não publicar em comunidades que proíbem divulgação. No Reddit (r/CleaningBusiness) e em grupos, só respostas genuínas, sem link, a menos que a regra do grupo permita.

## Canais escolhidos (2 principais + 1 secundário)
| Canal | Papel | Por quê |
|---|---|---|
| **Pinterest** (principal) | Tráfego perene para artigos e para a ferramenta grátis | Pins duram meses, o público busca "templates" e "pricing", e não exige rosto |
| **YouTube Shorts + vídeos longos** (principal) | Demonstração real do produto | Não foi achado um tutorial dominante de planilha de preço para limpeza (pesquisa). A gravação de tela mostra o produto funcionando e gera confiança. |
| **SEO no site próprio** (secundário) | Captar buscas de cauda longa | Os termos genéricos são dominados por SaaS. Foco em "markup vs margin cleaning", "commercial cleaning bid calculator" e similares (`market-research/KEYWORDS.md`). |
| TikTok / Instagram Reels | Opcional | Reaproveita os Shorts, se você quiser criar as contas |

## Funil
Pin, Short ou artigo → site ou página da Payhip → **Quick Price Check grátis** (captura o e-mail pela Payhip) → Starter, Complete ou Premium.

## Conteúdo produzido
- **Calendário de 30 dias** com 32 peças: título, roteiro, legenda, palavras-chave, CTA e imagem. Arquivos: `marketing/CONTENT_CALENDAR_30_DAYS.md` e `.csv`.
- **3 artigos SEO** (em `website/content/`, publicados em `website/dist/articles/`):
  - How to Price House Cleaning Jobs;
  - Markup vs Margin for Cleaning Businesses;
  - How to Bid a Commercial Cleaning Contract.
- **5 pins** (1000×1500), **3 posts de dica** (1080×1080) e **2 thumbnails** (1280×720), em `brand/social/`.
- **Textos da loja** com SEO: `store/PAYHIP_LISTINGS.md`.

## SEO técnico implementado
- Títulos e meta descriptions únicos em cada página.
- Dados estruturados válidos:
  - `Product` com `Offer` (preço e moeda), **sem avaliações falsas**;
  - `FAQPage`;
  - `Article`.
- `robots.txt`, `canonical` e `sitemap.xml`, gerados quando `site_url` for preenchido.
- HTML semântico, `alt` em todas as imagens, site mobile-first e rápido (sem JS).
- Não criamos centenas de páginas repetitivas. São 3 artigos úteis por enquanto.

## Rotina (cerca de 30 a 45 min por dia, sem aparecer)
1. Abra `marketing/CONTENT_CALENDAR_30_DAYS.md` e pegue o item do dia.
2. **Pin:** suba a imagem de `brand/social/` no Pinterest Business (grátis), com o título, a descrição e o link indicados.
3. **Short:** grave a tela do EXAMPLE seguindo o roteiro (por exemplo com o Xbox Game Bar no Windows ou o OBS, ambos grátis). Adicione o texto na tela no editor do YouTube ou no CapCut (grátis). Publique com a legenda indicada.
4. No `content_calendar.csv`, marque `status=published` e cole a URL.
5. Toda semana, copie as visitas da Cloudflare para `analytics/data/traffic.csv` e rode `python3 agents/run_agents.py`.

## Como medir (dados reais)
Visitas por origem, cliques no botão de compra, vendas confirmadas e conversão. Ver o painel `analytics/dashboard.html`. Depois de 30 dias, mantenha os 2 formatos que mais trazem cliques e corte os 2 piores.

## Marketing de afiliados
A Payhip tem programa de afiliados no plano Free. A sugestão é oferecer 30% de comissão, paga só sobre a venda (custo zero antecipado). Ative depois das primeiras vendas, convidando criadores de conteúdo de limpeza.
