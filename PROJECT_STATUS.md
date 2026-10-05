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

## IN PROGRESS

- Revisão de arquivos/segredos antes de commit; publicar correção de source em main e consultar CI real. Ainda sem resultado CI novo nesta revisão local.

## TODO

- Teste físico controlado: MINIMAL-BOOT → MINIMAL → FULL. Conferir log novo/hash/BUILD.json; parar na primeira falha.
- Depois do boot: hotkey, pausa/retorno, touch/scroll/mapa, HOME/sono/exit/swap e Old/New/MODE3, com evidência física.

## BLOCKED

- Não há console físico conectado nesta estação; aprovação física da 0.2.2 depende do usuário. Isso não impede source/build/pacotes/testes de PC.
- LeakSanitizer sob ptrace continua indisponível; UGG_LSAN=0 mantém ASan/UBSan.
- Jev doctor da instalação disponível não fornece ready/mock estruturados; integração não declarada validada.

## NEEDS HARDWARE RETEST

**0.2.2-alpha: NEEDS HARDWARE RETEST. Não testado em hardware real.** A incompatibilidade da chamada foi corrigida e testada por fonte/instruções/modelos; o crash físico ainda não está comprovadamente resolvido. 0.2.0 e 0.2.1 são FAIL reais.

## CONTENT PAUSED

Nenhuma expansão de guias ou nova compatibilidade física declarada. Histórico anterior em docs/history; [auditoria](docs/HEAP_INITIALIZATION_AUDIT_0.2.2.md) e [testes](TEST_REPORT.md).
