# Dashboard de Performance — Google Ads

Relatório de campanhas da Clínica Mais Med, no modelo do relatório da Alpha
Policlínica (`clintia-br/Alpha-relatorio`), adaptado para uma conta que roda
**apenas Google Ads**, com campanhas de pesquisa otimizadas para captação de
leads.

**Arquivo:** `dashboard.html` · **URL após deploy:** `/dashboard`

---

## Estado atual

Carregado com o export da conta de **abril a agosto de 2026** (04/04 a 25/08):
5 meses, 5 campanhas e 31 termos de busca, totalizando R$ 3.216,58 e 220,99
conversões.

---

## Pendências

### 1. Rastreamento de abril e maio — **confirmar**

`PRIMEIRA CAMPANHA` rodou de 05/04 a 31/05 com R$ 420,30 de investimento, 230
cliques e **zero conversões registradas**. Todas as campanhas de junho em diante
registram conversões normalmente.

O padrão é típico de tag de conversão ausente, não de campanha sem resultado —
mas isso precisa ser confirmado na conta antes de virar leitura para o cliente.
Enquanto não se confirma, o relatório:

- mostra CPL como `—` nesses meses, em vez de um número inventado;
- exibe um alerta apontando a lacuna;
- e informa, na tabela de evolução, o CPL acumulado considerando apenas os
  meses com rastreamento ativo (R$ 12,65, contra R$ 14,56 do acumulado bruto).

### 2. Definição do que conta como lead — **confirmar**

As campanhas são otimizadas para captação de leads. Confirmar qual ação está
marcada como conversão na conta — clique-para-WhatsApp, ligação ou formulário —
para que o rótulo "lead" no relatório corresponda ao que o cliente entende por
lead. O canal de marcação da clínica é o WhatsApp.

### 3. Orçamento planejado — **opcional**

Verba prevista por período e, se houver, o plano diário por especialidade.
Alimenta os blocos *Orçamento Esperado x Investido Real* e *Investimento Diário
por Especialidade*. Sem eles, os blocos simplesmente não são renderizados.

### 4. Publicação — **pronto**

Deploy na Vercel a partir deste repositório. `vercel.json` já envia
`X-Robots-Tag: noindex, nofollow` e `Cache-Control: must-revalidate` para
`dashboard.html`. Com `cleanUrls`, a página fica em `/dashboard`.

---

## Atualizar os dados

1. No Google Ads, gere o export da base com granularidade de **dia** e
   **palavra-chave** — mesmo formato do `insights_mais_med.csv`, com as colunas
   `Campanha`, `Dia`, `Pesquisar palavra-chave`, `Pesquisar tipo de
   correspondência de palavra-chave`, `Impr.`, `Cliques`, `CTR`,
   `Código da moeda`, `CPC méd.`, `Custo`, `Conversões`.
2. Rode o conversor:

   ```bash
   python3 tools/csv-google-para-dados.py export.csv > meses.js
   ```

3. Substitua o conteúdo de `DADOS.meses`, em `dashboard.html`, pela saída.

O conversor agrega por campanha e por palavra-chave, monta os meses do mais
recente para o mais antigo, marca como parcial apenas o último e insere
automaticamente o alerta de rastreamento em meses com investimento e nenhuma
conversão.

### Estrutura de um mês

```js
{
  id:        'agosto-2026',        // slug único
  rotulo:    'Agosto 2026',        // texto do botão do seletor
  periodo:   '01/08 – 25/08',      // chip do cabeçalho
  dias:      25,                   // dias com veiculação no recorte
  diasNoMes: 31,                   // total de dias do mês
  parcial:   true,                 // só o mês mais recente do export

  google: [
    { nome: '[Pediatria]', investimento: 251.18, impressoes: 1279, cliques: 161, leads: 51 }
  ],

  keywords: [
    { termo: 'pediatra ipiaú', campanha: '[Pediatria]', correspondencia: 'Correspondência de frase',
      investimento: 19.68, impressoes: 247, cliques: 13, leads: 1 }
  ]
}
```

### Campos opcionais

Acrescentados à mão em qualquer mês:

```js
orcamento:   3000,                                                 // verba prevista no recorte
planoDiario: [ { especialidade: 'Pediatria', investimentoDia: 100 } ],
alertas:     [ { tipo: 'amber', icone: '⚠️', titulo: '…', texto: '…' } ],
destaques:   [ { icone: '📈', titulo: '…', texto: '…' } ]
```

### De onde vem cada campo

| Campo | Coluna do export |
|---|---|
| `investimento` | Custo |
| `impressoes` | Impr. |
| `cliques` | Cliques |
| `leads` | Conversões |

### O que é calculado sozinho

Não preencha à mão: CPL, CTR, totais por campanha e por mês, acumulado,
investimento/dia, leads/dia, projeção de investimento e de leads, percentuais,
resumo por tipo de correspondência, detecção de palavras-chave duplicadas entre
campanhas e o CPL acumulado ajustado para períodos sem rastreamento. Tudo deriva
dos campos acima.

---

## Estrutura da página

Um seletor de mês no topo e três abas:

1. **Visão Geral** — KPIs do mês (investimento, leads, CPL), evolução mês a mês
   com ritmo diário e acumulado, orçamento planejado quando informado, e
   projeção (só no mês em andamento).
2. **Campanhas** — leitura por campanha: qual trouxe mais leads, qual tem o
   melhor CPL, qual consome mais verba, tabela completa e barras de leads e
   investimento.
3. **Palavras-chave** — só aparece quando o mês tem detalhamento por termo. CPL
   por palavra-chave, investimento sem retorno, desempenho por tipo de
   correspondência e alerta de termos que disputam entre campanhas.

Regras de exibição que o relatório aplica sozinho:

- período com investimento e nenhuma conversão mostra CPL como `—`, nunca
  `R$ 0,00`, e dispara o alerta de rastreamento;
- "melhor CPL" exige volume mínimo de 3 leads, para não premiar um termo ou
  campanha de lead único;
- só o mês mais recente do export é tratado como em andamento — nos anteriores,
  uma janela curta significa veiculação encerrada, não mês aberto;
- projeção aparece apenas em mês em andamento.

---

## Diferença em relação ao relatório da Alpha

O relatório da Alpha cobre duas plataformas e tem cada mês escrito à mão em
HTML: todos os totais, percentuais e larguras de barra digitados no arquivo, o
que faz cada fechamento custar centenas de linhas e abre espaço para erro de
conta.

Aqui a página é montada a partir do objeto `DADOS`, e o objeto sai do conversor.
Como a conta é só Google Ads, os blocos de comparação entre plataformas foram
substituídos pela evolução mês a mês, e o export com granularidade de termo de
busca — que o modelo da Alpha descartaria — virou a aba de palavras-chave.
