# Política de pesquisa e autoria dos guias

## Condição para retomar conteúdo

A prioridade atual é estabilidade. A 0.2.2-alpha foi testada em Old Nintendo 3DS / Luma 13.1.1: MINIMAL-BOOT e MINIMAL PASS; FULL PARTIAL PASS, com crashes em Pesquisa Offline e Configurações. Não expandir guias agora. Retomar produção extensa somente após correções, regressões e teste físico que aprove FULL boot, reconhecimento, guia, busca, configurações, mapas e retorno ao jogo. Manter evidência por build/variante; CI não comprova experiência em hardware.

## Escopo editorial

Escrever primeiro em **pt-BR**, com português natural; preparar en-US e outros idiomas depois. Região do jogo e idioma do guia são independentes. Priorizar jogos nativos do 3DS das famílias Mario (Super Mario, Kart, Party, Mario & Luigi, Luigi's Mansion, Yoshi e derivados adequados), Pokémon, Zelda e Kirby existentes no catálogo. Aplicativos recebem referência funcional, não um walkthrough artificial.

Cada variante regional precisa de evidência identificável: jogo, região, Title ID, idioma do guia e game-id associado. Nunca presumir IDs iguais entre USA/EUR/JPN, inferir um ID-base a partir de update/DLC ou inventar versões. Dúvidas ficam NEEDS_VERIFICATION no TITLE_ID_AUDIT.md.

## Hierarquia e usos das fontes

1. Fontes oficiais: Nintendo Support, manuais eletrônicos, páginas Nintendo e Pokémon. Consultar primeiro para controles, terminologia, mecânicas, modos e recursos documentados. Confirmar plataforma/edição; diferenças de remake importam.
2. Fontes especializadas por franquia, para fatos ausentes nos manuais e confirmação cruzada.
3. StrategyWiki, GameFAQs e outras referências comunitárias como fontes secundárias. Nunca copiar walkthroughs ou mapas de autores sem licença/permissão apropriada.

| Franquia | Fontes especializadas | Uso prioritário |
|---|---|---|
| Mario | Super Mario Wiki; StrategyWiki; GameFAQs | Mundos/fases, Star Coins/Star Medals, inimigos, power-ups, saídas, desbloqueáveis, Kart/Party/RPG/Luigi/Yoshi |
| Pokémon | Bulbapedia; Serebii; StrategyWiki; GameFAQs | Bulbapedia: progressão, rotas/cidades, dungeons, ginásios/trials, história e itens. Serebii: encounters, níveis, Pokédex, evolução, moves/abilities, Megas, Z-Moves, lendários e pós-game |
| Zelda | Zelda Dungeon; Zelda Wiki; StrategyWiki; GameFAQs | Zelda Dungeon: dungeons, puzzles, bosses, colecionáveis, side quests, 100%. Zelda Wiki: itens/locais/mecânicas e diferenças entre versões |
| Kirby | WiKirby; StrategyWiki; GameFAQs | Fases, Copy Abilities, Sun Stones, Rare Keychains, Code Cubes, stickers, bosses, extras e desbloqueáveis |

Essa lista orienta a pesquisa; não concede licença de reprodução. Abrir a página relevante e verificar sua situação atual quando a pesquisa for retomada. Cruzar fatos importantes sempre que possível, especialmente dados numéricos de Pokémon e requisitos de 100%. Preservar nomes originais quando não houver tradução oficial adequada. Não inventar traduções oficiais.

## Rastreabilidade e confiança

Cada jogo mantém `guides/pt-BR/<game-id>/SOURCES.md`. Registrar fonte/autor, URL direta, título ou seção consultada, edição/plataforma, finalidade, data de consulta real e licença quando relevante. A interface offline pode omitir URLs longas; o repositório conserva a rastreabilidade.

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

## Pesquisa automatizada responsável

Automação futura deve respeitar termos, robots.txt, rate limits e direitos de cada fonte. Consultar páginas necessárias, com cache limitado e intervalos adequados; sem scraping agressivo ou espelhamento integral. Erros de acesso não autorizam contornar restrições. Não redistribuir snapshots de walkthroughs/arte sem permissão.

## Critérios para completar um guia

Estrutura adaptada ao jogo, páginas úteis e revisadas, índice/busca offline, fontes por seção, mapas quando úteis e checklist factual de 100%. Mario: cada fase/coletável/power-up/desbloqueável; Kart: cups/pistas/atalhos/peças/técnicas; Pokémon: rotas/cidades/encontros/itens/objetivos/pós-game/mecânicas; Zelda: dungeons/puzzles/bosses/itens/upgrades/coletáveis/side quests; Kirby: habilidades/fases/coletáveis/bosses/extras.

Passar Builder, testes, limites de UTF-8/tamanhos/paths/licenças e revisão editorial. Catalogação, guia parcial, guia completo e compatibilidade física continuam estados diferentes. Não certificar um jogo apenas porque seu Title ID foi reconhecido. Futuras contribuições seguem [ADDING_A_GAME.md](ADDING_A_GAME.md) e [CONTRIBUTING.md](../CONTRIBUTING.md).
