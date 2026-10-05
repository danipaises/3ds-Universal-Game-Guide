# 3DS Universal Game Guide — 0.2.1-alpha

Projeto open source de guias offline para **Nintendo 3DS**, com **PT-BR primeiro** e arquitetura multilíngue. Plugin universal **CTRPluginFramework/.3gx**, carregado pelo **Luma3DS Plugin Loader**. O idioma do guia independe da região do jogo.

Repositório oficial e fonte principal: [danipaises/3ds-Universal-Game-Guide](https://github.com/danipaises/3ds-Universal-Game-Guide). Issues e contribuições devem usar esse repositório. **ALPHA — NEEDS HARDWARE RETEST; estabilidade ainda não comprovada.**

**TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD (0.2.0-alpha).**

**0.2.1-alpha: NEEDS HARDWARE RETEST.** O primeiro teste real em Super Mario 3D Land produziu exception ARM11 antes do overlay. A troca UsePrivateMemory=false foi aplicada e recompilada; não há ainda resultado físico desta nova build.

**Hardware Test #1:** versão **0.2.0-alpha**, jogo **Super Mario 3D Land**, resultado **ARM11 crash durante carregamento do plugin**. Na 0.2.1-alpha, `UsePrivateMemory=true` passou a `UsePrivateMemory=false`, mantendo `MemorySize=5MiB`. Essa alteração aguarda reteste físico; o crash não está comprovadamente corrigido.

Este incremento trata apenas inicialização e diagnóstico. Nenhum guia foi expandido. Catálogo: 68 títulos, 211 IDs únicos/279 associações; 67 guias parciais, zero completos, um ausente. O teste usa os mesmos seis pilotos reduzidos/78 páginas. [Cobertura](../../COVERAGE.md) e [lacunas](../../CONTENT_GAPS.md) continuam explícitas.

Baixe **UniversalGameGuide-PTBR-Hardware-Test-v0.2.1-alpha.zip**, faça backup com o console desligado e extraia na raiz do SD. O plugin instalado é MINIMAL: Title ID, indicação, hotkey START + SELECT + A e B para voltar. Sem guias/config/catálogo/mapas/busca/progresso. Depois de iniciar corretamente, teste o FULL copiando diagnostics/default-full.3gx para luma/plugins/default.3gx. [Instruções completas e recuperação](../../HARDWARE_RETEST.md).

O boot trace grava somente em 3ds/UniversalGameGuide/logs/boot-stage.txt: checkpoints precoces em RAM, persistidos após fsInit, 3 KiB e até 40 writes/execução. O logging normal permanece OFF por padrão. Ambos usam SHARED/5 MiB. SOURCE, símbolos ELF/MAP e instalador vêm separados. [Changelog](../../CHANGELOG.md), [estado](../../PROJECT_STATUS.md), [testes](../../TEST_REPORT.md).

Para o reteste pendente, preserve o par já entregue: MINIMAL `ad4ddcb8…` e FULL `beb5127c…` (SHA-256 completos em [TEST_REPORT.md](../../TEST_REPORT.md)). A correção GCC em State::get/toggle passou nos testes, mas recompilar o FULL gera outro binário: o primeiro CI produziu `acb8c084…`. MINIMAL manteve o hash original. A memória e o startup não foram alterados. Artifacts do CI recebem `-ci-<commit>` no nome do ZIP e **não substituem o par entregue para reteste**. Sempre use ELF/MAP do mesmo pacote de símbolos do binário testado.

Para contribuir, consulte [CONTRIBUTING](../../CONTRIBUTING.md), [ADDING_A_GAME](../../docs/ADDING_A_GAME.md) e [build fixado](../../docs/BUILDING.md). Código próprio MIT; CTRPF e demais dependências conservam suas licenças em THIRD_PARTY_NOTICES.md/docs/licenses e no runtime. Sem ROMs, firmware, CIAs comerciais ou alterações de saves. Interface/retomada continuam pendentes de reteste.

Comandos internos:

```sh
python builder.py validate --lang pt-BR
python -m pytest -q
UGG_LSAN=0 UGG_PYTHON=.venv/bin/python bash scripts/test.sh
bash scripts/build-plugin.sh --clean
python scripts/bundle_sources.py
python builder.py hardware-retest --lang pt-BR
python scripts/verify_release.py --hardware-retest
```

Instale `requirements-dev.txt` em um ambiente virtual antes dos testes. `scripts/test.sh` aceita `CXX=g++-14`; mantém `-Wall -Wextra -Werror` e ASan/UBSan. O workflow de pushes/PRs usa Ubuntu 24.04 com GCC 13 e 14, valida PT-BR, executa pytest/Ruff/testes nativos e compila ARM antes de gerar artifacts. Confira os resultados em [GitHub Actions](https://github.com/danipaises/3ds-Universal-Game-Guide/actions); a evidência observada fica em [TEST_REPORT.md](../../TEST_REPORT.md).

O SOURCE contém os archives upstream fixados em third-party-source.zip; restaure-os conforme docs/BUILDING.md. No clone Git, o script de build obtém as dependências verificadas pelo lock. Debug-Symbols contém dois ELF/MAP/3GX associados por hashes e o parser diagnostics.py; mantenha-o no computador. O ZIP do SD não contém ELF/MAP nem desenvolvimento. Builds/dist/toolchains/caches não são versionados.

Nenhuma release estável é publicada nesta etapa. Uma futura **v0.2.1-alpha pre-release** depende da confirmação física de MINIMAL e FULL. Até lá, os artifacts de Actions são builds candidatos e não certificam funcionamento no console. Para reportar crash, use o [formulário de crash](https://github.com/danipaises/3ds-Universal-Game-Guide/issues/new?template=crash-report.yml); para solicitar conteúdo, use o [formulário de jogo](https://github.com/danipaises/3ds-Universal-Game-Guide/issues/new?template=game-request.yml).
