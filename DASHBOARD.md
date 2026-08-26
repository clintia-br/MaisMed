# Dashboard de Performance — Google Ads + Meta Ads

Relatório de campanhas da Clínica Mais Med, no mesmo modelo do relatório da
Alpha Policlínica (`clintia-br/Alpha-relatorio`).

**Arquivo:** `dashboard.html` · **URL após deploy:** `/dashboard`

---

## Estado atual

**Google Ads carregado:** abril a agosto de 2026, a partir do export da conta
(`insights_mais_med.csv`, 4/4 a 25/8). São 5 meses, 5 campanhas e 31 termos de
busca, totalizando R$ 3.216,58 e 220,99 conversões.

**Meta Ads pendente:** a chave `meta` de todos os meses está vazia. A aba Meta
Ads e os blocos de comparação entre plataformas ficam ocultos ou marcados como
"sem veiculação" até a conta ser compartilhada (ver item 1 abaixo).

---

## O que é necessário para ligar os dados

### 1. Conta de anúncios do Meta Ads — **bloqueia**

Necessário:

- ID da conta de anúncios da Mais Med (formato `act_000000000000`);
- que essa conta esteja compartilhada com a Business Manager usada pela Clintia.

A conexão de Meta Ads da Clintia hoje enxerga 108 contas de anúncio e **nenhuma
delas é da Mais Med**. Enquanto a conta não for compartilhada, não há como puxar
investimento, conversas iniciadas, impressões e alcance por campanha.

Com o acesso liberado, o fluxo é o mesmo usado no relatório da Alpha: os números
vêm direto da conta via Meta Ads MCP, sem export manual.

### 2. Conta do Google Ads — **resolvido para 2026**

Alimentado pelo export da base por dia + palavra-chave. Para atualizar, basta
gerar o export novamente e rodar o conversor (ver *Atualizar os dados* abaixo).

Não há conector de Google Ads disponível, então continua sendo export manual —
mesmo caminho do relatório da Alpha. O que muda é que aqui o export não precisa
ser transcrito à mão: o conversor faz a agregação.

### 3. Rastreamento de abril e maio — **confirmar**

`PRIMEIRA CAMPANHA` rodou de 05/04 a 31/05 com R$ 420,30 de investimento, 230
cliques e **zero conversões registradas**. Todas as outras campanhas, de junho em
diante, registram conversões normalmente.

O padrão é típico de tag de conversão ausente, não de campanha sem resultado —
mas isso precisa ser confirmado na conta antes de afirmar qualquer coisa ao
cliente. Nesses dois meses o relatório mostra CPL como `—` em vez de um número
inventado, e exibe um alerta explicando a lacuna.

Vale também confirmar o critério de conversão em vigor: se for clique-para-
WhatsApp em vez de formulário, o rótulo "lead" continua válido, mas a origem
muda e isso precisa estar claro no relatório.

### 4. Recorte e periodicidade — **definido pelo export**

Um bloco por mês, gerado automaticamente. Apenas o mês mais recente do export é
marcado como parcial; nos meses anteriores, uma janela curta significa que a
veiculação parou antes do fim do mês, não que o mês esteja aberto. O relatório
calcula o ritmo diário para permitir comparação justa entre eles.

### 5. Orçamento planejado por especialidade — **definir**

Verba diária prevista por especialidade em cada plataforma. Alimenta dois
blocos: *Investimento Diário por Especialidade* e *Orçamento Esperado x
Investido Real*. Ambos são opcionais — se não forem informados, o relatório
simplesmente não renderiza esses blocos.

### 6. Publicação — **pronto**

Deploy na Vercel a partir deste repositório. `vercel.json` já envia
`X-Robots-Tag: noindex, nofollow` e `Cache-Control: must-revalidate` para
`dashboard.html`. Com `cleanUrls`, a página fica em `/dashboard`.

---

## Atualizar os dados

### Google Ads — via conversor

1. No Google Ads, gere o export da base com granularidade de **dia** e
   **palavra-chave** (mesmo formato do `insights_mais_med.csv`: colunas
   `Campanha`, `Dia`, `Pesquisar palavra-chave`, `Pesquisar tipo de
   correspondência de palavra-chave`, `Impr.`, `Cliques`, `CTR`,
   `Código da moeda`, `CPC méd.`, `Custo`, `Conversões`).
2. Rode o conversor:

   ```bash
   python3 tools/csv-google-para-dados.py export.csv > meses.js
   ```

3. Substitua o conteúdo de `DADOS.meses`, em `dashboard.html`, pela saída.

O conversor agrega por campanha e por palavra-chave, monta os meses do mais
recente para o mais antigo, marca como parcial apenas o último e insere
automaticamente o alerta de rastreamento em meses com investimento e nenhuma
conversão.

### Meta Ads — manual, por enquanto

Assim que a conta for compartilhada, os números vêm via Meta Ads MCP e entram na
chave `meta` de cada mês:

```js
meta: [
  { nome: '[MaisMed][WPP] Pediatria', investimento: 640.00, impressoes: 71200, alcance: 28400, conversas: 214 }
],
```

Preenchida essa chave, a aba Meta Ads, o comparativo entre plataformas e os
cards de distribuição passam a aparecer sozinhos.

### Campos opcionais

Podem ser acrescentados a mão em qualquer mês:

```js
orcamento:   { google: 3000, meta: 1500 },                        // verba prevista no recorte
planoDiario: [ { especialidade: 'Pediatria', google: 100, meta: 50 } ],
alertas:     [ { tipo: 'amber', icone: '⚠️', titulo: '…', texto: '…' } ],
destaques:   [ { icone: '📈', titulo: '…', texto: '…' } ]
```

`orcamento` liga o bloco *Orçamento Esperado x Investido Real*; `planoDiario`
liga o *Investimento Diário por Especialidade*. Sem eles, os blocos simplesmente
não são renderizados.

### De onde vem cada campo

| Campo | Google Ads (export) | Meta Ads (MCP / Gerenciador) |
|---|---|---|
| `investimento` | Custo | `spend` |
| `impressoes` | Impr. | `impressions` |
| `cliques` | Cliques | — |
| `alcance` | — | `reach` |
| `leads` | Conversões | — |
| `conversas` | — | `results` (conversas iniciadas) |

### O que é calculado sozinho

Não preencha à mão: CPL, CPR, CTR, totais por plataforma, total consolidado,
investimento/dia, resultados/dia, percentuais de distribuição, tabela de ritmo
diário entre meses, diferença e % consumido do orçamento, projeção de
investimento para 7/15/30 dias, resumo por tipo de correspondência e detecção de
palavras-chave duplicadas entre campanhas. Tudo deriva dos campos acima.

## Estrutura da página

Um seletor de mês no topo e quatro abas por mês, iguais às da Alpha:

1. **Visão Geral** — KPIs consolidados, ritmo diário entre meses, comparativo
   por plataforma, distribuição de investimento e resultados, orçamento
   planejado, esperado x realizado, projeção e destaques.
2. **Google Ads** — KPIs, tabela por campanha (investimento, leads, CPL, CTR,
   impressões) e barras de investimento e leads.
3. **Meta Ads** — KPIs, tabela por campanha (investimento, conversas, CPR,
   impressões, alcance) e barras de investimento e conversas.
4. **Palavras-chave** — só aparece quando o mês tem detalhamento por termo.
   Traz CPL por palavra-chave, investimento sem retorno, desempenho por tipo de
   correspondência e alerta de termos que disputam entre campanhas.
5. **Todas as Campanhas** — as duas listas completas, lado a lado.

---

## Diferença em relação ao relatório da Alpha

Na Alpha, cada mês é HTML escrito à mão — todos os totais, percentuais e
larguras de barra estão digitados no arquivo, o que faz cada fechamento custar
centenas de linhas e abre espaço para erro de conta. Aqui a página é montada a
partir do objeto `DADOS`: carregar um mês é colar os números brutos de cada
campanha, e o resto se calcula. Visualmente o resultado é o mesmo modelo.
