# Segurança e privacidade

## Implementado
- **Nenhuma credencial no repositório.** `store_config.json` só tem links públicos. O token do Cloudflare Analytics é público por natureza. `.gitignore` exclui os dados de clientes, os logs e os rascunhos.
- **Planilhas sem macros**, sem scripts e sem links externos (testado).
- **Site estático, sem JavaScript próprio, sem formulários e sem cookies**, o que reduz muito a superfície de ataque (sem injeção nem XSS de entrada). Todo texto dinâmico é escapado no build (`html.escape`).
- **Pagamentos 100% na Payhip e no PayPal.** Nunca tocamos em dados de cartão.
- **Agentes com permissões mínimas, limites e logs mascarados.** Ações críticas são bloqueadas no código.
- **Validação de entradas** nas planilhas (números ≥ 0, faixas de percentuais, listas) e nos agentes (`money()` rejeita valores inválidos).
- **Dependências:** só bibliotecas mantidas e open source. Sem dependências npm no projeto (o Playwright é usado só localmente).
- **Acessibilidade básica:** `alt` em todas as imagens, contraste da paleta, link "skip to content", HTML semântico, layout responsivo (testado).
- **Direitos autorais:** todo o texto, as fórmulas, o logo e as imagens foram criados para este projeto. A fonte Inter é OFL. Não há conteúdo copiado de concorrentes.

## Para você fazer
- Ative a 2FA em Gmail, PayPal, Payhip e Cloudflare.
- Use senhas únicas, num gerenciador grátis (Bitwarden).
- Nunca cole senha, CPF ou documentos em arquivos do projeto ou no chat.

## Conformidade (sem declaração de conformidade absoluta)
- As políticas de privacidade, termos e reembolso foram escritas para o modelo de negócio, citando direitos de CCPA e estados dos EUA, GDPR/UK e LGPD. **Não foram revisadas por um advogado.** Recomenda-se uma revisão quando houver receita.
- **Formalização no Brasil (MEI, Carnê-Leão etc.):** é decisão do dono, com um contador. Nenhuma empresa foi aberta e nenhum dado de empresa foi inventado.
- **Não usamos endereço americano fictício.** A política informa que o vendedor fica no Brasil, sem expor o nome do dono.
