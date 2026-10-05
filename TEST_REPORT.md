# Validação — 0.2.2-alpha — 2026-10-05

**0.2.1-alpha MINIMAL: TESTED ON REAL HARDWARE — RESULT: FAIL**, Old/Luma 13.1.1, Title ID 0004000000053F00. **0.2.2-alpha: NEEDS HARDWARE RETEST / Não testado em hardware real.**

| Verificação | Resultado observado |
|---|---|
| Dump físico #2 | Parser bounded/addr2line ARM executados com ELF exato. PC 07005B5C → Fail/allocateHeaps.cpp:16/51, LR 07005B50 → linha 50. R0 D8E007F7 é invalid handle; PC store aponta para DEADC0DE. Dump privado preservado. |
| Python pytest | **44 passed, 4 subtests passed, 0 failed**, 18,95 s, build/022-pytest.log. Modelos ABI, identidade, catálogo, corrupção, source sem dump/cache, busca/state/pack e links reais. |
| Builder validate | **PASS**: 68 jogos, 211 IDs únicos/279 associações, 67 guias/2.151 páginas, 9 mapas; Tretta sem guia continua explícito. |
| Native C++ | **PASS**, GCC local 15.2.0, -Wall/-Wextra/-Werror. Core: 67 packs/2.151 páginas/IDs, UTF-8, lazy search, CRC, state e arquivos corrompidos; max single read 175.344 bytes. |
| ASan/UBSan | **PASS**, UGG_LSAN=0; core e boot normal/fs-fail/io-fail. Logger 3 KiB/40 writes, sem SD antes de FS; fs-fail zero writes, io-fail um write e interrupção. Teste de stubs, não SD físico. |
| Lint | **PASS** Ruff check/format de 22 arquivos Python; Bash syntax build/test. Não executado ClangFormat/actionlint nesta revisão. |
| ARM | **PASS**, SDK/libraries e três ELF recompilados do zero no digest devkitPro fixado. C++ próprio mantém -Werror; não foi silenciado maybe-uninitialized. |
| MINIMAL-BOOT | 7.800 text + 528 data + 7.832 BSS = 16.160 bytes de seções, 12.659 bytes no .3gx. Sem símbolos de ScreenImpl/OSDImpl/PluginMenu/Font/gspInit/ncsndInit. Mantém allocator/stack_adjust/syscalls do SDK; não testa a UI. |
| MINIMAL / FULL | 221.044 / 292.364 bytes de seções; .3gx 286.082 / 378.572 bytes. Headers todos PRIVATE=false / 5MiB. DWARF e MAP correspondentes preservados. |
| Wrapper/allocator | **PASS**, verify_arm.py verifica os ELF reais: 1 allocator forte por variante, 12 casos ABI (0/1 flags × old/current × 3 variantes), registros preservados. Baseline 0.2.1 dá D8E007F7 no modelo old. É modelo de SVC, não emulador 3DS/kernel/hardware. |
| Pacotes | **PASS** verify_release.py: 81 arquivos/80 hashes no SD ZIP, 6 packs/78 páginas/22 IDs/4.963 registros de busca/45 tiles; 13 arquivos no ZIP de símbolos; SOURCE separado sem ELF/MAP/3GX/objetos/raw dumps. Checksums/CRC/paths e manifest conferidos. |
| Conteúdo | Git diff de guides/assets/data só aponta hardware-tests.json; nenhum guia/ID/asset expandido. COVERAGE/CONTENT_GAPS somente refletem versão/status novos. |
| GitHub Actions 0.2.2 | **Ainda não consultado nesta revisão local.** O PASS da 0.2.1 não é evidência do commit novo. |

Log native: build/022-native-tests.log. Build limpo: build/022-arm-build-final.log. Instruções/modelos: build/arm-verification.json. Pacotes: build/release-verification.json. Toolchain e upstream continuam fixados em data/dependencies.lock.json; comparações primárias e limites em [auditoria](docs/HEAP_INITIALIZATION_AUDIT_0.2.2.md).

Hashes .3gx desta candidata local:

```text
MINIMAL-BOOT 7167f564c2ed90c08d09ee8b35654e3ddabf34801e2192590b3f5d82afe1405a
MINIMAL      ec3ab2ad151710d08cbef4ae579e36c4dc7be560deb8a532a6170c2c156fc238
FULL         ea96f45a5f870f1e9ba0b3916a177b88be6794ed82e9ba387bc28fb358b0d702
```

A baseline original 0.2.1 continua em build/021-baseline; ZIPs antigos dist não foram substituídos. MINIMAL original ad4ddcb8…/ELF 35112cdb… é o par usado na simbolização #2. Não misture ELF de outra versão/compilação. No GitHub, artifacts candidatos recebem sufixo ci-commit; podem diferir de hashes locais mesmo com fontes equivalentes, devendo conservar seu próprio BUILD.json.

Tentativas iniciais desta revisão encontraram: argumento nullptr em SVC u32, dependência indireta UI causando entrypoint duplicado no probe, fixture de pacote sem os documentos recém-linkados e tamanho zero de símbolos assembly sem .size. Todos foram corrigidos e os checks acima reexecutados; essas tentativas falhas não contam como sucesso. Não se removeu -Werror nem a validação de links para fazê-los passar.

Sem teste de overlay em emulador e sem acesso físico local. A causa do erro #2 foi demonstrada na ABI e a chamada candidata foi corrigida, mas **não marcar crash como resolvido** antes do reteste [MINIMAL-BOOT → MINIMAL → FULL](HARDWARE_RETEST.md). [Histórico 0.2.1](docs/history/TEST_REPORT-0.2.1.md).
