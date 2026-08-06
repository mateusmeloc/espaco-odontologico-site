# Espaço Odontológico — site institucional

Site one-page da clínica Espaço Odontológico (Feu Rosa, Serra/ES).
Responsável técnica: Dra. Hosana A. S. Melo — CRO-ES 5226.

**Status:** prévia V6, aguardando aprovação da Dra. Hosana.

## Como funciona

**Nunca edite `index.html` direto — ele é gerado.** A fonte de verdade é
`_build/template.html`; o build embute a marca como data URI e escreve o
`index.html`.

```bash
python3 _build/build.py          # template + assets -> index.html
```

Fotos da clínica são **arquivos separados** em `assets/fotos/`, não base64:
carregam sob demanda, ficam em cache e mantêm o HTML abaixo de 100 KB. Para
adicionar ou trocar fotos, salve os originais em `fotos-originais/` e rode:

```bash
python3 _build/prepare-fotos.py  # originais -> assets/fotos/*.webp (900px e @2x)
python3 _build/build.py
```

`prepare-fotos.py` precisa do `cwebp` (`brew install webp`); `sips` já vem no
macOS. Só reprocessa o que mudou.

| Arquivo | Uso |
|---|---|
| `_build/template.html` | fonte do site — é aqui que se edita |
| `assets/logo-original.png` | 900×227, fonte da marca |
| `assets/logo.webp` | 500 px, embutido em base64 no HTML |
| `assets/favicon.png` | 64 px, embutido em base64 |
| `assets/fotos/` | fotos da clínica, servidas como arquivo |
| `fotos-originais/` | originais em alta, entrada do `prepare-fotos.py` |

## Pendências antes de publicar no domínio definitivo

- [ ] Fotos reais em alta: fachada, recepção, consultórios, equipamentos, antes/depois, retratos das 5 dentistas
- [ ] **As 3 imagens hospedadas no GreatPages estão com 404** — o site mostra um quadro "Foto em produção" no lugar. As demais fotos ainda são hotlink de terceiros (Wix, Google) e precisam ser substituídas por arquivos locais
- [ ] Frase da Dra. Hosana para o bloco da história
- [ ] Respostas de convênios, atendimento infantil, valor da avaliação e estacionamento (saíram do FAQ até serem confirmadas)
- [ ] Seção da equipe completa
- [ ] Definir o domínio e trocar `canonical`, `og:url` e os campos `@id` / `url` do schema (4 pontos no `index.html`)
- [ ] GA4, Meta Pixel e Search Console no dia da publicação

## Conformidade

Sem comparação com concorrentes (art. 44 do Código de Ética Odontológica), sem
preço, sem promessa de resultado. Antes/depois com nota de autorização de uso de
imagem. Responsável técnica e CRO no rodapé.

O `aggregateRating` foi removido do JSON-LD de propósito — o Google desencoraja
marcar a própria nota sem os reviews individuais. O bloco está comentado no
`index.html` para reverter, se for a decisão.
