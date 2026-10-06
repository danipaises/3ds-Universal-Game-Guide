# Modelo para fontes futuras

Aplicar quando a expansão for autorizada. Não preencher datas ou evidências sem consulta real. Não migrar os 67 guias nesta etapa.

Em `guides/pt-BR/<game-id>/SOURCES.md`, registrar:

```text
Game / edição / plataforma:
Guide ID / idioma:
Região / Title ID / evidência: (não inferir a região pelo idioma)

Fonte / autor ou site:
Página / artigo / seção:
URL direta:
Finalidade / páginas do guia beneficiadas:
Consulta real em: AAAA-MM-DD
Tier: A / B / C
Confiança do fato: PRIMARY / SECONDARY / CROSS-CHECKED / UNCERTAIN
Outra evidência independente: (ou declarar ausente)
Licença / uso: referência factual, prosa original; autorização separada para assets
Observações / diferenças de versão ou região:
Divergências / decisão fundamentada / pendências:
```

Tier mede a categoria da fonte; confiança mede a evidência do fato. Um artigo especializado pode verificar melhor um percurso que um manual. Uma fonte primária também pode ser insuficiente para uma afirmação mais ampla.

Preservar o contrato existente de `sources.json`: lista de objetos com `title`, `url` HTTPS e `retrieved`. Cada `pages[].sources` em `guide.json` contém índices válidos dessa lista. Não reordenar/remover fontes sem atualizar referências. Associar detalhes de confiança, divergências e licenças no SOURCES.md, sem introduzir um formato novo no runtime.

O catálogo usa `data/games.json` (Game ID → região → Title IDs e cobertura por idioma) e `data/title-id-evidence.json` (evidência da associação). O diretório e `guide.json.gameId` devem corresponder ao catálogo, e o idioma deve corresponder ao diretório. Um jogo reconhecido sem guia continua explícito; não criar páginas vazias para apagar essa lacuna.

Executar `python builder.py validate --lang pt-BR` e os testes oficiais. A validação confirma estrutura, IDs, referências e hashes; não confirma os fatos, independência das fontes, completude editorial ou compatibilidade física.
