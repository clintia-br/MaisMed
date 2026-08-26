# Dashboard de Performance — Google Ads + Meta Ads

Relatório de campanhas da Clínica Mais Med, no mesmo modelo do relatório da
Alpha Policlínica (`clintia-br/Alpha-relatorio`).

**Arquivo:** `dashboard.html` · **URL após deploy:** `/dashboard`

---

## Estado atual

A página está construída e funcionando. O que ela mostra hoje é a **tela de
setup**, porque `DADOS.meses` está vazio — não há dados das contas da Mais Med
disponíveis. Assim que o primeiro mês for carregado, a tela de setup some
sozinha e o relatório aparece no lugar.

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

### 2. Conta do Google Ads — **bloqueia**

Necessário:

- ID da conta (CID, formato `000-000-0000`);
- o export mensal da aba **Campanhas**, com as colunas `Custo`, `Impr.`,
  `Cliques` e `Conversões`.

Não há conector de Google Ads disponível — no relatório da Alpha esses números
também vêm do export manual da interface. Alternativa: acesso de leitura à conta
para que a Clintia gere o export.

### 3. Definição do que conta como resultado — **definir**

No modelo da Alpha: Google = **leads** (conversões) e Meta = **conversas
iniciadas**. Vale confirmar se é o mesmo critério para a Mais Med, já que aqui o
canal de marcação é o WhatsApp e o site institucional é novo — se a conversão do
Google for clique-para-WhatsApp em vez de formulário, o rótulo "lead" continua
válido, mas a origem muda e isso precisa estar claro para o cliente.

### 4. Recorte e periodicidade — **definir**

Um bloco por mês, com o mês corrente marcado como parcial (o relatório calcula
o ritmo diário para permitir comparação justa entre um mês parcial e meses
fechados). Definir a partir de qual mês o relatório começa — a primeira campanha
de tráfego pago (pediatria, Cláusula 6) é o marco zero.

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

## Como carregar um mês

Abra `dashboard.html`, localize a constante `DADOS` no topo do bloco `<script>`
e acrescente um objeto ao array `meses`. Nada mais precisa ser alterado.

```js
const DADOS = {
  cliente:  'Clínica Mais Med',
  operador: 'Clintia',
  meses: [
    {
      id:        'setembro-2026',        // slug único
      rotulo:    'Setembro 2026',        // texto do botão do seletor
      periodo:   '01/09 – 30/09',        // chip do cabeçalho
      dias:      30,                     // dias com veiculação no recorte
      diasNoMes: 30,                     // total de dias do mês
      parcial:   false,                  // true = mês em andamento

      // opcional: verba prevista para o recorte
      orcamento: { google: 3000, meta: 1500 },

      google: [
        { nome: '[MaisMed] Pediatria', investimento: 812.40, impressoes: 9120, cliques: 940, leads: 118 }
      ],

      meta: [
        { nome: '[MaisMed][WPP] Pediatria', investimento: 640.00, impressoes: 71200, alcance: 28400, conversas: 214 }
      ],

      // opcional
      planoDiario: [
        { especialidade: 'Pediatria', google: 100, meta: 50 }
      ],

      // opcional
      alertas: [
        { tipo: 'amber', icone: '⚠️', titulo: 'Título curto', texto: 'Explicação.' }
      ],

      // opcional
      destaques: [
        { icone: '📈', titulo: 'Título curto', texto: 'Leitura do número.' }
      ]
    }
  ]
};
```

O mês mais recente deve ficar **em primeiro** no array — é ele que abre por
padrão. O seletor de mês só aparece quando há dois ou mais meses.

### De onde vem cada campo

| Campo | Google Ads (export "Campanhas") | Meta Ads (MCP / Gerenciador) |
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
diário entre meses, diferença e % consumido do orçamento, e a projeção de
investimento para 7/15/30 dias. Tudo deriva dos campos acima.

---

## Estrutura da página

Um seletor de mês no topo e quatro abas por mês, iguais às da Alpha:

1. **Visão Geral** — KPIs consolidados, ritmo diário entre meses, comparativo
   por plataforma, distribuição de investimento e resultados, orçamento
   planejado, esperado x realizado, projeção e destaques.
2. **Google Ads** — KPIs, tabela por campanha (investimento, leads, CPL, CTR,
   impressões) e barras de investimento e leads.
3. **Meta Ads** — KPIs, tabela por campanha (investimento, conversas, CPR,
   impressões, alcance) e barras de investimento e conversas.
4. **Todas as Campanhas** — as duas listas completas, lado a lado.

---

## Diferença em relação ao relatório da Alpha

Na Alpha, cada mês é HTML escrito à mão — todos os totais, percentuais e
larguras de barra estão digitados no arquivo, o que faz cada fechamento custar
centenas de linhas e abre espaço para erro de conta. Aqui a página é montada a
partir do objeto `DADOS`: carregar um mês é colar os números brutos de cada
campanha, e o resto se calcula. Visualmente o resultado é o mesmo modelo.
