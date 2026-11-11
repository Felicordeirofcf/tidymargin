# 04 — Especificação do produto

Arquivos finais: `products/release/*.zip` (são estes que você sobe na Payhip). Fontes: `kit/`.

## Módulos por planilha

| Aba | Starter | Complete | Premium | Função |
|---|:-:|:-:|:-:|---|
| Start Here | ✓ | ✓ | ✓ | Início rápido, índice com links, código de cores, avisos |
| Settings | ✓ | ✓ | ✓ | Empresa, salário, encargos, sq ft/h, horas por quarto/banheiro, custo/milha, overhead, jobs/mês, taxa do cartão, margem-alvo, imposto, arredondamento, preço mínimo, prazos, tabelas editáveis (serviços, imóveis, frequências, condição, categorias) |
| Price Calculator | ✓ | ✓ | ✓ | **Módulo 1:** horas, custos, preço, margens e "Check a price" |
| Quote Table | ✓ | ✓ | ✓ | 50 jobs lado a lado |
| Margin vs Markup | ✓ | ✓ | ✓ | Conversor e explicação |
| Estimate | ✓ | ✓ | ✓ | **Módulo 5:** orçamento imprimível em 1 página (letter) |
| Clients | | ✓ | ✓ | **Módulo 3:** 300 clientes; último e próximo atendimento, dias sem visita, follow-up e receita total (automáticos) |
| Schedule | | ✓ | ✓ | **Módulo 4:** 600 visitas; status Scheduled/Confirmed/In Progress/Completed/Cancelled; destaque dos próximos 7 dias; próxima visita sugerida |
| Transactions | | ✓ | ✓ | **Módulo 2:** 1.500 lançamentos; categoria → grupo (receita, mão de obra, insumos, transporte, variável, fixo, imposto); status Received/Paid/Pending |
| Monthly Summary | | ✓ | ✓ | **Módulo 2:** resultado mensal e anual, lucro ≠ caixa, comparação com o mês anterior, resultado por serviço, gráfico |
| Invoice | | ✓ | ✓ | **Módulo 5:** fatura com vencimento, valor pago e saldo |
| Dashboard | | | ✓ | KPIs do ano, do mês e da operação + 2 gráficos + mesmo mês do ano anterior |
| Goal Planner | | | ✓ | Ponto de equilíbrio, meta de pró-labore e capacidade |
| Commercial Bid | | | ✓ | Preço mensal de contrato comercial |
| Crew Cost | | | ✓ | Custo real por hora faturável |
| Checklists | | | ✓ | Standard, deep e move-in/out |

Também acompanham: o PDF User Guide (todos os tiers), o PDF Pricing Playbook (Premium), o README.txt e o arquivo EXAMPLE preenchido com uma empresa fictícia.

## Fórmulas (fonte da verdade: `kit/pricing.py`)
- **Horas** = (sqft ÷ sqft_por_hora + quartos×h_quarto + banheiros×h_banheiro) × mult_serviço × mult_imóvel × mult_condição. Pode ser substituído por um valor manual.
- **Mão de obra** = horas × salário × (1 + encargos).
- **Custo direto** = mão de obra + insumos + milhas×custo/milha + outros.
- **Overhead do job** = overhead mensal ÷ jobs por mês.
- **Preço** = custo total ÷ (1 − margem − taxa_cartão×(1+imposto)). Isso garante que **lucro líquido ÷ preço = margem-alvo**, ou seja, margem e não markup.
- **Preço cobrado** = MAX(preço mínimo, ARREDONDAR.PARA.CIMA(preço ÷ passo) × passo). Se não houver horas, o preço é 0.
- **Preço "regular"** = preço ÷ (1 − desconto total), com desconto total = 1 − (1−freq)(1−extra). Assim o desconto sai do preço regular e não da margem.
- **Margem bruta** = (preço − mão de obra − insumos) ÷ preço.
- **Margem de contribuição** = (preço − custos diretos − taxa do cartão) ÷ preço.
- **Margem líquida** = (contribuição − overhead) ÷ preço.
- **Markup equivalente** = lucro ÷ custo.

## Regras de qualidade
- Sem macros, sem scripts e sem links externos.
- Só funções compatíveis com Excel 2019+/365, Excel Web, Google Sheets e LibreOffice. Isso é verificado automaticamente.
- Sem "Tabelas" do Excel (ListObjects), para não quebrar referências no Sheets.
- Validação de dados: números ≥ 0, percentuais em faixas, listas suspensas e datas.
- Abas de cálculo protegidas **sem senha**: evitam erros acidentais, e o usuário pode desproteger.
- Valores padrão marcados como EXEMPLO. Não há tabela universal de preços dos EUA.
- Os dados do usuário ficam no próprio arquivo dele. Para excluir, apaga-se a linha; para exportar, salva-se em CSV.

## Diferenças entre Excel e Google Sheets
- O Sheets ignora a proteção de abas: a fórmula fica desprotegida, mas funciona.
- Os gráficos podem ficar com aparência um pouco diferente.
- Excel 2016 e anteriores não têm MAXIFS/MINIFS: as colunas "Last/Next visit" da aba Clients mostram #NAME?. Isso está documentado, com a alternativa (Excel Web, que é grátis, ou Sheets).

## Limitações
- Não há sincronização com Google Calendar nem com Outlook. Não prometemos isso.
- O invoice não cobra: é só um documento.
- Não há versão em espanhol. Está planejada para a v1.1.
- O Google Sheets **não foi testado num Google Sheets real**, porque não havia conta disponível. A compatibilidade foi verificada estaticamente, função a função. Ver 06.
