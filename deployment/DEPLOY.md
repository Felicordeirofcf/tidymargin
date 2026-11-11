# Publicar o site de graça (Cloudflare Pages)

Por que Cloudflare Pages:
- **Vercel Hobby:** só para uso não comercial (verificado em trecho de busca).
- **GitHub Pages:** a política diz que não é para sites cujo objetivo principal é vender ou transações comerciais.
- **Cloudflare Pages Free:** permite uso comercial (fonte de terceiros). Confirme nos termos ao criar a conta.

## Opção A: upload direto, sem Git (a mais simples)
1. Crie uma conta grátis em dash.cloudflare.com com o Gmail da marca e ative a 2FA.
2. Vá em Workers & Pages > Create > Pages > **Upload assets**.
3. Dê o nome do projeto: `tidymargin` (o endereço fica `https://tidymargin.pages.dev`, se estiver livre).
4. Arraste a **pasta** `global-ai-commerce/website/dist/` e clique em Deploy.
5. Copie a URL para `site_url` em `deployment/store_config.json`, rode `python3 kit/build_site.py` (gera o sitemap e o canonical) e envie a pasta de novo.

## Web Analytics (grátis, sem cookies)
Cloudflare > Analytics & Logs > Web Analytics > Add a site → copie o **token** (é público, não é segredo) para `cloudflare_analytics_token` → rode o build e envie de novo.

## Atualizações
Sempre: `./build_all.sh` (testes) → upload da pasta `website/dist/`.

## Limites do plano grátis
Para este site, que é pequeno e estático, os limites do plano gratuito (número de builds e de arquivos) sobram. Não há cobrança automática no plano Free. **Não cadastre cartão.**
