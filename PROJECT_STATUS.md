# Estado — 0.2.2-alpha — 2026-10-05

## DONE

- Hardware Test #2 registrado: 0.2.1-alpha MINIMAL, Old, Luma 13.1.1, Title ID 0004000000053F00, **TESTED ON REAL HARDWARE — FAIL**, Data Abort / Write em CTRPF::__system_allocateHeaps.
- Dump real conferido com ELF/3GX exatos; PC 07005B5C/LR 07005B50/Result D8E007F7. Baseline 0.2.1 e seus símbolos/pacotes preservados localmente. Dump bruto privado/ignorado, somente metadados necessários versionados.
- Causa identificada: CTRPF usa magic/R6 da ABI nova em Luma 13.1.1, que resolve magic como handle inválido; Fail grava DEADC0DE. Comparação primária pin/develop/fork Vapecord/Luma 13.1.1/v13.4/libctru documentada, sem inferir falta de RAM.
- Patch reproduzível em prepare_framework.py/CTRPF_FILESYSTEM.patch: flags zero no ABI legado aceito old/current; nonzero ainda ABI nova. PRIVATE=false/5MiB/layout inalterados.
- MINIMAL-BOOT vincula CRT/initLib/allocator do SDK, sem UI/GSP/HID/audio/fonts; bypass de aplicativos do sistema e eventos loader conforme fonte fixada. MINIMAL/FULL preservam startup existente.
- 44 testes Python/4 subtests passaram; core/boot ASan/UBSan e Builder PT-BR passaram. Ruff check/format e Bash syntax passaram. ELF ARM das três variantes construídos do zero, com DWARF/MAP.
- Inspeção de ELF: um único allocator forte por variante, wrapper/calling convention validado por instruções reais com modelos ABI explícitos, nenhuma UI no probe. Modelo baseline reproduz D8E007F7; não é teste do kernel físico.
- Hardware Test ZIP instala MINIMAL-BOOT, inclui MINIMAL/FULL em diagnostics; símbolos e SOURCE separados. Verificação local: 81 arquivos runtime, 80 hashes, 6 packs/78 páginas/22 IDs/45 tiles; 13 arquivos no ZIP de símbolos. Checksum/CRC/paths/identidade conferidos, sem config/progresso sobrescritos.
- Guias/Title IDs/assets congelados. Catálogo 68/211 IDs/279 associações, 67 guias parciais, zero completos, Tretta sem guia. Somente data/hardware-tests.json mudou nos dados.
- README/instruções/issue template atualizados: MINIMAL-BOOT não possui overlay ou hotkey. Nenhuma tag/release estável.
- Correção publicada em main no commit fc81f1848c242deae97e49b23113ff9a4fd63310; GitHub Actions real [37362312465](https://github.com/danipaises/3ds-Universal-Game-Guide/actions/runs/37362312465) PASS em GCC 13/14 e ARM/pacotes. Logs/artifacts consultados; os três 3GX/ELF/MAP do CI são idênticos aos locais. Auditoria antes de commit: 2.476 candidatos, nenhum segredo/arquivo proibido encontrado.

## DONE — resultado físico #3

- **0.2.2-alpha REAL HARDWARE TESTED**: Old Nintendo 3DS / Luma 13.1.1 / Super Mario 3D Land, Title ID 0004000000053F00. MINIMAL-BOOT PASS; MINIMAL PASS; FULL PARTIAL PASS.
- Boot, hotkey, game detection, main UI, guia, navegação básica e retorno ao jogo passaram no console relatado. Offline Search e Settings causam ARM11 crash, registrados separadamente em data/hardware-tests.json.
- Os três ZIPs 0.2.2 foram recuperados do CI e conferidos com os hashes da entrega anterior; SOURCE coincide com o commit e3b78dc. Nenhum plugin foi substituído. Procedência em docs/RELEASE_PROVENANCE_0.2.2.json.

## DONE — Fase A

- Pre-release histórica [v0.2.2-alpha](https://github.com/danipaises/3ds-Universal-Game-Guide/releases/tag/v0.2.2-alpha) CREATED, pre-release YES, tag e3b78dc. Quatro assets baixados após upload e conferidos por SHA-256; nenhum foi regenerado.
- docs/GUIDE_RESEARCH_POLICY.md criada: PT-BR primeiro, fontes/confiança/rastreabilidade/licenças/prosa própria/mapas esquemáticos, expansão condicionada à aprovação física do FULL.
- Automação futura implementada com tags v*, testes/build e criação real de Release via GitHub CLI, conteúdos write apenas no publish. Não substitui assets existentes.
- BUILD.json schema 2 identifica commit/versão/variante/toolchain/dependências/patch/hashes e CI-REBUILT. Publicação verifica SOURCE inteiro contra commit e proíbe árvore suja ou símbolos misturados.
- Ferramenta atual de simbolização exige também MAP e SHA do plugin instalado; pacote histórico mantém ferramenta original intacta.

## IN PROGRESS

- Checks locais concluídos: 50 pytest/8 subtests, Builder/Ruff/actionlint, core/boot ASan/UBSan, build limpo ARM, verificação ARM/pacotes PASS. CI da alteração será consultado após push.

## BLOCKED — diagnóstico dos crashes

- Dump A de Offline Search e dump B de Settings ainda não fornecidos. A identidade do FULL instalado precisa de confirmação antes de simbolizar. Não assumir causas comuns nem alterar runtime ao acaso.
- Sem console físico conectado nesta estação; resultados reais acima são do usuário. LSAN sob ptrace continua indisponível; ASan/UBSan permanecem ativos.

## TODO / NEEDS HARDWARE TEST

- Receber dumps/BUILD.json/hash instalado; confirmar trio FULL, analisar cada exception/PC/LR/SP/stack separadamente, depois corrigir e adicionar regressões.
- Só então preparar 0.2.3-alpha e testar checklist completa incluindo Search/Settings/maps e retorno ao jogo. VERSION continua 0.2.2-alpha.
- Guia, Title IDs e assets congelados. Política editorial não autoriza expansão nesta etapa. Nenhuma declaração de estabilidade ou FULL PASS.
