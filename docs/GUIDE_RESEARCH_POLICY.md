# Política de pesquisa e autoria dos guias

## Condição para retomar conteúdo

A prioridade atual é estabilidade. A 0.2.2-alpha foi testada em Old Nintendo 3DS / Luma 13.1.1: MINIMAL-BOOT e MINIMAL PASS; FULL PARTIAL PASS, com crashes em Pesquisa Offline e Configurações. Não expandir guias agora. Retomar produção extensa somente após correções, regressões e teste físico que aprove FULL boot, reconhecimento, guia, busca, configurações, mapas e retorno ao jogo. Manter evidência por build/variante; CI não comprova experiência em hardware.

## Escopo editorial

Escrever primeiro em **pt-BR**, com português natural; preparar en-US e outros idiomas depois. Região do jogo e idioma do guia são independentes. Priorizar jogos nativos do 3DS das famílias Mario (Super Mario, Kart, Party, Mario & Luigi, Luigi's Mansion, Yoshi e derivados adequados), Pokémon, Zelda e Kirby existentes no catálogo. Não apagar outros jogos existentes. Aplicativos recebem referência funcional, não um walkthrough artificial.

Cada variante regional precisa de evidência identificável: jogo, região, Title ID, idioma do guia e game-id associado. Nunca presumir IDs iguais entre USA/EUR/JPN, inferir um ID-base a partir de update/DLC ou inventar versões. Dúvidas ficam NEEDS_VERIFICATION no TITLE_ID_AUDIT.md.

## Hierarquia e usos das fontes

A regra é **usar fontes confiáveis**, não limitar a pesquisa a fontes oficiais. Avaliar a página, sua edição e a evidência do fato; uma fonte especializada pode ser mais útil para walkthroughs, encounters, colecionáveis, mapas e 100%.

1. **TIER A — primárias:** Nintendo, Nintendo Support, manuais eletrônicos/dos jogos, páginas oficiais, Pokémon oficial e observação verificável no próprio jogo. Prioridade para controles, terminologia, mecânicas documentadas, modos e recursos oficiais. Registrar edição e, para observação direta, build/região e método de reprodução.
2. **TIER B — especializadas confiáveis:** Super Mario Wiki para Mario/Luigi/Yoshi; Bulbapedia e Serebii para Pokémon; Zelda Dungeon e Zelda Wiki para Zelda; WiKirby para Kirby; StrategyWiki quando aplicável. Confirmar plataforma/edição; diferenças de remake importam.
3. **TIER C — comunitárias secundárias:** GameFAQs, guias especializados reconhecidos e comunidades técnicas úteis. Complementar e fazer cross-check. Uma postagem isolada não ganha confiabilidade automaticamente. Nunca copiar walkthroughs ou mapas sem licença/permissão apropriada.

| Franquia | Fontes especializadas | Uso prioritário |
|---|---|---|
| Mario | Super Mario Wiki; StrategyWiki | Mundos/fases, Star Coins/Star Medals, inimigos, power-ups, saídas, desbloqueáveis, Kart/Party/RPG/Luigi/Yoshi |
| Pokémon | Bulbapedia; Serebii; StrategyWiki | Bulbapedia: progressão, rotas/cidades, dungeons, ginásios/trials, história e itens. Serebii: encounters, níveis, Pokédex, evolução, moves/abilities, Megas, Z-Moves, lendários e pós-game |
| Zelda | Zelda Dungeon; Zelda Wiki; StrategyWiki | Zelda Dungeon: dungeons, puzzles, bosses, colecionáveis, side quests, 100%. Zelda Wiki: itens/locais/mecânicas e diferenças entre versões |
| Kirby | WiKirby; StrategyWiki | Fases, Copy Abilities, Sun Stones, Rare Keychains, Code Cubes, stickers, bosses, extras e desbloqueáveis |

Essa lista orienta a pesquisa; não concede licença de reprodução. Abrir a página relevante e verificar sua situação atual quando a pesquisa for retomada. Tentar confirmar fatos importantes em pelo menos duas fontes independentes quando razoável: colecionáveis, desbloqueios, segredos, encontros Pokémon, itens, bosses, 100%, pós-game e diferenças regionais/entre versões. Dois sites reproduzindo a mesma fonte não são confirmações independentes. Quando só houver uma evidência, declarar SECONDARY ou UNCERTAIN conforme o caso. Preservar nomes originais quando não houver tradução oficial adequada. Não inventar traduções oficiais.

## Rastreabilidade e confiança

Cada jogo mantém `guides/pt-BR/<game-id>/SOURCES.md`. Registrar fonte/autor, URL direta, título ou seção consultada, edição/plataforma, finalidade, data de consulta real e licença quando relevante. Usar o [modelo de fontes](SOURCES_TEMPLATE.md) para novos registros, sem reescrever fontes existentes ou inventar consultas. Manter `sources.json` e os índices `pages[].sources` de `guide.json` coerentes; o Builder verifica esses vínculos. A interface offline pode omitir URLs longas; o repositório conserva a rastreabilidade.

| Classificação | Evidência exigida |
|---|---|
| PRIMARY | Manual/documento oficial para o fato descrito |
| SECONDARY | Uma fonte comunitária identificada; não afirmar confirmação cruzada |
| CROSS-CHECKED | Duas fontes identificadas concordam; registrar quais |
| UNCERTAIN | Evidência incompleta ou divergente; registrar dúvida e não apresentar como certeza |

Modelo de registro factual:

```text
Fato/seção: localização de colecionável na fase indicada
Fonte: título da página, URL direta, seção, autor/site
Consultado em: AAAA-MM-DD
Finalidade: verificar caminho e condição de acesso
Confiança: SECONDARY / CROSS-CHECKED
Cross-check: outra página identificada, se realmente consultada
Licença/uso: referência factual; nenhuma prosa/arte redistribuída
Divergências: versões/condições conflitantes e decisão baseada em evidência
```

Se fontes discordarem, investigar versão/região/modo e documentar a divergência. Não escolher silenciosamente nem citar páginas não consultadas. Uma lista de URLs não substitui revisão factual. `guide.json` declara cobertura e revisão reais; páginas genéricas ou esboços não contam como guia completo.

## Autoria, copyright e assets

**Pesquisar não significa copiar.** Produzir prosa original, reorganizada para consulta durante gameplay, sintetizando fatos de várias fontes. Não copiar parágrafos, grandes trechos, walkthroughs completos ou fazer paráfrase superficial de uma única obra. Não criar cópia local de sites inteiros.

Verificar a licença **atual da página e do asset** antes de qualquer reutilização; o fato de ser wiki ou estar acessível não autoriza redistribuição. Fonte factual, texto e imagem podem ter direitos diferentes. Manter avisos/atribuições exigidos; não reclassificar terceiros como MIT.

Preferir mapas esquemáticos próprios, baseados em fatos de progressão, com legenda e orientação legíveis em 320×240/400×240. Exemplos: início → checkpoint → coletável → saída; cidade → rota → próxima cidade com ramificações; entrada → chave → miniboss → boss. Não copiar o layout artístico de mapas protegidos.

Antes de embutir qualquer asset em `ASSET_LICENSES.json`, registrar caminho, origem, autor, licença, URL, data de acesso, permissão de redistribuição/atribuição e SHA-256. Sem licença clara compatível: **não incluir no pacote**; manter referência ou criar esquema original. Não baixar imagens automaticamente da busca para o repositório. Converter em tiles/páginas leves com o Builder, respeitando os limites de memória e leitura lazy; a Pokédex também usa páginas/índices pequenos.

Para um asset externo, registrar também titular/copyright, URL da licença ou autorização e requisitos de atribuição no registro ou em documento local referenciado por `source`/`url`. Guardar a evidência de permissão antes da inclusão. O Builder verifica licença permitida, autoria/origem, SHA-256 e integridade da imagem; não consegue provar autorização jurídica. Os oito PNGs atuais são próprios e permanecem congelados.

## Pesquisa automatizada responsável

Automação futura deve respeitar termos, robots.txt, rate limits e direitos de cada fonte. Consultar páginas necessárias, com cache limitado e intervalos adequados; sem scraping agressivo ou espelhamento integral. Erros de acesso não autorizam contornar restrições. Não redistribuir snapshots de walkthroughs/arte sem permissão.

## Critérios para completar um guia

Estrutura adaptada ao jogo, páginas úteis e revisadas, índice/busca offline, fontes por seção, mapas quando úteis e checklist factual de 100%. Mario: cada fase/coletável/power-up/desbloqueável; Kart: cups/pistas/atalhos/peças/técnicas; Pokémon: rotas/cidades/encontros/itens/objetivos/pós-game/mecânicas; Zelda: dungeons/puzzles/bosses/itens/upgrades/coletáveis/side quests; Kirby: habilidades/fases/coletáveis/bosses/extras.

Passar Builder, testes, limites de UTF-8/tamanhos/paths/licenças e revisão editorial. Catalogação, guia parcial, guia completo e compatibilidade física continuam estados diferentes. Não certificar um jogo apenas porque seu Title ID foi reconhecido. Futuras contribuições seguem [ADDING_A_GAME.md](ADDING_A_GAME.md) e [CONTRIBUTING.md](../CONTRIBUTING.md).

## Pesquisa offline futura

Após diagnosticar e corrigir o crash, avaliar títulos, seções, locais, personagens, itens, bosses, colecionáveis e aliases PT-BR/originais como termos rastreáveis por página. Hoje o Builder indexa títulos, texto e keywords em UGS2; o core consulta prefixos em blocos limitados. Não prometer busca arbitrária por substring. Novos aliases devem caber nos limites atuais ou passar por revisão conjunta de Builder/core, com testes e reteste Old 3DS. Nenhum conteúdo ou índice novo é gerado nesta preparação.
