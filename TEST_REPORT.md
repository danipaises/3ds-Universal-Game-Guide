# Validação — 0.2.2-alpha — 2026-10-05

**REAL HARDWARE TESTED — FULL PARTIAL PASS**, relato direto do usuário: Old Nintendo 3DS / Luma3DS 13.1.1 / Super Mario 3D Land / `0004000000053F00`.

| Função física | Resultado |
|---|---|
| MINIMAL-BOOT | PASS |
| MINIMAL | PASS — boot, hotkey, UI, Title ID, B/retorno |
| FULL boot / hotkey / game detection / main UI / guide / navegação básica / retorno | PASS |
| Offline Search | **FAIL — ARM11 CRASH**; dump A pendente |
| Settings | **FAIL — ARM11 CRASH**; dump B pendente |
| FULL overall | **PARTIAL PASS** |
| Mapas / settings save / reabertura repetida / HOME / sono / swap | NOT TESTED ou não informado |

MINIMAL exibiu newlib heap **8.172.600 bytes** e boot log result **00000000**, conforme relato. A etiqueta de tela “NEEDS HARDWARE RETEST” é anterior ao teste. Não inferir RAM livre/configuração recebida pelo loader a partir desse valor; confirmar boot-stage/BUILD.json e hash instalado. Arquivos originais preservados: [procedência](docs/RELEASE_PROVENANCE_0.2.2.json). Nenhum dump dos dois novos crashes foi recebido; exception/access/PC/LR/SP e causas permanecem pendentes, sem stack trace inventado.

## Evidência automatizada anterior ao reteste

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
| GitHub Actions 0.2.2 | **PASS**, [run 37362312465](https://github.com/danipaises/3ds-Universal-Game-Guide/actions/runs/37362312465), commit fc81f1848c242deae97e49b23113ff9a4fd63310. GCC 13/14, Python/Builder/Ruff/core/boot ASan/UBSan, ARM/modelos ABI/pacotes/upload com success, consultados após conclusão. |

Log native: build/022-native-tests.log. Build limpo: build/022-arm-build-final.log. Instruções/modelos: build/arm-verification.json. Pacotes: build/release-verification.json. Toolchain e upstream continuam fixados em data/dependencies.lock.json; comparações primárias e limites em [auditoria](docs/HEAP_INITIALIZATION_AUDIT_0.2.2.md).

Hashes .3gx desta candidata local:

```text
MINIMAL-BOOT 7167f564c2ed90c08d09ee8b35654e3ddabf34801e2192590b3f5d82afe1405a
MINIMAL      ec3ab2ad151710d08cbef4ae579e36c4dc7be560deb8a532a6170c2c156fc238
FULL         ea96f45a5f870f1e9ba0b3916a177b88be6794ed82e9ba387bc28fb358b0d702
```

A baseline original 0.2.1 continua em build/021-baseline; ZIPs antigos dist não foram substituídos. MINIMAL original ad4ddcb8…/ELF 35112cdb… é o par usado na simbolização #2. Não misture ELF de outra versão/compilação. No GitHub, artifacts candidatos recebem sufixo ci-commit; podem diferir de hashes locais mesmo com fontes equivalentes, devendo conservar seu próprio BUILD.json.

Tentativas iniciais desta revisão encontraram: argumento nullptr em SVC u32, dependência indireta UI causando entrypoint duplicado no probe, fixture de pacote sem os documentos recém-linkados e tamanho zero de símbolos assembly sem .size. Todos foram corrigidos e os checks acima reexecutados; essas tentativas falhas não contam como sucesso. Não se removeu -Werror nem a validação de links para fazê-los passar.

Sem teste de overlay em emulador e sem acesso físico local. O teste #3 confirmou a inicialização das variantes, mas expôs crashes em Search e Settings. A correção da ABI não representa aprovação integral do FULL. [Coleta separada e checklist](HARDWARE_RETEST.md). [Histórico 0.2.1](docs/history/TEST_REPORT-0.2.1.md).

## Evidência do GitHub e reprodução

Logs reais e artifacts foram consultados/baixados. GCC 14: 44 passed/4 subtests, 23,84 s; GCC 13: 44 passed/4 subtests, 17,65 s. Native core/boot passa em ambos com -Werror/ASan/UBSan; o warning de State::get/toggle permanece corrigido. ARM job 111940504823 concluiu as três builds, verificação de instruções e pacotes.

As três combinações **3GX + ELF + MAP do CI são idênticas às locais por SHA-256**. Checksums externos dos artifacts também conferidos. Isso comprova reprodução nesses dois ambientes desta build, não funcionamento físico. [Registro da execução e comparação](docs/GITHUB_CI_0.2.2.json). Metadata do pacote no contêiner confirma libctru **2.7.0-1** e GCC ARM **16.1.0**; o header version.h não existe nessa instalação.

Antes do commit foram examinados 2.476 candidatos ao Git, sem arquivos gerados/raw dumps/chaves privadas ou padrões conhecidos de tokens. Apenas data/hardware-tests.json mudou entre guias/assets/dados. O push para main não usou force e não criou tag/release. Atualização posterior de documentação registra este run; seus commits não mudam binários e não substituem a evidência física. O reteste #3 foi posteriormente relatado acima.


## Fase A — Release histórica e infraestrutura — 2026-10-05

- **Python PASS: 50 passed, 8 subtests passed, 0 failed**, 18,90 s; build/phase-a-pytest.log. Inclui rejeição de símbolos misturados/MAP incorreto/hash instalado diferente, tag incompatível, SOURCE divergente, árvore suja e checksum/path inválido.
- **Native core/boot ASan/UBSan PASS**, GCC local 15.2.0, -Werror, UGG_LSAN=0. Core 67 packs/2.151 páginas; boot normal/fs-fail/io-fail 40/0/1 writes. build/phase-a-native.log.
- **Builder/lint PASS**: catálogo 68/211 IDs/279 associações/67 guias/2.151 páginas/9 mapas; Ruff check/format (24 arquivos), Bash syntax, actionlint 1.7.12 (SHA do archive oficial conferido).
- **ARM clean build PASS**: três variantes; compiler 16.1.0, pacotes devkitARM r68-1 / libctru 2.7.0-1 consultados com dkp-pacman. Todos os 3GX/ELF/MAP iguais por SHA-256 à baseline 0.2.2. verify_arm.py PASS; build/phase-a-arm.log / build/phase-a-verify-arm.log.
- **Pacotes CI-REBUILT PASS**: 81 arquivos/80 hashes, 6 packs/78 páginas/22 IDs/45 tiles; 13 arquivos de símbolos; SOURCE 2.484 arquivos incluindo BUILD.json schema 2. Local dirty=true registrado honestamente; esse pacote local não pode ser publicado pelo guard de tag. Verificação em build/phase-a-verify-release.log.
- **Release histórica CREATED**: [v0.2.2-alpha](https://github.com/danipaises/3ds-Universal-Game-Guide/releases/tag/v0.2.2-alpha), pre-release YES/draft NO/tag e3b78dc. Os quatro assets foram baixados após upload; todos os ZIPs passaram sha256sum --check. Originais não foram regenerados nem atualizados.
- Guias/assets/runtime C++/VERSION inalterados. Política de pesquisa criada e expansão pausada. Nenhum dump Search/Settings recebido; nenhuma causa/fix/0.2.3 alegada.

Primeira execução desta fase: um teste ainda exigia #2 como último resultado e foi atualizado para manter o FAIL histórico junto do PARTIAL PASS atual; coleta de toolchain inicialmente usou pacman ausente e foi corrigida para dkp-pacman constatado na imagem. Os checks afetados foram reexecutados com os resultados acima. CI desta alteração deve ser consultado após push; os checks locais não são declarados CI remoto.


CI do commit 2a7f392: PC PASS (50 pytest/8 subtests e core/boot ASan/UBSan em GCC 13/14, logs consultados), mas ARM job 112045802672 no run 37393949227 e job 112045846748 no smoke release 37393981406 falharam após linkar os três ELF: `build/arm-compiler-version.txt: No such file or directory`. O checkout limpo ARM ainda não tinha build/. Correção incremental: criar build/ antes da coleta de toolchain, sem mudar código/opções/binários. Novo CI é necessário; estes dois runs falhos não contam como aprovação.
