# Clínica Mais Med — Entregáveis Clintia

Dois documentos servidos pelo mesmo projeto:

- **`/`** — DPV (Dossiê de Posicionamento e Vendas), entregável da Cláusula 4 do contrato de implantação PROClip.
- **`/dashboard`** — Relatório de performance de Google Ads + Meta Ads, no modelo do relatório da Alpha Policlínica. Ver [DASHBOARD.md](DASHBOARD.md) para o que é necessário para alimentá-lo e como carregar cada mês.

**Cliente:** Dr. Cauê Araujo Braz · Clínica Mais Med
**Operador:** Clintia
**Confidencial.** Não divulgar URL publicamente.

---

## Stack

- HTML estático (single page, sem build)
- Hospedagem: Vercel
- Versionamento: GitHub

Não há dependências, não há etapa de build. A Vercel serve o `index.html` direto.

---

## Estrutura

```
.
├── index.html       # DPV completo (5 abas, navegação SPA)
├── dashboard.html   # Relatório de performance Google Ads + Meta Ads
├── vercel.json      # headers de segurança + noindex
├── DASHBOARD.md     # como alimentar o relatório de performance
├── .gitignore
└── README.md
```

Duas páginas independentes no mesmo deploy: o DPV em `/` e o relatório de
performance em `/dashboard`. Uma não depende da outra.

---

## Subir no GitHub

Pré-requisito: Git instalado e conta no GitHub.

```bash
# dentro da pasta do projeto
git init
git add .
git commit -m "DPV Mais Med - versão inicial"
git branch -M main
```

Crie um repositório **privado** no GitHub (https://github.com/new). Importante que seja privado — o DPV contém estratégia comercial.

Depois conecte e empurre:

```bash
git remote add origin git@github.com:SEU-USUARIO/dpv-mais-med.git
git push -u origin main
```

---

## Hospedar na Vercel

1. Acesse https://vercel.com/new
2. Import Git Repository → selecione o repositório recém-criado
3. **Framework Preset:** Other (deixe como está, ele detecta sozinho)
4. **Root Directory:** `./`
5. **Build Command:** deixe vazio
6. **Output Directory:** deixe vazio
7. Clique em Deploy

Em ~30 segundos o link estará pronto: `https://dpv-mais-med.vercel.app` (ou similar).

---

## Proteger o acesso (recomendado)

O DPV não deve ficar indexado nem acessível publicamente. Três caminhos, do mais simples ao mais robusto:

### Opção 1 — URL não indexada (já configurada)
O `vercel.json` já envia `X-Robots-Tag: noindex, nofollow`. Google não indexa. Quem tiver o link acessa, mas o link não aparece em buscas.

### Opção 2 — Password Protection (Vercel Pro)
Em Project Settings → Deployment Protection → Vercel Authentication ou Password Protection. Custa US$20/mês no plano Pro, mas protege com senha sem alterar código.

### Opção 3 — Domínio com obscuridade
Use um subdomínio do tipo `dpv-cliente-3f7a2b.clintia.com.br`. Combinado com noindex, é suficiente para entregáveis confidenciais de curto prazo.

Para a entrega ao Cauê, **Opção 1 + URL enviada apenas no WhatsApp** resolve. Se quiser camada extra, vai de Opção 3.

---

## Atualizar o DPV

Para aplicar ajustes (lembrar das 2 rodadas previstas na Cláusula 4.3):

```bash
# editar index.html
git add index.html
git commit -m "Ajustes rodada 1 - feedback Cauê"
git push
```

A Vercel faz o deploy automático em segundos.

---

## Entregar para o cliente

O contrato (Cláusula 4.1) prevê entrega em **PDF**. Fluxo recomendado:

1. Mandar o link da Vercel para o Cauê revisar (mais fácil de navegar)
2. Coletar feedback dentro da janela de 15 dias (Cláusula 4.3)
3. Aplicar ajustes
4. Exportar versão final para PDF: abrir o link → Imprimir → Destino: Salvar como PDF → Layout Paisagem → Margens Mínimas → Imprimir gráficos de fundo: ON
5. Enviar o PDF como entregável oficial

---

## Domínio customizado (opcional)

Se quiser usar um subdomínio da Clintia (ex.: `dpv-mais-med.clintia.com.br`):

1. Vercel → Project → Settings → Domains
2. Adicionar o subdomínio
3. Configurar o CNAME no provedor de DNS conforme instrução da Vercel
