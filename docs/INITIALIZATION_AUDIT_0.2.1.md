# Auditoria do crash/startup — 2026-10-05

> Documento histórico, anterior ao dump #2. A 0.2.1 falhou em hardware. A causa comprovada e a candidata 0.2.2 estão em [HEAP_INITIALIZATION_AUDIT_0.2.2.md](HEAP_INITIALIZATION_AUDIT_0.2.2.md).

0.2.0-alpha: **TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD**. 0.2.1-alpha: **NEEDS HARDWARE RETEST**. Fonte física: relato do usuário em Super Mario 3D Land, sem dump fornecido. A etapa exata antes de overlay é desconhecida; não declaramos causa comprovada.

## Mudança controlada

Primeiro alteramos somente UsePrivateMemory true→false e recompilamos SDK/dependências/plugin com --clean. Binário de controle local: 02034de71bef9f8f672dee0bd2d23cb921b6262fd6c28dbb6b7cafc6fa80f7a0. Sua versão interna permanece 0.2.0; não é o binário final de entrega. Depois incrementamos SemVer para 0.2.1-alpha e adicionamos diagnóstico/variante minimal. Os novos plugins foram recompilados, não apenas renomeados.

O relato [Luma #2225](https://github.com/LumaTeam/Luma3DS/issues/2225) descreve PRIVATE=true causando crash em outros títulos mesmo com minimal, e desaparecimento da falha com false. Ele não testa nosso Mario/plugin/console. O [PR #2086](https://github.com/LumaTeam/Luma3DS/pull/2086) introduz PRIVATE para socket/HTTP compartilhar heap. O [memoryblock.c v13.4](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/memoryblock.c) usa a flag tanto no executável quanto no heap. Conferimos o bit 8 também no header 3GX final, não somente no YAML.

## PRIVATE e serviços

- Código UGG não depende de heap PRIVATE, não inicia soc/httpc, não cria sockets, não faz HTTP nem downloads. Os símbolos ARM dos dois ELF foram inspecionados: inicializadores de socket/HTTP ausentes.
- Startup CTRPF fixado mantém srv/ac/am/fs/HID/cfg/CSND/loader e GSP. FS usa IPC; HID/GSP/shared font/CSND mapeiam handles/shared blocks fornecidos pelo sistema, não fazem a operação socInit de compartilhar novamente nosso heap. acInit abre serviço AC e não significa abrir socket.
- __system_allocateHeaps do SDK mapeia duas páginas de hook usando flags 0, independente de PRIVATE; manter SHARED é consistente com esse caminho. Não reescrevemos alocador nem protocolo de eventos.
- Fonte, inicialização do SDK, patch genérico de font mapping e sua gestão de serviços permanecem no par minimal/full. Não alegar que MINIMAL elimina o CTRPF; ele elimina o core de guias. Marcadores distinguem entrada, heap/construtores, serviços, gráficos/fonte e main.
- Os checkpoints adicionados são reaplicados via prepare_framework.py a partir do archive fixado; docs/CTRPF_FILESYSTEM.patch é gerado, não editado apenas no cache .deps. Ordem de chamadas, pausa, game release, HOME, sono e respostas ao loader são preservadas.

## MemorySize

3gxtool fixado aceita 2/5/10 MiB. MemorySize é o bloco loader, não um limite só para texto ou só para heap. No FULL medimos 292.340 bytes (~285,5 KiB) de seções estáticas ARM; MINIMAL 221.036 bytes (~216 KiB). O arquivo .3gx contém também símbolos/metadados e tem tamanho diferente do espaço executável na RAM.

allocateHeaps.cpp reserva quatro framebuffers RGB565: 400x240x2x2 + 320x240x2x2 = 691.200 bytes, alinhados a **692.224 bytes** (~676 KiB), mais 8 KiB de hook/shared page. InitHeap ainda reserva 1.048.576 bytes para heap CTRPF. Com executável/BSS/header alinhados a ~288 KiB no FULL, um bloco 2 MiB teria só ~52 KiB antes de outras alocações, threads, fonte e páginas. O UGG exige **1 MiB de newlib livre** antes de abrir um guia. Logo, 2 MiB não satisfazem a arquitetura atual sem outras mudanças relevantes.

**Mantido 5 MiB em FULL e MINIMAL**, sem aumento, para isolar PRIVATE e manter startup comparável. Isso não prova que 5 MiB são mínimos para uma futura implementação mínima sem framework. Otimizar/remover reservas de search do SDK seria outra mudança, após estabilizar o reteste. Old 3DS continua prioritário, sem inferir disponibilidade física do heap. O logger/UI mostra getMemFree newlib, não RAM livre total. Pico real e modelos específicos dependem do reteste.

## Limites do diagnóstico

Entrypoint só registra em BSS (sem constructors, heap, FS ou printf). A primeira persistência exige fsInit e OpenArchive; um crash anterior não produz marker. Falha ao gravar desliga gravações seguintes; buffer/cap de writes verificados em stubs de PC, não SD físico. Antes de cada teste, arquive/remova o marker antigo. Ele não intercepta a exceção nem tenta gravar de um handler inseguro.

Se MINIMAL falhar, ainda não será problema de conteúdo: lookup/Guide do core não são vinculados nesse ELF. Se MINIMAL passar e FULL falhar, compare ações e checkpoint; não declare que a diferença causa o crash até correlacionar PC/LR/dump. Se PC estiver no loader/kernel/jogo, ELF do plugin não o simboliza. Stack varrida fornece candidatos, não um backtrace garantido.

Código de referência Luma v13.4 baixado do repositório oficial em 2026-10-05 para pesquisa: archive SHA-256 3df201f365d0e980fc78e5c1645f0fe9fc070edb8eaea06622a9c58b68d70aa7. Não incluído no runtime nem usado para instalar firmware. O Luma exato do usuário não foi informado. Demais fontes e instruções de dump estão em [HARDWARE_RETEST](../HARDWARE_RETEST.md).

O ELF de controle da 0.2.0 está preservado localmente em build/private-false-control/default.elf (nomes de funções, sem DWARF completo). Restaurar somente o bit PRIVATE do header do controle reproduziu SHA a1014ecf2f79c4666511b18291a51201175e7dd5e8d9609e7cd732d9eefafe8e da distribuição 0.2.0; esse controle permite referência de endereços antigos quando chegar o dump. Nenhum binário antigo reconstruído dessa forma é instalado ou distribuído no reteste. Os ELF/MAP entregues em Debug-Symbols são somente 0.2.1 e não devem ser confundidos com esse controle.
