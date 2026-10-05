# Reconstruir

A distribuição já inclui `default.3gx`; estas etapas são para contribuidores. Requisitos: Linux ou WSL2, Python 3.11+, pip, CMake, G++ e Docker. Nada dessas ferramentas precisa ser instalado pelo usuário do console.

Clone o [repositório oficial](https://github.com/danipaises/3ds-Universal-Game-Guide) e trabalhe diretamente na raiz. Instale `requirements-dev.txt` em um ambiente virtual e execute `python -m pytest -q`, `python builder.py validate --lang pt-BR` e `UGG_LSAN=0 bash scripts/test.sh`. Para GCC 14, use `CXX=g++-14 UGG_LSAN=0 bash scripts/test.sh`. CXX seleciona o compilador sem remover warnings ou -Werror; ASan/UBSan permanecem ativos. Pytest coleta somente tests/, evitando cópias de snapshots em research/. Os jobs PC do CI exercitam GCC 13 e 14 em Ubuntu 24.04 antes do build ARM. Os símbolos ELF/MAP são artifacts de desenvolvimento, nunca arquivos para o SD.

Para o reteste 0.2.2, instale `requirements-dev.txt`, execute `bash scripts/test.sh`, `bash scripts/build-plugin.sh --clean`, `python3 scripts/bundle_sources.py` e `python3 builder.py hardware-retest --lang pt-BR`. O resultado fica em `dist/`. `python3 scripts/verify_release.py --hardware-retest` confere o instalador, trio de variantes, ELF/MAP/DWARF, checksums, índices/tiles e SOURCE separado. Ruff: `ruff check builder.py scripts tools tests` e `ruff format --check builder.py scripts tools tests`.

O patch de build fixa os metadados de CTRPF em 0.8.0/a502818c, em vez de consultar o Git do diretório pai do archive. Assim o SDK não recebe a identidade do repositório do projeto. A macro COMPILE_DATE é fixada em `2026-10-04T00:00:00UTC`, a época de distribuição da 0.2, e não representa o relógio da máquina de build. Duas compilações locais consecutivas com as mesmas fontes/toolchain produziram o mesmo hash; isso não comprova todos os hosts nem um build limpo remoto.

A imagem devkitPro é fixada em `data/dependencies.lock.json`; não depende de uma tag latest em novas reconstruções. Downloads de fontes têm hash e commit. A compilação ARM é feita no mount `/work`, que evita problemas de espaços no caminho do workspace. O conversor nativo é executado no host após o ELF sair do contêiner, evitando diferenças de glibc entre host e imagem. A biblioteca CTRPF é construída sem LTO com o compilador GCC 16.1.0 constatado na imagem.

Use `bash scripts/build-plugin.sh --clean` para remover somente objetos/bibliotecas ARM gerados e recompilar o SDK, suas bibliotecas de áudio e o plugin. As fontes fixadas permanecem no cache. O ELF depende também de libctrpf.a e 3gx.ld: alterações nesses arquivos obrigam nova linkedição mesmo sem mudança em main.cpp. Não use make -B no SDK: esse alvo tenta clonar libcwav apesar da cópia fixada já presente.

`prepare_framework.py` reaplica uma derivação a partir do arquivo original verificado, preserva os demais arquivos e documenta o diff. Não faz `git pull`. `fetch_deps.py --offline` usa os arquivos presentes em `research/`; para reconstruir pelo bundle de fontes, extraia `archives/` do third-party-source.zip em `research/` primeiro. Symlinks e nomes de arquivo que escapem do destino são recusados.

O ZIP é determinístico para a mesma árvore de entrada e o mesmo executável; isso não prova que recompilações ARM em datas ou ambientes diferentes tenham hash idêntico. Metadados do framework e toolchain podem alterar o binário. O arquivo `build/third-party-source.zip` é normalizado para distribuição, mas registros de build local ficam fora do SD.

Para regenerar a Pokédex, execute `python3 scripts/fetch_data_sources.py pokemon` e `python3 scripts/generate_pokedex.py`. O downloader e o gerador conferem o lock de fontes; não aceitam silenciosamente CSVs alterados. Ele atualiza apenas páginas `dex-*` geradas; revise condições históricas antes de distribuir. Nunca importe flavor text ou sprites sem licença. `scripts/seed_pilots.py` é o registro de autoria inicial e recusa sobrescrever guias existentes.

O catálogo é importado com snapshots list_US/GB/JP/KR/TW do commit 5d9141a de hax0kartik/3dsdb e o XML público. Use `python3 scripts/fetch_data_sources.py catalog` antes de `python3 scripts/import_catalog.py`. O XML público é um endpoint mutável: se seu hash mudar, a restauração histórica será recusada, devendo-se obter o snapshot preservado ou auditar uma atualização explícita. Esses snapshots não são baixados implicitamente durante build normal. Evidências e hashes estão versionados. Não derivar um ID-base de update ou atribuir todas as regiões a uma entrada WLD.

## Pacotes e reprodução offline

`python builder.py hardware-test --lang pt-BR` cria seis guias reduzidos, com até 15 páginas por pack e estado de teste separado. `python builder.py release --lang pt-BR` gera os três ZIPs e dist/SHA256SUMS.txt. O plugin precisa estar compilado e o bundle upstream gerado antes. O SOURCE não inclui toolchain, caches, objetos ou binário .3gx.

O SOURCE conserva data/migrations/alpha-0.1.0-pt-BR.json: IDs e fingerprints do instalador oficial anterior. O Builder transforma esse registro em UGR1; não é necessário ter o ZIP antigo para reconstruir os instaladores atuais. Para refazer a auditoria de IDs, os snapshots públicos originais são necessários; confira os hashes antes de executar scripts/audit_title_ids.py.

## Diagnóstico 0.2.2-alpha

O build produz default-full.3gx (também default.3gx), default-minimal.3gx e default-minimal-boot.3gx, com três ELF/MAP distintos. Todos PRIVATE=false/5MiB. --clean remove objetos ARM/SDK e os três diretórios de objetos próprios. Cada variante conserva -g3/SDK G=-g; o conversor não copia DWARF para o SD.

MINIMAL/FULL conservam o startup CTRPF existente. MINIMAL-BOOT tem entrypoint próprio e somente Header/TLS de uma thread; vincula o CRT, initLib, allocator e wrapper do mesmo SDK, sem UI. A linkedição deixa de puxar FwkSettings.o/Preferences/ThreadEx. Confira a análise e os limites em [HEAP_INITIALIZATION_AUDIT_0.2.2.md](HEAP_INITIALIZATION_AUDIT_0.2.2.md).

Depois de compilar, rode `python scripts/verify_arm.py`. A ferramenta lê símbolos e instruções ARM reais dos três ELF, testa calling convention contra modelos explícitos old/current e rejeita UI no probe. Não é teste de kernel/hardware. Opcionalmente `--baseline-elf build/021-baseline/default-minimal.elf` reproduz no modelo a falha da build original preservada. Essa baseline privada não é necessária no CI nem vem no SOURCE.

Gere `bundle_sources.py`, `builder.py hardware-retest --lang pt-BR` e `verify_release.py --hardware-retest`. O ZIP SD instala MINIMAL-BOOT e mantém MINIMAL/FULL em diagnostics. Debug-Symbols-v0.2.2-alpha.zip contém três pares ELF/MAP/3GX associados por BUILD.json. SOURCE contém fontes e archives upstream separados; não contém binários, raw dumps, objetos ou toolchain. Config/progresso não são sobrescritos.

No CI, ZIPs ganham sufixo `-ci-<commit>` e SHA-256 externos novos, enquanto BUILD.json identifica os bytes internos. Não há promoção automática para release/tag. Sempre use os símbolos da build realmente instalada; versão igual não garante mesmo hash. A baseline 0.2.1 é histórica e falhou no teste físico #2, não é recomendada para instalação.

prepare_framework.py extrai fontes pristine verificadas e reaplica inclusive csvc.s, com diff versionado em CTRPF_FILESYSTEM.patch. Flags zero usam ABI legada, flags não zero continuam no protocolo novo; fonte kernel Luma 13.1.1/v13.4 foi consultada antes da mudança. Layout/memória/fluxos de MINIMAL/FULL não foram aumentados ou reorganizados. O probe trata eventos do loader conforme plgldr.c fixado, mas HOME/sono/swap/exit ainda precisam de hardware. Nada escreve no SD antes de FS e não se fazem writes por frame.

**0.2.1: TESTED ON REAL HARDWARE — FAIL em CTRPF::__system_allocateHeaps. 0.2.2: NEEDS HARDWARE RETEST; Não testado em hardware real.**
