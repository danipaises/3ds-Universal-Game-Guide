# 3DS Universal Game Guide — 0.2.2-alpha

Projeto open source de guias offline para **Nintendo 3DS**, com **PT-BR primeiro**, plugin universal **CTRPluginFramework/.3gx** e **Luma3DS Plugin Loader**. Idioma do guia e região do jogo são independentes.

Repositório oficial: [danipaises/3ds-Universal-Game-Guide](https://github.com/danipaises/3ds-Universal-Game-Guide). **ALPHA — REAL HARDWARE TESTED: FULL PARTIAL PASS.** Pesquisa Offline e Configurações provocam ARM11 crash; aguardamos dumps separados.

| Teste físico | Ambiente | Resultado |
|---|---|---|
| #1 — 0.2.0-alpha | Super Mario 3D Land | ARM11 crash durante carregamento do plugin |
| #2 — 0.2.1-alpha MINIMAL | Old; Luma 13.1.1; Title ID 0004000000053F00 | **TESTED ON REAL HARDWARE — FAIL**, Data Abort / Write em CTRPF::__system_allocateHeaps |
| #3 — 0.2.2-alpha | Old Nintendo 3DS; Luma 13.1.1; Super Mario 3D Land / 0004000000053F00 | **MINIMAL-BOOT PASS; MINIMAL PASS; FULL PARTIAL PASS** |

A 0.2.1 trocou `UsePrivateMemory=true` por `false`, mantendo 5 MiB, mas falhou no reteste. O dump real foi conferido com o ELF exato: PC 07005B5C, LR 07005B50 e erro D8E007F7. O wrapper do CTRPF enviava o marcador de uma ABI posterior ao Luma 13.1.1, que o interpretava como handle inválido. O alocador então causava deliberadamente uma escrita em DEADC0DE. A 0.2.2 corrige a chamada sem aumentar memória ou mudar o layout do heap. [Auditoria e fontes](docs/HEAP_INITIALIZATION_AUDIT_0.2.2.md).

O pacote **UniversalGameGuide-PTBR-Hardware-Test-v0.2.2-alpha.zip** instala **MINIMAL-BOOT** primeiro. Essa variante testa o alocador/construtores do CTRPF sem inicializar gráficos ou menu: nenhuma notificação/hotkey é esperada. Após desligar, confira `3ds/UniversalGameGuide/logs/boot-stage.txt`. Somente depois de confirmar esse teste, troque para MINIMAL e finalmente FULL. [Instalação, resultados esperados e recuperação](HARDWARE_RETEST.md).

**Não usar Pesquisa Offline ou Configurações durante uso normal:** ambas crasharam em hardware. Nenhuma causa comum foi presumida. A expansão de guias está pausada até validar o FULL. [Política de pesquisa futura](docs/GUIDE_RESEARCH_POLICY.md).

O boot trace usa BSS antes do heap e só grava após FS funcionar: até 3 KiB/40 writes por execução. Logging normal do FULL continua OFF. Todas as variantes usam PRIVATE=false/5 MiB. SOURCE e símbolos ELF/MAP vêm em ZIPs separados; use sempre o ELF/MAP identificado pelo mesmo BUILD.json do binário instalado. Binários e pacotes anteriores foram preservados localmente.

Guias/IDs/assets permanecem congelados: 68 títulos, 211 IDs únicos/279 associações, 67 guias parciais, zero completos, um ausente. O perfil de teste contém seis pilotos reduzidos/78 páginas. Reconhecimento no catálogo não comprova compatibilidade física. [Cobertura](COVERAGE.md), [lacunas](CONTENT_GAPS.md), [estado](PROJECT_STATUS.md), [testes](TEST_REPORT.md), [changelog](CHANGELOG.md).

Para desenvolvimento:

```sh
python -m pip install -r requirements-dev.txt
python builder.py validate --lang pt-BR
python -m pytest -q
UGG_LSAN=0 bash scripts/test.sh
bash scripts/build-plugin.sh --clean
python scripts/verify_arm.py
python scripts/bundle_sources.py
python builder.py hardware-retest --lang pt-BR
python scripts/verify_release.py --hardware-retest
```

Use um ambiente virtual. O C++ próprio mantém `-Wall -Wextra -Werror`; `CXX=g++-14` seleciona GCC 14. CI Ubuntu 24.04 executa GCC 13/14, pytest, Builder, Ruff, core/boot ASan/UBSan, ARM e verificação da ABI nos ELF reais. [Actions](https://github.com/danipaises/3ds-Universal-Game-Guide/actions) e [build fixado](docs/BUILDING.md).

Código próprio MIT; dependências conservam licenças em [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) e no runtime. Sem ROMs, firmware, CIAs comerciais ou edição de saves. O SOURCE inclui o bundle upstream verificado, sem toolchain/binários/caches. O instalador não contém desenvolvimento nem sobrescreve configuração/progresso.

[Pre-release histórica v0.2.2-alpha](https://github.com/danipaises/3ds-Universal-Game-Guide/releases/tag/v0.2.2-alpha): baixe somente o Hardware-Test.zip. SOURCE e Debug-Symbols são para desenvolvimento. Os pacotes originais permanecem intactos, com rótulos anteriores ao teste. Boot/hotkey/UI/guia/retorno passaram no console relatado; Search e Settings falharam. Mapas, salvamento, HOME/sono e outras combinações ainda precisam de teste. [Procedência e hashes](docs/RELEASE_PROVENANCE_0.2.2.json). [Reportar crash](https://github.com/danipaises/3ds-Universal-Game-Guide/issues/new?template=crash-report.yml), [contribuir](CONTRIBUTING.md), [adicionar jogo](docs/ADDING_A_GAME.md).
