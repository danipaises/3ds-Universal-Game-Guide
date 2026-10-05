# Estado — 0.2.1-alpha — 2026-10-05

## HARDWARE TEST #1 — FAIL

**TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD (0.2.0-alpha).**

Plugin Loader Enabled; default.3gx encontrado SIM; Super Mario 3D Land; ARM11 exception imediatamente ao iniciar; overlay NÃO; hotkey NÃO testada; guias NÃO testados. Fonte: relato direto do usuário. Modelo exato, Luma, Title ID/região e .dmp não fornecidos. Histórico estruturado em data/hardware-tests.json.

## DONE

- UsePrivateMemory=false aplicado. Primeira recompilação limpa somente dessa alteração preservada localmente como controle; fontes anteriores preservadas no SOURCE 0.2.0.
- MINIMAL próprio sem core/parser/config/guia, FULL com checkpoints; mesmo startup CTRPF e protocolo do loader, sem alteração de pausa/HOME/sono.
- Buffer boot 3 KiB/40 writes, BSS antes dos serviços e flush após fsInit; marcador separado do logging normal OFF. Não depende de PRIVATE/socket/HTTP.
- MemorySize 5 MiB mantido; análise de reservas documentada. Pico de RAM/hardware continua desconhecido.
- Símbolos DWARF/MAP de ambas as variantes e ferramenta de diagnóstico com identificação por hash. HARDWARE_RETEST.md, changelog e registro da falha real criados.
- Builder/CI para reteste, símbolos e SOURCE separados, sem sobrescrever config/progresso. Instalação inicial MINIMAL.
- 38 testes Python, core e três cenários de boot trace sob ASan/UBSan passaram. Ruff/ClangFormat/Bash/actionlint passaram.
- Duas reconstruções limpas produziram hashes idênticos nos dois 3GX/ELF/MAP. Simbolização com dump sintético resolveu PC/LR para linhas de boot.cpp; não houve análise do dump físico ainda ausente.
- Três ZIPs de reteste/símbolos/SOURCE gerados e verificados, incluindo header PRIVATE=false/5MiB/DWARF, CRCs/paths e checksums. Conteúdo permanece congelado: 2.363 arquivos editoriais/assets/catálogo iguais ao staging 0.2.0.
- Importação do SOURCE 0.2.1 conferida: árvore na raiz, sem pasta intermediária. Correção explícita de State::get/toggle aplicada, preservando -Werror, protocolo e configuração de memória.
- Repositório oficial definido: https://github.com/danipaises/3ds-Universal-Game-Guide. README e formulários de crash/jogo preparados; .gitignore cobre binários, caches, toolchains e build/dist.

## IN PROGRESS

- Validação para importação, commit/push em main e execução real do GitHub Actions, incluindo GCC 13/14 no Ubuntu 24.04. A conclusão externa será registrada após consultar os runs.
- Investigação da causa exata aguarda o reteste/dump; a candidata PRIVATE=false está compilada e entregue, sem declarar solução física.

## TODO

- Receber .dmp/foto/log e dados do teste #1; investigar PC/LR da build correspondente quando disponíveis.
- Reteste MINIMAL → FULL sem hotkey → overlay/catálogo → guia → busca → mapa. Identificar a primeira etapa divergente com evidência física.

## BLOCKED

- Não há acesso ao console físico nesta estação. O relato confirma a falha da build anterior, não valida o novo binário.
- Sem dump original, impossível identificar agora a instrução/módulo exatos do primeiro crash.
- LeakSanitizer indisponível sob ptrace; core usa ASan/UBSan com UGG_LSAN=0. Jev doctor não fornece ready/mock estruturados nesta versão; integração não declarada validada.

## NEEDS HARDWARE RETEST

**0.2.1-alpha: NEEDS HARDWARE RETEST.** Não chamar crash de resolvido por compilar. Old/New, memória estendida, startup, touch, hotkey, pausa/retorno, HOME/sono, SD e interface pendentes.

## CONTENT PAUSED

Guias, Title IDs e assets congelados durante esta correção. 67 parciais, zero completos, Tretta sem guia/ID-base; conteúdo e lacunas da etapa anterior preservados. Nenhuma compatibilidade física inferida pelo catálogo.
