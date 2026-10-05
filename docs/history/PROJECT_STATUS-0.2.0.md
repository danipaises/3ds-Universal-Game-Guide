> Histórico anterior ao teste #1. O resultado real posterior é CRASH ON PLUGIN LOAD; [estado atual](../../PROJECT_STATUS.md).

# Estado da etapa 2 — 0.2.0-alpha

## DONE

- SOURCE/PTBR oficiais preservados, extraídos e auditados; 1.604 arquivos próprios coincidentes, sem recomeçar a arquitetura. Baseline de 17 testes/core/ARM executada antes das mudanças.
- Incrementos do plugin: logging OFF com buffer de 4 KiB, diagnóstico, configuração Touch/lembrar página, bypass R antes de gráficos, liberação de páginas ao fechar e guarda de headroom newlib.
- Leitor UGT1/UGG1/UGS2/UGI1/UGP2 preservado. UGC1 lido/UGC2 escrito; migração do progresso 0.1 por slug e fingerprint. Erros desconhecido/catálogo/guia ausente/corrompido diferenciados; consulta de existência fora do loop de frames; teclado de busca limitado e X no menu/índice. Hotkeys impossíveis com direções opostas são rejeitadas.
- Primeiro Hardware-Test reduzido criado antes da expansão; perfil final com seis guias, 78 páginas e estado separado. HARDWARE_TEST.md e checklist físico preparados, todos ainda pendentes de execução.
- Pilotos ampliados: Mario 79 páginas/159 localizações em 53 fases; X/Y 843 páginas cada, encontros por área e equipes/níveis de oito ginásios/Liga; Ocarina 36 páginas de roteiro/seções; Kirby 54 páginas com coleta das 35 fases; Dark Moon 52 páginas, missões, Boos e 13 gemas da primeira mansão.
- Outros 61 títulos identificáveis possuem quatro páginas próprias de referência inicial cada. **67 parciais, zero completos, um ausente.** COVERAGE.md e CONTENT_GAPS.md gerados automaticamente, sem inflar completude.
- 279 associações/211 IDs rechecados em snapshots com hash. 166 cross-checked, 112 single-source, um rótulo CHN pendente. Tretta sem ID-base, sem IDs inventados.
- Oito PNGs próprios/nove mapas por jogo com autoria, licença, hashes, tiles e zoom; sem arte não licenciada. Novos mapas inspecionados visualmente.
- Builder valida encoding, caminhos, limites, imagens, seções/revisão, idioma, links, migração e conteúdo do pacote. Runtime separado do SOURCE; configuração/progresso existentes não vêm no instalador.
- 31 testes Python, core ASan/UBSan de 67 packs/2.151 páginas, Ruff/ClangFormat/Bash e actionlint passaram. Duas reconstruções ARM completas e reconstrução em SOURCE extraído geraram o mesmo .3gx.
- CI preparado para PR, links, build ARM e três artifacts de release; tag conferida contra VERSION. Não houve execução no GitHub.
- Três ZIPs locais gerados e conferidos por hashes/CRCs/vínculos; instalador completo aproximadamente 1,53 MiB, teste 0,48 MiB. SOURCE reconstruído em diretório vazio com o mesmo hash ARM. Checksums em dist/SHA256SUMS.txt.

## IN PROGRESS

- Conteúdo detalhado e revisão dos 67 guias parciais. As lacunas específicas de cada jogo estão em CONTENT_GAPS.md/guide.json; nenhuma é declarada concluída por existir um arquivo.
- Teste físico e matriz de compatibilidade por modelo/título/região.

## TODO

- Mario: Special 2–8, Mystery Boxes, walkthrough entre medalhas e revisão de 100%.
- X/Y: TMs/HMs/Mega Stones/itens completos, puzzles, movesets/treinadores comuns, Friend Safari/breeding/tutors e formas/eventos.
- Ocarina: todas as salas/chaves, 36 Heart Pieces, 100 Skulltulas, Great Fairies/upgrades/trocas e Master Quest.
- Kirby: percursos completos, padrões/DX/True Arena/Dededetour e todas as entradas dos 256 Keychains.
- Dark Moon: outras 52 gemas, salas/puzzles/chefes, upgrades/três estrelas e coleção ScareScraper.
- Expandir as 61 referências iniciais em walkthroughs/tabelas próprios de cada jogo; utilitários continuam como referências.
- Confirmar região CHN de Ocarina e ID-base de Tretta Lab; reforçar os 112 registros single-source.
- Validar novas distribuições com os dois ZIPs legais disponíveis juntos e SHA256SUMS.txt. Nunca incluir source no instalador do usuário.

## BLOCKED

- Nenhum Nintendo 3DS físico disponível. Não declarar compatibilidade ou estabilidade física.
- Sem repositório GitHub remoto informado para executar workflows/publicar release.
- LeakSanitizer bloqueado por ptrace; ASan/UBSan executados com UGG_LSAN=0.
- Integração Jev não declarada validada: doctor ready:true/mock:false não confirmado nesta estação; relatórios antigos permanecem históricos.

## NEEDS HARDWARE TEST

**NOT TESTED ON REAL HARDWARE.** Old 3DS/XL/2DS e New 3DS/XL/2DS XL: boot, bypass R, hotkey, touch/teclado, scroll/mapas/zoom, busca, spoilers, favoritos/progresso/migração, logging/diagnóstico, retorno, HOME/tampa, SD cheio/erro/perda de energia, fontes regionais e memória estendida/MODE3. O primeiro pacote de teste e as instruções estão preparados; nenhum desses resultados foi fingido.
