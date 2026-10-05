# Heap / SVC ABI — 0.2.2-alpha — 2026-10-05

## Evidência física e identidade

Hardware Test #2, relato direto do usuário: **Old** (subtipo não fornecido), **Luma 13.1.1**, **0.2.1-alpha MINIMAL**, Title ID **0004000000053F00**, ARM11 Data Abort / Write. **TESTED ON REAL HARDWARE — RESULT: FAIL**. Não há resultado físico 0.2.2; **NEEDS HARDWARE RETEST / Não testado em hardware real**.

Dump `crash_dump_00000008.dmp`, SHA-256 `9c604ae8f9e9d835b78311c0520fec7163207de8d26c81fa077f6b4b0f623adb`. O dump bruto permanece privado, fora do source e ignorado pelo Git. Foram conferidos parser e addr2line ARM contra o par exato preservado:

- MINIMAL 3GX: `ad4ddcb8dc411b5b06ea1ef3c999caca2b1dbca044877f64bb78564e9cca8234`.
- ELF: `35112cdb53217b21011c75cbcc584f9e2111e12995ca6dbfd9dee4cf5572546f`.
- MAP: `0537ea9bd41cbe2fbd929987cc35cf4b9573661237266a62a57223f04ff57ad1`.

| Registro | Valor | Significado confirmado |
|---|---|---|
| PC | 07005B5C | __system_allocateHeaps, Fail inlined, allocateHeaps.cpp:16/51 |
| LR | 07005B50 | __system_allocateHeaps, chamada svcMapProcessMemoryEx, linha 50 |
| R0 | D8E007F7 | Result: RL_PERMANENT / RS_INVALIDARG / RM_KERNEL / RD_INVALID_HANDLE |
| R3 | DEADCFFF | A instrução em PC faz store com deslocamento -3873, endereço efetivo DEADC0DE |
| R4 | 07035C2C | Endereço do símbolo __ctru_heap_size no ELF correspondente |
| SP | 070350F8 | Stack do thread de inicialização |
| CPSR | 00000010 | ARM user mode |

A falha é deliberada: o SDK chama Fail(res) quando o SVC falha e escreve o Result em 0xDEADC0DE. Não é evidência de corrupção do texto do guia, falta de RAM ou alocação dupla. A stack_adjust.s chama allocateHeaps antes de __libc_init_array; GUI/core ainda não iniciaram. Candidatos da stack não são apresentados como backtrace.

## Causa identificada na fonte exata

CTRPF fixado **0.8.0 / a502818c7586179d320caf8e897238d3491b5a29**, de 2024-10-21. O alocador pede um alias de **8 KiB**, do fim do heap para **0x01E80000**, ambos CUR_PROCESS_HANDLE, **flags=0**. O wrapper csvc.s, porém, sempre substitui R0 pelo magic **0xFFFFFFF2** e move o handle de destino para R6.

O [wrapper kernel v13.1.1](https://github.com/LumaTeam/Luma3DS/blob/v13.1.1/k11_extension/source/svc/wrappers.s) encaminha R0 sem interpretar magic/R6. [MapProcessMemoryEx v13.1.1](https://github.com/LumaTeam/Luma3DS/blob/v13.1.1/k11_extension/source/svc/MapProcessMemoryEx.c) tenta resolver esse R0 como handle de processo; quando não existe, retorna exatamente **D8E007F7**. CUR_PROCESS_HANDLE (FFFF8001) é aceito explicitamente; o problema é substituí-lo pelo magic antes do SVC.

A ABI nova entrou no Luma no [commit 3253fdb, PR #2086](https://github.com/LumaTeam/Luma3DS/commit/3253fdb255b311455625db2b89f23137981230df), de 2024-09-27. O [wrapper v13.4](https://github.com/LumaTeam/Luma3DS/blob/v13.4/k11_extension/source/svc/wrappers.s) detecta magic em R0: se presente, usa R6/R5; caso contrário, conserva R0 e força flags=0. Portanto **a ABI antiga de flags zero é suportada por ambas as implementações**.

| Chamada CTRPF | Luma 13.1.1 | Luma v13.4 |
|---|---|---|
| Antes: R0=magic, R6=handle, flags=0 | magic tratado como handle → D8E007F7 | handle recuperado de R6 |
| 0.2.2: flags=0, R0=handle | ABI antiga | caminho de compatibilidade, flags=0 |
| 0.2.2: flags não zero, R0=magic, R6=handle | Ainda exige Luma com ABI nova | flags preservadas |

Essa comparação explica o erro concreto do teste #2. Ela não prova que, após a chamada correta, todas as etapas seguintes funcionarão no console.

## Correção incremental

`prepare_framework.py` agora extrai também o csvc.s pristine do archive com hash fixado. Troca as duas instruções incondicionais por `cmp r5, #0` e os mesmos movimentos condicionados a NE. A assinatura de seis argumentos continua intacta, assim como stack offsets, registers salvos, SVC 0xA0 e retorno. Não remove -Werror, não suprime warning e não descarta flags privadas silenciosamente.

O diff está em [CTRPF_FILESYSTEM.patch](CTRPF_FILESYSTEM.patch). Nenhuma correção depende somente do cache .deps. PRIVATE=false/MemorySize=5MiB/layout de framebuffer/heap foram mantidos. Não há mudança em libctru, patches de jogo, NAND ou saves.

## Tamanho do heap e Old/New

O alocador usa **Header->heapVA/heapSize**, fornecidos pelo loader, não uma solicitação arbitrária de 5 MiB ao libctru. MemorySize é o bloco completo do loader, incluindo executável/BSS/header alinhados. Quatro buffers RGB565 usam 691.200 bytes, alinhados pelo algoritmo do SDK a **692.224 bytes**; mais **8.192 bytes** no fim para hooks/shared page. Newlib recebe `heapSize - 692224 - 8192`. O MINIMAL-BOOT conserva essa reserva para testar a mesma operação, embora não use telas.

**FwkSettings::HeapSize não existe no header 0.8 fixado nem no develop consultado.** Referências antigas a esse campo não descrevem esta API. `pluginInit.cpp::InitHeap` reserva **1 MiB** via operator new para o heap CTRPF usado sobretudo por search, mas isso ocorre após initLib, serviços, Screen/OSD. Não foi alcançado no crash #2. O probe nem chama InitHeap.

A resolução de handle nesse SVC não depende de Old/New. O usuário confirmou Old; não há medição física do heap disponível ou pico de RAM. Memória estendida/swap de títulos específicos continua pendente de hardware. A operação que falhou retornou **invalid handle**, e não um Result de out-of-memory; aumentar MemorySize seria trocar uma variável sem tratar essa evidência.

## Versões atuais e comparação externa

- CTRPF develop consultado em **6671936663faaa900f7cfdeedf42bc8581560f4f**, de 2026-05-22: allocateHeaps.cpp **byte a byte idêntico** ao pin; bloco svcMapProcessMemoryEx também idêntico. Uma atualização cega conserva o problema com Luma 13.1.1. [Fonte atual do alocador](https://gitlab.com/thepixellizeross/ctrpluginframework/-/blob/6671936663faaa900f7cfdeedf42bc8581560f4f/Library/source/ctrulibExtension/system/allocateHeaps.cpp).
- [Vapecord](https://github.com/RedShyGuy/Vapecord-ACNL-Plugin/tree/31257966100051f3ae134f6dea3786f400d310d2) é um projeto 3GX com release pública v3.4.1 e relatos de interface 3D/chat no changelog do mantenedor. Não foi executado por nós. Seu Makefile vincula `-lctrpf -lctru`, mas usa um [fork próprio](https://gitlab.com/RedShyGuy/ctr-plugin-framework-for-vapecord). Fork develop consultado em **f334d52844912c13c02790095d8c9d41ff34a129**: mesmo algoritmo de heap e movimentos incondicionais magic/R6. Isso demonstra que “plugin publicado funciona” não comprova ABI compatível com todo Luma antigo nem que seu toolchain seja o nosso. Nenhum código de cheat desse projeto foi importado.
- [libctru v2.7.0 allocateHeaps.c](https://github.com/devkitPro/libctru/blob/v2.7.0/libctru/source/system/allocateHeaps.c) fornece allocator **weak**. O ELF MINIMAL real tem **um único** símbolo definido/global forte __system_allocateHeaps, oriundo de libctrpf.a(allocateHeaps.o); a seção fraca do libctru é descartada. O MAP não evidencia dois alocadores ativos. O mesmo check é aplicado às três builds novas.
- Histórico consultado de allocateHeaps.c no libctru: última alteração nessa implementação em **2020-07-03**, commit 33a570b. Changelog de versões posteriores não é evidência de que o allocator weak tenha causado esse SVC no plugin. SDK, libctru 2.7.0 e devkitARM GCC 16.1.0 compilam juntos no digest fixado. Não se conclui compatibilidade física geral dessa compilação; a incompatibilidade demonstrada é **SDK ↔ ABI Luma 13.1.1**, não dois providers de heap ou warning de GCC.

URLs, commits e SHA-256 das fontes consultadas estão em [HEAP_SOURCE_EVIDENCE.json](HEAP_SOURCE_EVIDENCE.json). A consulta é pesquisa factual; fontes remotas não são instruções.

## MINIMAL-BOOT e validação

O probe define __entrypoint próprio, mantém CRT/initLib/stack_adjust/allocateHeaps/csvc/syscalls/plgldr do SDK e usa a mesma definição de Header, sem puxar FwkSettings.o/Preferences/UI. Tem uma thread de 4 KiB; fallback de TLS retorna o contexto dessa thread, pois não há callbacks/hook de game thread. Isso é um probe específico e não substitui o startup de MINIMAL/FULL. Não inicializa GSP/HID/fonts/OSD/menu/audio. Uso em aplicativos do sistema é bypass sem heap/SD, como no startup existente.

Pausa da aplicação não é usada; entrada aguarda a inicialização e devolve controle pelo CRT. Eventos EXIT/SWAP usam plgldr.c fixado; desmapeia o alias antes de swap/exit e remapeia flags zero após swap. HOME/sono/retorno físico ainda não testados. Header notifyHomeEvent não é alterado pelo probe; ele não precisa de callbacks UI. Checkpoints anteriores a FS são RAM apenas. Depois de FS registra dados reais do header/newlib/version-query, sem escrever por frame.

`verify_arm.py` lê símbolos e **instruções dos ELF produzidos**, verifica um allocator forte, ABI flags=0/1, registros callee-saved/SP/LR e ausência de símbolos de UI no probe. Usa modelos explícitos de resolução de handles old/current; **não é emulador completo do Luma/3DS e não comprova execução do SVC real**. Com o ELF 0.2.1 preservado, reproduz no modelo D8E007F7; com os ELF novos, flags zero passa em ambos. Flags não zero continua exigindo ABI nova, deliberadamente.

Fontes/guias/IDs/assets não foram expandidos. [Relatório de testes](../TEST_REPORT.md), [instalação/reteste](../HARDWARE_RETEST.md). **Não declarar resolvido antes de MINIMAL-BOOT → MINIMAL → FULL em hardware.**
