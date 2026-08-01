# Espaço Odontológico — site institucional

Site one-page da clínica Espaço Odontológico (Feu Rosa, Serra/ES).
Responsável técnica: Dra. Hosana A. S. Melo — CRO-ES 5226.

**Status:** prévia V6, aguardando aprovação da Dra. Hosana.

## Como funciona

`index.html` é autocontido: CSS, JavaScript, logo e favicon estão embutidos no
próprio arquivo. Não há build, dependência ou servidor — abrir o arquivo no
navegador é suficiente.

A pasta `assets/` guarda os originais usados para gerar os embutidos:

| Arquivo | Uso |
|---|---|
| `logo-original.png` | 900×227, fonte da marca |
| `logo.webp` | 500 px, é este que está em base64 no HTML |
| `favicon.png` | 64 px, também em base64 |

Para regerar depois de trocar a marca:

```bash
sips -Z 500 assets/logo-original.png --out /tmp/l.png && cwebp -q 88 -alpha_q 100 /tmp/l.png -o assets/logo.webp
```

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
