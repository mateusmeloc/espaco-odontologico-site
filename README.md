# Espaço Odontológico — site institucional

Site one-page da clínica **Espaço Odontológico** (Feu Rosa, Serra/ES), no ar em
**[www.espacoodontologicoserra.com.br](https://www.espacoodontologicoserra.com.br)**.

É um site estático, sem framework e sem dependência de runtime: um único
`index.html` gerado por um build em Python, fotos otimizadas em WebP e hospedagem
gratuita no GitHub Pages.

## O que tem

- **12 seções** numa página só: topo, sinais, tratamentos, avaliações, resultados,
  clínica, estrutura, história, princípios, formas de pagamento, dúvidas e local
- **Foco em conversão**: botões de WhatsApp com mensagem pré-preenchida
- **SEO local**: JSON-LD (`Dentist`, `FAQPage` com 8 perguntas, horários, endereço e
  coordenadas), `canonical`, Open Graph e `lang="pt-BR"`
- **Imagens responsivas**: cada foto em duas larguras (`srcset`), carregamento
  preguiçoso e fallback quando um arquivo falha
- **Leve**: HTML de ~115 KB (marca e favicon embutidos como data URI), fotos como
  arquivos separados para ficarem em cache

## Estrutura

| Caminho | Função |
|---|---|
| `_build/template.html` | **fonte do site** — é aqui que se edita |
| `_build/build.py` | embute a marca no template e escreve o `index.html` |
| `_build/prepare-fotos.py` | converte as fotos originais em WebP (900 px e `@2x`) |
| `index.html` | arquivo final servido pelo Pages — **gerado, não edite direto** |
| `assets/fotos/` | fotos da clínica já otimizadas |
| `assets/logo.webp`, `favicon.png` | marca, embutida em base64 no HTML |
| `CNAME` | domínio próprio do GitHub Pages |

## Como rodar

```bash
python3 _build/build.py          # template + assets -> index.html
open index.html                  # abre direto no navegador, sem servidor
```

O build aborta (em vez de gerar um site quebrado) se faltar um arquivo ou sobrar
um placeholder no template.

Para adicionar ou trocar fotos, coloque os originais em `fotos-originais/` (pasta
local, **fora do git**) e rode:

```bash
python3 _build/prepare-fotos.py  # originais -> assets/fotos/*.webp
python3 _build/build.py
```

`prepare-fotos.py` usa `sips` (já vem no macOS) e `cwebp` (`brew install webp`) e só
reprocessa o que mudou.

## Publicação

O Pages serve a `main` pela raiz. O DNS fica no Registro.br: `www` aponta (CNAME)
para o GitHub Pages e o domínio sem `www` usa os IPs do Pages. Para publicar uma
mudança: editar o template, rodar o build e dar push.

## Fotos e privacidade

Fotos de pacientes só entram no site com autorização de uso de imagem. Os arquivos
originais (alta resolução, com metadados) ficam **fora do repositório** — `.gitignore`
bloqueia `fotos-originais/`, `_drive/` e `.heic` — e só as versões otimizadas, sem
metadados, vão para `assets/fotos/`.

## Conformidade

O conteúdo segue o Código de Ética Odontológica: sem comparação com concorrentes,
sem preço e sem promessa de resultado. O `aggregateRating` foi removido do JSON-LD de
propósito, porque o Google desencoraja a clínica marcar a própria nota sem os reviews
individuais; o bloco está comentado no template, caso a decisão mude.

## Licença

Todos os direitos reservados. Código, textos e imagens são da clínica e não têm
licença de reuso. O repositório é público para mostrar a forma como o site foi feito.
