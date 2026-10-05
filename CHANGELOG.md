# Changelog

## 0.2.2-alpha — 2026-10-05 — NEEDS HARDWARE RETEST

- Teste físico #2 documentado: 0.2.1 MINIMAL, Old/Luma 13.1.1, FAIL em CTRPF::__system_allocateHeaps. Dump real simbolizado com ELF exato.
- Corrige svcMapProcessMemoryEx do SDK: flags zero usa ABI legada aceita em Luma 13.1.1 e atual; flags não zero conserva magic/R6. Memória/layout permanecem PRIVATE=false/5MiB.
- MINIMAL-BOOT sem inicialização gráfica, com allocator/CRT do SDK e logging limitado; teste antes de MINIMAL/FULL.
- Três ELF/MAP/binários vinculados por BUILD.json, verificação da ABI nas instruções ARM reais e check de único allocator. Pacotes/source/símbolos separados; dumps privados ignorados.
- Nenhuma expansão de guia/ID/asset, nenhuma release estável. 0.2.2 Não testado em hardware real. Os status “aguarda reteste” da 0.2.1 abaixo são históricos; o teste #2 agora é FAIL.

## 0.2.1-alpha — 2026-10-05 — NEEDS HARDWARE RETEST

- Registra hardware test #1: 0.2.0-alpha encontrou default.3gx, mas Super Mario 3D Land crashou com exception ARM11 ao iniciar. Overlay/hotkey/guias não foram testados. Modelo/Luma/Title ID/dump não fornecidos.
- **UsePrivateMemory true → false**, no .plgInfo e conferido no bit 8 do header 3GX de ambos os binários. Primeira recompilação limpa foi feita com somente essa alteração; depois foram reconstruídos SDK e variantes com diagnóstico. Não reutilizamos/renomeamos o binário anterior como correção.
- **MemorySize mantido em 5MiB**, sem aumento. É tamanho do bloco loader, incluindo executável/BSS e heap. Converter suporta 2/5/10 MiB. CTRPF reserva ~676 KiB para framebuffers, 8 KiB para hooks e 1 MiB para seu heap; 2 MiB deixam margem insuficiente para FULL, que exige mais 1 MiB livre antes do guia. A medição física de pico continua pendente; MINIMAL mantém 5 MiB para comparar o mesmo startup e uma única estratégia de mapeamento.
- Serviço SD/HID/shared font/CSND usa IPC/handles/mapas de memória fornecidos pelo sistema; não foi encontrada dependência UGG de PRIVATE nem inicialização de soc/httpc. acInit do framework abre o serviço AC, mas não cria sockets nem downloads. Essa revisão de fonte não comprova funcionamento em hardware.
- Cria **MINIMAL** independente do core de guias: somente startup CTRPF, Title ID, indicação, overlay simples, B para voltar e marcador de boot. FULL preserva recursos existentes e adiciona checkpoints de catálogo/guia/busca/mapa.
- Boot trace em BSS desde __entrypoint; persiste após fsInit via APIs oficiais libctru. Limitado a 3 KiB/40 writes, sem SD antes de FS, sem gravação repetida por frame e sem alterar config/save. É ligado exclusivamente no par de binários de reteste; Debug Logging continua OFF no FULL.
- Preserva .elf com DWARF do código próprio/SDK e .map de cada variante. O ZIP de símbolos fica separado do instalador. BUILD.json associa hashes de ELF/MAP/3GX; parser próprio valida dumps Luma 1.x/ARM11 e rotula stack como candidatos.
- Builder ganha hardware-retest; instala MINIMAL primeiro e inclui variantes em diagnostics. SOURCE separado; artifacts de compilação e símbolos não entram no SOURCE. CI produz teste, símbolos e SOURCE, com verificação local dos arquivos.
- **Nenhum guia, Title ID ou imagem foi expandido.** Mantidos seis pilotos/78 páginas no teste, dados/fontes existentes preservados. Pausa, HOME, sono e respostas ao loader mantidos; patch de SDK somente acrescenta checkpoints às etapas existentes.
- Importação no repositório oficial danipaises/3ds-Universal-Game-Guide. Corrige State::get/toggle para GCC 14 com ponteiros explícitos/máscara unsigned, mantendo -Werror; CI Ubuntu 24.04 usa GCC 13/14 e pytest. Artifacts candidatos têm commit no nome, pois o FULL recompilado difere do FULL já entregue para reteste; nenhum binário local anterior foi substituído e não houve release estável.

Status não é “resolvido”: **TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD (0.2.0-alpha); 0.2.1-alpha NEEDS HARDWARE RETEST**.
