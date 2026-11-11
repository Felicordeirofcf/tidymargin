# 06 — Testes do produto (TEST REPORT)

**Execução:** 2026-11-11, `./build_all.sh` → **39 testes unitários e de integração passaram** e **SITE OK** (10 páginas × 2 viewports).

## Como foi testado
1. **Matemática** (`tests/test_pricing.py`, 15 testes): margem atingida exatamente (várias margens e impostos), markup ≠ margem, arredondamento (inclusive ruído de ponto flutuante), preço mínimo, desconto composto, desconto que preserva a margem, formulário vazio = 0, entradas inválidas (negativos, equipe 0, margem + taxa ≥ 100%), relação bruta > contribuição > líquida, "check a price", ponto de equilíbrio, bid comercial e custo de equipe.
2. **Planilhas reais recalculadas** (`tests/test_workbooks.py`, 15 testes): gera os 7 arquivos, **recalcula no LibreOffice** e compara célula a célula com `pricing.py`:
   - Calculadora: os 24 resultados, no exemplo e em **6 casos-limite** (recorrente semanal + desconto extra + imposto 8,25%; horas, salário e margem manuais; job mínimo; condição com pets; margem 98% → alerta; sqft negativo → alerta).
   - Quote Table: 6 linhas.
   - Resumo mensal: receita, recebido, despesas, lucro, impostos, fluxo de caixa, visitas, comparação jun × mai.
   - Ligações entre Clients e Schedule: último atendimento, contagem, receita, próxima visita e follow-up.
   - Estimate e Invoice: subtotal, desconto, total, vencimento e saldo. O Estimate do Starter funciona sem a aba de clientes.
   - Goal Planner, Commercial Bid, Crew Cost, Dashboard e ferramenta grátis.
   - **Varredura de erros** (#REF!, #NAME?, #VALUE!, #DIV/0!, #N/A) em todas as células de todos os arquivos: **zero**.
   - **Compatibilidade:** só funções da lista portátil (Excel 2019+/Web/Sheets/LibreOffice); nenhum `vbaProject` (macro) nem `externalLink`.
   - Estrutura de abas por tier.
3. **Agentes** (`tests/test_agents.py`, 9 testes): só vendas confirmadas contam, ausência de dados = sem vendas, nenhuma ação crítica executável, e-mails mascarados em logs e relatórios, escalonamento de reembolso, checagem de alegações proibidas, QA dos ZIPs reais, CEO e painel.
4. **Site** (`tests/site_check.cjs`, Chromium): desktop 1366px e iPhone 13; sem erros de console, links internos e âncoras válidos, imagens carregando, `alt` em todas as imagens, `<h1>` em todas as páginas, sem rolagem horizontal no celular.
5. **Inspeção visual:** capturas da calculadora, estimate, dashboard, resumo, capas, pins e landing page (desktop e mobile) revisadas. Problemas encontrados e corrigidos: sobreposição na calculadora, título cortado, capa grátis mostrando a ferramenta errada, espaço no logo.
6. **Impressão/PDF:** áreas de impressão em 1 página nas abas Estimate, Invoice, Calculadora e Dashboard, exportadas a PDF pelo LibreOffice na geração das capturas.

## Bugs encontrados pelos testes e corrigidos
- MAXIFS/MINIFS sem o prefixo `_xlfn.` (daria #NAME? no Excel) → corrigido.
- Formulário vazio mostrava o preço mínimo (US$ 100) → agora mostra 0 enquanto não houver horas.
- Resumo de novembro no exemplo com margem de 100% (sem despesas) → dados de exemplo completados.

## Não testado / pendências
| Item | Status | Motivo |
|---|---|---|
| Abrir no **Microsoft Excel** real | IMPLEMENTADO, MAS NÃO TESTADO | Não há Excel no ambiente. Formato OOXML padrão, recalculado no LibreOffice. |
| Abrir no **Google Sheets** real | IMPLEMENTADO, MAS NÃO TESTADO | Sem conta Google. A compatibilidade de funções foi verificada estaticamente. **Primeiro passo do dono:** subir o Complete-EXAMPLE no Drive e conferir a aba Monthly Summary. |
| Upload e entrega na Payhip | PENDENTE DE AUTORIZAÇÃO | Precisa da conta do dono. |
| Checkout de teste | BLOQUEADO POR TERCEIROS | Depende da conta e do PayPal. Não fazemos compra real sem autorização. Use o produto grátis (US$ 0) para testar a entrega. |
| Importador de vendas da Payhip | IMPLEMENTADO, MAS NÃO TESTADO com export real | O formato do CSV da Payhip não foi confirmado. |
