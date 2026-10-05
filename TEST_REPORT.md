# Validação — 0.2.1-alpha — 2026-10-05

**TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD (0.2.0-alpha).**

**0.2.1-alpha: NEEDS HARDWARE RETEST.** Teste #1 informado pelo usuário: loader Enabled/default encontrado, Super Mario 3D Land, exception ARM11 imediatamente ao iniciar. Overlay/hotkey/guias NÃO executados; .dmp/modelo/Luma/ID não fornecidos. A instrução/módulo exatos da falha continuam desconhecidos.

| Verificação | Resultado observado |
|---|---|
| PRIVATE=false isolado | Primeira clean build alterou somente o YAML; controle local SHA 02034de71bef9f8f672dee0bd2d23cb921b6262fd6c28dbb6b7cafc6fa80f7a0. Não é o binário final e não foi testado fisicamente. |
| Python | **38 testes passando, zero falhando**, incluindo dumps sintéticos/formatos/corrupção/stack parcial e identidade ELF/3GX. /tmp/ugg-021-tests-final.log, 17,712 s. |
| Core C++ | ASan/UBSan, 67 packs/2.151 páginas/211 IDs; max single read 175.344 bytes. Sem alteração editorial. |
| Boot trace com FS stub | ASan/UBSan: normal cap 40 writes, fs-fail 0, io-fail 1 seguido de interrupção; sem escrita antes de FS, sem duplicar checkpoint por frame, limites e paths conferidos. Não é um teste de cartão SD. |
| ARM MINIMAL/FULL | SDK/libs e os dois plugins compilados do zero com toolchain fixado, sem flags PRIVATE no YAML ou nos headers binários. MemorySize 5MiB em ambos. FULL 378.516 bytes; MINIMAL 286.042 bytes. |
| Reprodutibilidade | Duas clean builds consecutivas: hashes de ambos os 3GX, ELF e MAP **idênticos**, mesmo host/imagem/fontes. Não certifica hosts futuros. |
| Símbolos | .debug_info e .debug_line presentes em ambos os ELF; MAP preservados. MINIMAL sem ugg::Guide/lookup vinculados. Ambos sem inicializadores soc/httpc/socket vinculados, confirmado com nm ARM. |
| Simbolização | Ferramenta executada com addr2line ARM e dump explicitamente **sintético**: PC/LR resolveram para UGGBootStage em boot.cpp:60/61. Não analisa nem reproduz o crash físico original. Stack é tratada como candidatos, não backtrace confirmado. |
| Congelamento de conteúdo | 2.363 arquivos de guias/assets/catálogo comparados byte a byte com o staging SOURCE 0.2.0 retido: iguais. Sem guias, mapas ou IDs adicionados. |
| Lint | Ruff check/format de 20 arquivos Python, ClangFormat do C++ próprio/stubs e Bash syntax passaram. Actionlint dos três workflows passou; shellcheck/pyflakes integrados desabilitados, Ruff/Bash separados. |
| Pacotes | **Passaram** verificação de hashes/CRC/paths/identidade: 80 arquivos/79 hashes internos, seis packs/78 páginas/22 IDs/45 tiles; MINIMAL instalado primeiro e FULL em diagnostics. Símbolos em ZIP separado (dez arquivos) e SOURCE sem 3GX/ELF/MAP/objetos. Config/progresso não são sobrescritos. Hashes externos em dist/SHA256SUMS.txt; relatórios de source serão regenerados após esta atualização. |
| GitHub | **PASS**, [run 37352375785](https://github.com/danipaises/3ds-Universal-Game-Guide/actions/runs/37352375785), commit a25023326132ec5a4b2d1fe1dfbe0d3e955db67c. GCC 13/14/Ubuntu 24.04, pytest/Builder/Ruff/native/ASan/UBSan/boot, ARM, pacotes e upload consultados; todos concluídos com success. |

LeakSanitizer não funciona sob ptrace nesta estação; `UGG_LSAN=0` desabilita somente LSan, mantendo ASan/UBSan. Não houve teste do overlay em emulador nesta revisão. Houve falha inicial de validação por links históricos movidos e uma fixture de pacote sem HARDWARE_RETEST.md; caminhos/fixture corrigidos e suite completa reexecutada. Essas tentativas não foram contadas como sucesso.

Hashes do par .3gx:

```text
MINIMAL ad4ddcb8dc411b5b06ea1ef3c999caca2b1dbca044877f64bb78564e9cca8234
FULL    beb5127cb9976de5a32a1815a053ff860b9926b5b1a5553191ef92dc395b0bbd
```

[Auditoria de startup/memória](docs/INITIALIZATION_AUDIT_0.2.1.md), [instruções/dumps/recuperação](HARDWARE_RETEST.md), [changelog](CHANGELOG.md), [histórico anterior ao teste #1](docs/history/TEST_REPORT-0.2.0.md).

## Validação da importação para GitHub

- `State::get()` e `State::toggle()` passaram a usar ponteiro explícito e máscara uint8_t com deslocamento unsigned, conforme revisão. `-Werror` permanece ativo. Compilador local: GCC 15.2.0. **GCC warning FIXED**, confirmado no GitHub com g++-14 (Ubuntu 14.2.0-4ubuntu2~24.04.1), job 111906142813, e g++-13 (13.3.0), job 111906142193. Ambos passaram core e boot sob ASan/UBSan, sem silenciar maybe-uninitialized.
- `python -m pytest -q`: **38 passed, 4 subtests passed**, zero falhando, 18,00 s. A primeira coleta incluiu cópias históricas em research/ e falhou; testpaths=tests corrige a seleção no pyproject.toml, incluído no SOURCE.
- Builder validate PT-BR: **PASS**, 68 jogos/211 IDs/279 associações/67 guias/2.151 páginas/9 mapas. Conteúdo não expandido; Tretta continua explicitamente sem guia.
- `UGG_LSAN=0 bash scripts/test.sh`: **PASS**, 38 testes Python, core C++ sob ASan/UBSan, boot normal/fs-fail/io-fail. Log local: build/github-import-native-tests.log. GCC local 15.2.0 manteve -Wall/-Wextra/-Werror.
- Ruff check/format, ClangFormat, actionlint e sintaxe Bash: **PASS**. Pytest 9.0.2 fixado em requirements-dev.txt; CXX permite reproduzir GCC 14.
- SOURCE original extraído para auditoria: SHA-256 b563e6a15c2065738a3394be26eac7e05bbf7d7cb3a8171cf723839c9a356163; nenhum arquivo de source ausente ou caminho inseguro. Antes das edições de importação, somente core.cpp diferia pela correção solicitada.
- Auditoria dos arquivos candidatos ao Git não encontrou arquivos proibidos, chaves privadas ou padrões de tokens conhecidos. Build/dist/binários/toolchains/caches/.env excluídos; nenhuma credencial foi lida para essa auditoria. Relatório local em build/import-security-audit.json.
- Os .3gx instaláveis já entregues **não foram recompilados ou substituídos localmente**. Seus hashes MINIMAL/FULL dentro do ZIP de reteste conferem com os registrados acima; UsePrivateMemory=false/MemorySize=5MiB preservados. Nenhuma release/tag criada nesta etapa.
- CI real: **38 passed, 4 subtests passed**, zero falhando em cada compilador; GCC 14 levou 22,78 s no pytest. Core: 67 packs/2.151 páginas, max single read 175.344 bytes; boot normal 40 writes/fs-fail 0/io-fail 1. Builder e lint também success. ARM-package (job 111906724832) concluiu build limpo, bundle, geração/verificação e upload em 1m44s.
- Artifacts do primeiro run baixados em build/github-ci/37352375785. Comparação: MINIMAL idêntico ao entregue; FULL recompilado **difere**, tem 378.532 bytes e SHA-256 **acb8c0849bbbd3e3d5fb93fa076295755a77484c5b6bfc7ccb9aaaab5c321efe**. Headers de ambos: PRIVATE=false, 5MiB. A correção de fonte solicitada alterou o resultado do build FULL; isso não comprova nem corrige o crash físico. Par original ad4ddcb8…/beb5127c… preservado para o reteste já planejado.
- Os próximos artifacts usam nome de ZIP `-ci-<commit>` para distinguir reconstruções do pacote já entregue. O pacote de símbolos acompanha o binário desse mesmo CI; não misture seus ELF/MAP com o FULL anterior. Nenhum ELF/MAP entrou no ZIP do SD.
- Comparação dos símbolos ARM dos ELF anterior/CI: somente State::get (48 → 56 bytes) e migrateState (748 → 752 bytes) têm tamanhos de função diferentes; nenhum símbolo de função foi adicionado/removido. Registro local: build/github-ci/37352375785/symbol-size-comparison.json. Isso documenta a diferença do build decorrente da correção, sem substituir teste físico.

O crash **não está comprovadamente resolvido**. Ausência de boot-stage pode indicar falha anterior a fsInit ou falha do SD; não permite apontar a etapa exata. É necessário reteste físico controlado MINIMAL → FULL → overlay/catálogo → guia → busca → mapa, com .dmp/PC/LR e identificação do binário. Pausa/retorno, Old/New/MODE3, GSP, touch, HOME/sono, SD e pico de memória continuam pendentes. Não chamar estes artifacts de release estável.
