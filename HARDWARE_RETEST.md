# Reteste de inicialização — 0.2.1-alpha

**TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD (0.2.0-alpha).**

**0.2.1-alpha: NEEDS HARDWARE RETEST.** Compilação não demonstra que o crash foi corrigido.

Este reteste continua usando o par já entregue: MINIMAL `ad4ddcb8…`, FULL `beb5127c…` (SHA-256 completos no [relatório oficial](https://github.com/danipaises/3ds-Universal-Game-Guide/blob/main/TEST_REPORT.md)). A correção GCC na importação GitHub recompila um FULL diferente, `acb8c084…`; os artifacts novos identificam o commit com `-ci-<commit>` no nome. Eles são candidatos separados, sem resultado físico. Preserve o pacote original para a comparação já planejada e use os símbolos do mesmo pacote do binário instalado.

Teste #1 informado pelo usuário em 2026-10-05: Plugin Loader Enabled; default.3gx encontrado SIM; Super Mario 3D Land; exception ARM11 imediatamente ao iniciar; overlay NÃO; hotkey NÃO testada; guias NÃO testados. **FAIL — plugin initialization/load crash.** Modelo exato, Luma, Title ID, região e .dmp ainda não informados. Não inferimos esses campos.

## 1. Instalar MINIMAL primeiro

1. Desligue o 3DS e faça backup de `luma/plugins/default.3gx` e `3ds/UniversalGameGuide/` no computador.
2. Extraia **UniversalGameGuide-PTBR-Hardware-Test-v0.2.1-alpha.zip** na raiz do SD. `luma/plugins/default.3gx` já é o **MINIMAL**. Configuração/progresso não vêm no instalador e não são apagados.
3. Na pasta `diagnostics/`, ficam `default-minimal.3gx`, `default-full.3gx` e BUILD.json. São builds diferentes, ambos PRIVATE=false / 5 MiB. Não os execute simultaneamente.
4. Se houver um plugin específico em `luma/plugins/<Title ID>/`, faça backup e desabilite-o temporariamente renomeando seu `.3gx` para `.3gx.disabled`: ele tem prioridade sobre default. Preserve plugins de outros títulos.
5. Antes de cada tentativa, copie o `logs/boot-stage.txt` anterior para o computador e remova apenas esse marcador do SD, com o console desligado. Isso evita confundir uma execução antiga com um crash antes do primeiro flush.
6. Mantenha seu Luma e as opções usados no teste #1; confirme Plugin Loader habilitado. Não é necessário atualizar firmware para este experimento. Abra **Super Mario 3D Land**, sem segurar R.
7. Espere pelo início normal do jogo e pela indicação `UGG MINIMAL 0.2.1 carregado`. Em seguida use **START + SELECT + A**, solte os botões e confirme a tela com Title ID e heap. Pressione **B** e confirme imagem, som e input do jogo.
8. Encerre e desligue normalmente. Copie o marcador para `boot-stage-minimal.txt` no computador e anote o resultado. Se o MINIMAL falhar, pare e envie o .dmp/marcador; não avance para guias.

O MINIMAL não lê config, VERSION, titles.bin, guia, mapa, busca, favoritos ou progresso. Usa o mesmo startup CTRPF e protocolo do loader do FULL; portanto não é um plugin sem framework. O único acesso próprio ao SD é o marcador de diagnóstico. A hotkey dele é fixa e ignora configurações antigas; evite configurar Rosalina com a mesma combinação.

## 2. Trocar para FULL após MINIMAL iniciar

Com o console desligado, **copie** `diagnostics/default-full.3gx` para `luma/plugins/` e renomeie a cópia para `default.3gx`, substituindo a anterior. Não basta renomear o MINIMAL como FULL. Mantenha os originais em diagnostics. Limpe o marcador como no passo 5.

Teste separadamente e registre onde ocorreu a primeira falha:

| Tentativa | Ação | Evidência |
|---|---|---|
| A | Apenas iniciar FULL e jogar alguns segundos, sem hotkey | stage 0x11: main entrou no loop após ler config |
| B | Abrir menu com a hotkey configurada; B retorna | 0x12: overlay solicitado; 0x13/0x14: catálogo |
| C | Abrir índice/primeira página de Mario | 0x15/0x16: guia solicitado/carregado |
| D | X no menu/índice; pesquisar Mario | 0x17/0x18: busca iniciou/retornou |
| E | Abrir mapa de World 1-1 | 0x19/0x1A: mapa solicitado/primeiro tile |

No FULL, a configuração anterior de hotkey continua válida. O padrão é START + SELECT + A. Este pacote conserva os mesmos seis pilotos reduzidos/78 páginas da etapa anterior. Nenhum guia foi expandido. O progresso do perfil de teste continua em `state/test-pt-BR-<game>.bin`.

O índice/guia é carregado na primeira abertura do overlay. Os checkpoints informam limites de etapas; não permitem provar sozinho qual instrução falhou. Se FULL falhar e MINIMAL passar, registre a primeira ação divergente. Se ambos falharem antes de main, investigue loader/startup CTRPF pelos símbolos e dump; não culpe o conteúdo sem evidência.

## Marcadores precoces e limites

Arquivo: `SD:/3ds/UniversalGameGuide/logs/boot-stage.txt`.

| Stage hexadecimal | Ponto alcançado |
|---|---|
| 01 | Entrypoint, somente buffer BSS, antes do heap/serviços |
| 02 / 03 | Thread inicial; antes / depois de initLib e construtores |
| 04 / 05 | srvInit / fsInit começam; resultados das chamadas no buffer |
| 06 | Primeiro acesso ao marcador SD após fsInit; descarrega checkpoints anteriores |
| 07 / 08 | Serviços retornaram / Kernel-System-Process inicializados, Title ID |
| 09 / 0A | Screens / OSD inicializados |
| 0B / 0C | FS e heap CTRPF / HID e preferências; game release |
| 0D | GSP inicializado; espera antes da thread principal |
| 0E / 0F | Inicialização de fonte/screenshots da thread main começou/terminou |
| 10 / 11 | main MINIMAL/FULL entrou / loop de hotkey |
| MINIMAL 12 / 13 / 14 | overlay solicitado / frame submetido / voltou ao jogo |

Antes de fsInit não há escrita segura no SD: 01–05 existem somente em RAM até 06. Ausência do arquivo pode significar falha do loader/CRT, heap, construtores, serviços ou acesso ao SD; **não identifica sozinha a etapa**. Resultados de serviços são hexadecimais, não afirmações de sucesso. O arquivo traz versão e variante; não traz dados do save.

Boot trace é deliberadamente ligado nesses dois binários de diagnóstico, independente de Debug Logging. Limite: buffer de 3.072 bytes, no máximo 40 gravações por execução; checkpoints não se repetem por frame. Falha de escrita interrompe as próximas gravações. O marcador pode ficar incompleto em crash/perda de energia. `latest.log` continua opcional e OFF por padrão no FULL. O protocolo de pausa/HOME/sono/saída não foi reescrito.

## Crash dump do Luma

Na tela **An exception occurred**, fotografe a tela inteira e pressione **A para salvar o crash dump**, conforme a opção exibida. Anote o caminho mostrado. Normalmente será:

`SD:/luma/dumps/arm11/crash_dump_XXXXXXXX.dmp`

Copie **o arquivo .dmp mais recente daquela tentativa**, não um .dmp de outra execução. O número é incremental; não há um nome fixo. Se a tela mostrar CTRNAND em vez de SD, registre o caminho e a foto; não altere NAND como parte deste reteste. O guia antigo da wiki cita um parser que não existe no tree v13.4 consultado; esta entrega fornece parser próprio limitado ao formato documentado na fonte oficial.

Envie junto: variante MINIMAL/FULL, hash do .3gx instalado, BUILD.json, foto, boot-stage correspondente (se existir), modelo exato, versão do Luma, Title ID/região/updates quando conhecidos e ação que precedeu o crash. Para o primeiro crash 0.2.0, podemos analisar o dump estruturalmente; **os símbolos 0.2.1 não correspondem ao binário 0.2.0**.

## ELF/MAP da mesma compilação — computador, não instalação

Baixe **UniversalGameGuide-Debug-Symbols-v0.2.1-alpha.zip** e extraia no computador. Ele contém default-minimal.elf/.map/.3gx, default-full.elf/.map/.3gx, BUILD.json, licenças e diagnostics.py. O SOURCE vem em ZIP separado. Não coloque ELF/MAP em luma/plugins. Os SHA-256 em BUILD.json associam exatamente ELF, MAP e binário de cada variante; não use símbolos de outra build, mesmo com a mesma versão no nome.

Com Python e o addr2line do devkitARM, dentro da pasta extraída:

```sh
python diagnostics.py crash_dump_XXXXXXXX.dmp --variant full --elf default-full.elf --plugin default-full.3gx --manifest BUILD.json --addr2line /opt/devkitpro/devkitARM/bin/arm-none-eabi-addr2line
```

Para MINIMAL, troque os três argumentos correspondentes. O script verifica os hashes, extrai PC/LR/SP e simboliza somente endereços dentro das seções executáveis do ELF. PC já foi ajustado pelo Luma; não subtraia outro offset nem 0x07000000. O bit Thumb é limpo para consulta. Palavras da stack que parecem endereços são **candidatos**, não backtrace confirmado. Otimização e frame pointers omitidos no SDK limitam unwinding. PC/LR fora do plugin exigem contexto do loader/jogo/kernel e não têm símbolo correspondente neste ELF; `??` não prova erro do plugin.

Consulta manual de um endereço do plugin:

```sh
arm-none-eabi-addr2line -f -C -i -e default-full.elf 0x07000100
```

O endereço acima é apenas um exemplo de entrada; use o PC/LR reais da tela/dump. MAP localiza funções/objetos/seções; ELF com DWARF fornece linhas. DMP do Luma possui cabeçalho próprio e não é um core dump ELF do GDB.

## Recuperação

Se ocorrer crash, salve o dump e desligue. Com o console desligado, renomeie `luma/plugins/default.3gx` para `default.3gx.disabled` ou desabilite Plugin Loader no Rosalina. Restaure o backup anterior quando necessário; o .3gx antigo volta a reproduzir o problema já observado. O bypass R da build anterior permanece experimental e não evita alocação/mapeamento inicial do Luma; não dependa dele para este crash.

## Fontes técnicas consultadas em 2026-10-05

- [Luma issue #2225](https://github.com/LumaTeam/Luma3DS/issues/2225): relato de PRIVATE=true crashando outros títulos, inclusive minimal; hipótese pertinente, não prova da causa em Mario.
- [Luma PR #2086](https://github.com/LumaTeam/Luma3DS/pull/2086): PRIVATE para compartilhar heap com serviços socket/HTTP. UGG não inicializa soc/httpc.
- [Loader memoryblock.c v13.4](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/memoryblock.c): escolha de flags e tamanho do bloco, diferenças Old/New/MODE3.
- [Exception header v13.4](https://github.com/LumaTeam/Luma3DS/blob/v13.4/k11_extension/include/fatalExceptionHandlers.h), [handler](https://github.com/LumaTeam/Luma3DS/blob/v13.4/k11_extension/source/fatalExceptionHandlersMain.c), [salvamento](https://github.com/LumaTeam/Luma3DS/blob/v13.4/arm9/source/exceptions.c): formato, ajuste de PC, botão A e caminho do dump.
- [GNU addr2line](https://sourceware.org/binutils/docs/binutils/addr2line.html): consulta de função/linha/inlining a partir do ELF.
- CTRPF 0.8.0/a502818c e 3gxtool 57e3160 fixados em data/dependencies.lock.json; patch próprio em docs/CTRPF_FILESYSTEM.patch.
