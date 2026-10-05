# Reconstruir

A distribuição já inclui `default.3gx`; estas etapas são para contribuidores. Requisitos: Linux ou WSL2, Python 3.11+, pip, CMake, G++ e Docker. Nada dessas ferramentas precisa ser instalado pelo usuário do console.

Clone o [repositório oficial](https://github.com/danipaises/3ds-Universal-Game-Guide) e trabalhe diretamente na raiz. Instale `requirements-dev.txt` em um ambiente virtual e execute `python -m pytest -q`, `python builder.py validate --lang pt-BR` e `UGG_LSAN=0 bash scripts/test.sh`. Para GCC 14, use `CXX=g++-14 UGG_LSAN=0 bash scripts/test.sh`. CXX seleciona o compilador sem remover warnings ou -Werror; ASan/UBSan permanecem ativos. Pytest coleta somente tests/, evitando cópias de snapshots em research/. Os jobs PC do CI exercitam GCC 13 e 14 em Ubuntu 24.04 antes do build ARM. Os símbolos ELF/MAP são artifacts de desenvolvimento, nunca arquivos para o SD.

Para o reteste 0.2.1, instale `requirements-dev.txt`, execute `bash scripts/test.sh`, `bash scripts/build-plugin.sh --clean`, `python3 scripts/bundle_sources.py` e `python3 builder.py hardware-retest --lang pt-BR`. O resultado fica em `dist/`. `python3 scripts/verify_release.py --hardware-retest` confere o instalador, par de variantes, ELF/MAP/DWARF, checksums, índices/tiles e SOURCE separado. Ruff: `ruff check builder.py scripts tools tests` e `ruff format --check builder.py scripts tools tests`.

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

## Diagnóstico 0.2.1-alpha

O build agora gera default.3gx/default-full.3gx e default-minimal.3gx, com seus ELF/MAP. Ambos usam UsePrivateMemory=false/5MiB, conferidos também no header binário. Minimal compila minimal.cpp + boot.cpp, sem core.cpp/main.cpp. Cada variante tem objetos separados (build/ e build-minimal/). O SDK é o mesmo em ambas. --clean remove os dois conjuntos de objetos e relinka ambos; não renomeia builds antigas. O build conserva objetos SDK com G=-g, código próprio com -g3 e otimização -Os; nenhum strip no ELF. O conversor usa somente seções de runtime e símbolos .3gx, sem colocar DWARF no SD.

O pacote atual usa `python builder.py hardware-retest --lang pt-BR`, em vez de expandir a release comum. Ele instala MINIMAL e inclui FULL em diagnostics. Gere bundle_sources.py antes. Debug-Symbols-v0.2.1-alpha.zip mantém ELF/MAP/3GX/BUILD.json correspondentes; SOURCE não inclui nenhum desses binários/objetos. Todos os hashes ficam em SHA256SUMS.txt. Comandos gerais release/hardware-test continuam disponíveis para versões futuras e não substituem o reteste controlado.

Checkpoints do startup são aplicados somente via prepare_framework.py e publicados em docs/CTRPF_FILESYSTEM.patch. Fonte original, ordem de serviços, pause/HOME/sono e handshake do loader foram lidos novamente antes da instrumentação; esses protocolos não mudaram. Antes de fsInit só há BSS, sem alocação/log SD. Não chame o novo binário de estável: **NEEDS HARDWARE RETEST**. O relatório anterior de compilação determinística da 0.2.0 é histórico e não demonstra o resultado físico da 0.2.1.
