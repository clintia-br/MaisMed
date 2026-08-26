#!/usr/bin/env python3
"""
Converte o export do Google Ads (base por dia + palavra-chave) no bloco
`meses` consumido por dashboard.html.

Uso:
    python3 tools/csv-google-para-dados.py insights_mais_med.csv > meses.js

Depois cole a saída dentro de `DADOS.meses` em dashboard.html.

Formato de entrada esperado (export "Base de Dados - Relatório Ads"):
    linha 1  título
    linha 2  intervalo de datas
    linha 3  cabeçalho: Campanha, Dia, Pesquisar palavra-chave,
             Pesquisar tipo de correspondência de palavra-chave, Impr.,
             Cliques, CTR, Código da moeda, CPC méd., Custo, Conversões, ...

Os dados de Meta Ads não vêm daqui — são acrescentados ao objeto do mês
separadamente, na chave `meta`.
"""
import csv
import calendar
import json
import sys
from collections import defaultdict, OrderedDict

MESES_PT = [None, 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

SLUG_PT = [None, 'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
           'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


def numero(txt):
    """Converte número em formato pt-BR ('1.234,56', '12,5%') para float."""
    txt = (txt or '').strip().replace('%', '')
    if not txt:
        return 0.0
    if ',' in txt:
        txt = txt.replace('.', '').replace(',', '.')
    try:
        return float(txt)
    except ValueError:
        return 0.0


def ler(caminho):
    with open(caminho, encoding='utf-8-sig') as f:
        linhas = f.read().splitlines()
    # descarta as duas linhas de título até chegar no cabeçalho real
    inicio = next(i for i, l in enumerate(linhas) if l.startswith('Campanha,'))
    return list(csv.DictReader(linhas[inicio:]))


def agregar(linhas):
    meses = OrderedDict()
    for r in linhas:
        dia = r['Dia']
        chave = dia[:7]
        m = meses.setdefault(chave, {
            'dias': set(),
            'campanhas': defaultdict(lambda: dict(investimento=0.0, impressoes=0, cliques=0, leads=0)),
            'keywords': defaultdict(lambda: dict(investimento=0.0, impressoes=0, cliques=0, leads=0,
                                                 campanha='', correspondencia='')),
        })
        m['dias'].add(dia)

        custo = numero(r['Custo'])
        impr  = int(numero(r['Impr.']))
        cli   = int(numero(r['Cliques']))
        conv  = numero(r['Conversões'])

        c = m['campanhas'][r['Campanha']]
        c['investimento'] += custo
        c['impressoes']   += impr
        c['cliques']      += cli
        c['leads']        += conv

        termo = r['Pesquisar palavra-chave']
        k = m['keywords'][(r['Campanha'], termo)]
        k['campanha']       = r['Campanha']
        k['correspondencia'] = r['Pesquisar tipo de correspondência de palavra-chave']
        k['investimento']  += custo
        k['impressoes']    += impr
        k['cliques']       += cli
        k['leads']         += conv
    return meses


def montar(meses):
    saida = []
    # só o último mês do export pode estar em andamento; nos anteriores, uma
    # janela curta significa veiculação encerrada antes do fim do mês, não mês aberto
    mais_recente = max(meses) if meses else None
    for chave in sorted(meses, reverse=True):          # mais recente primeiro
        m = meses[chave]
        ano, mes_num = int(chave[:4]), int(chave[5:7])
        dias = sorted(m['dias'])
        primeiro, ultimo = dias[0], dias[-1]
        dias_no_mes = calendar.monthrange(ano, mes_num)[1]

        campanhas = [
            dict(nome=nome, **{k: round(v, 2) if isinstance(v, float) else v for k, v in vals.items()})
            for nome, vals in sorted(m['campanhas'].items(), key=lambda x: -x[1]['investimento'])
        ]
        keywords = [
            dict(termo=termo, campanha=vals['campanha'], correspondencia=vals['correspondencia'],
                 investimento=round(vals['investimento'], 2), impressoes=vals['impressoes'],
                 cliques=vals['cliques'], leads=round(vals['leads'], 2))
            for (_camp, termo), vals in sorted(m['keywords'].items(), key=lambda x: -x[1]['investimento'])
            if vals['impressoes'] > 0
        ]

        investimento = sum(c['investimento'] for c in campanhas)
        conversoes   = sum(c['leads'] for c in campanhas)

        bloco = OrderedDict()
        bloco['id']        = '%s-%d' % (SLUG_PT[mes_num], ano)
        bloco['rotulo']    = '%s %d' % (MESES_PT[mes_num], ano)
        bloco['periodo']   = '%s/%s – %s/%s' % (primeiro[8:], primeiro[5:7], ultimo[8:], ultimo[5:7])
        bloco['dias']      = len(dias)
        bloco['diasNoMes'] = dias_no_mes
        bloco['parcial']   = chave == mais_recente and int(ultimo[8:]) < dias_no_mes
        bloco['google']    = campanhas
        bloco['meta']      = []
        bloco['keywords']  = keywords

        # investimento sem nenhuma conversão registrada é quase sempre falta de
        # tag de conversão, não campanha ruim — sinaliza em vez de exibir CPL zero
        if investimento > 0 and conversoes == 0:
            bloco['alertas'] = [{
                'tipo': 'amber', 'icone': '🏷️',
                'titulo': 'Período sem conversões registradas',
                'texto': ('Houve investimento (%s) e cliques, mas nenhuma conversão foi contabilizada. '
                          'Confirmar se a tag de conversão já estava instalada neste período — sem ela, '
                          'o Google registra o clique mas não o contato gerado, e o CPL fica indisponível.'
                          % ('R$ %.2f' % investimento).replace('.', ','))
            }]
        saida.append(bloco)
    return saida


def registro(d, indent):
    """Serializa um registro (campanha/keyword) numa única linha legível."""
    partes = []
    for k, v in d.items():
        val = json.dumps(v, ensure_ascii=False) if isinstance(v, str) else repr(v)
        partes.append('%s: %s' % (k, val))
    return indent + '{ ' + ', '.join(partes) + ' }'


def js(blocos):
    saida = []
    for b in blocos:
        saida.append('    {')
        saida.append('      id: %s,' % json.dumps(b['id'], ensure_ascii=False))
        saida.append('      rotulo: %s,' % json.dumps(b['rotulo'], ensure_ascii=False))
        saida.append('      periodo: %s,' % json.dumps(b['periodo'], ensure_ascii=False))
        saida.append('      dias: %d, diasNoMes: %d, parcial: %s,'
                     % (b['dias'], b['diasNoMes'], 'true' if b['parcial'] else 'false'))
        if b.get('alertas'):
            saida.append('      alertas: [')
            for a in b['alertas']:
                saida.append(registro(a, '        ') + ',')
            saida.append('      ],')
        saida.append('      google: [')
        for c in b['google']:
            saida.append(registro(c, '        ') + ',')
        saida.append('      ],')
        saida.append('      meta: [],')
        saida.append('      keywords: [')
        for k in b['keywords']:
            saida.append(registro(k, '        ') + ',')
        saida.append('      ]')
        saida.append('    },')
    return '\n'.join(saida)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('uso: python3 tools/csv-google-para-dados.py <arquivo.csv>')
    print(js(montar(agregar(ler(sys.argv[1])))))
