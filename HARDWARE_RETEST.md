# Reteste controlado — 0.2.2-alpha

**0.2.1-alpha: TESTED ON REAL HARDWARE — FAIL.** Old, Luma **13.1.1**, MINIMAL, Super Mario 3D Land, Title ID **0004000000053F00**. Dump #8: PC 07005B5C, LR 07005B50, CTRPF::__system_allocateHeaps; retorno D8E007F7 (handle inválido). O diagnóstico está na [auditoria](https://github.com/danipaises/3ds-Universal-Game-Guide/blob/main/docs/HEAP_INITIALIZATION_AUDIT_0.2.2.md).

**0.2.2-alpha: REAL HARDWARE TESTED — FULL PARTIAL PASS.** A chamada foi corrigida e a memória continua PRIVATE=false / 5 MiB. Não considere o crash resolvido por compilar.

## Resultado real recebido — teste #3

**0.2.2-alpha REAL HARDWARE TESTED**, Old Nintendo 3DS + Luma 13.1.1, Super Mario 3D Land / 0004000000053F00. **MINIMAL-BOOT PASS; MINIMAL PASS; FULL PARTIAL PASS**. Boot, hotkey, Title ID, main UI, guia/navegação básica e retorno passaram. **Offline Search e Settings provocam ARM11 crash**. Mapas e outros fluxos ainda não têm aprovação física.

A observação MINIMAL foi heap newlib 8.172.600 bytes / boot log result 00000000. Rótulos de tela e dos ZIPs históricos anteriores ao reteste permanecem preservados. Não assumir causa comum dos dois crashes. Para uso normal, evite essas duas opções até corrigir.

## Coletar dumps A e B separadamente

1. Preserve o plugin instalado, o ZIP original e `diagnostics/BUILD.json`. Anote SHA-256 de `luma/plugins/default.3gx`. O FULL histórico conhecido é ea96f45a5f870f1e9ba0b3916a177b88be6794ed82e9ba387bc28fb358b0d702.
2. Para a tentativa de Pesquisa, guarde ação exata, foto, boot-stage e dump mais novo em luma/dumps/arm11; identifique-o como **A — Offline Search** no computador, preservando o nome original.
3. Para Configurações, faça registro independente e identifique o dump como **B — Settings**. Não confunda com crash_dump_00000008.dmp da 0.2.1.
4. Confirme Title ID, exception/access, PC/LR/SP e registradores. ELF FULL esperado: 5bd2c9d1c0c4a6c0b99c3fed5036bd40186f6b427366f5f8840de33675dec1b6; MAP: 288c46577ad93bfe95fc8497956fecab0fccf1767cdaac98f82096381f9a3c38.
5. **Sem confirmação de identidade instalada + BUILD.json + ELF/MAP, parar antes da simbolização.** O arquivo recebido da stack só permite candidatos; não inventar backtrace. Os dumps brutos ficam privados/ignorados pelo Git.

## Próximo reteste — 0.2.3 ainda não gerada

Nenhuma caixa abaixo está aprovada antecipadamente. Somente aplicar à futura build corrigida, com hashes próprios, após analisar os dumps.

- [ ] Plugin Loader
- [ ] boot
- [ ] MINIMAL-BOOT
- [ ] MINIMAL
- [ ] hotkey
- [ ] FULL boot
- [ ] game detection
- [ ] main UI
- [ ] guide
- [ ] guide navigation
- [ ] offline search
- [ ] empty search (confirmar rejeição/retorno sem crash)
- [ ] search without results
- [ ] search → back → search, repetidamente
- [ ] settings
- [ ] settings save
- [ ] settings reopen, conferindo preferências persistidas
- [ ] settings → back → settings, repetidamente
- [ ] maps
- [ ] navigation
- [ ] close guide
- [ ] reopen guide
- [ ] close plugin (fechar overlay)
- [ ] reopen plugin (reabrir overlay sem reiniciar o jogo)
- [ ] return to game
- [ ] game remains playable

FULL = PASS exige todas as funções relevantes aprovadas em hardware, incluindo abrir/fechar Search e Settings repetidamente. HOME/sono/swap devem ter registro separado. Expansão massiva de guias permanece pausada.

Testes adicionais, separados da checklist principal:

- [ ] HOME behavior
- [ ] sleep/wake
- [ ] game/app transition

Nenhum desses testes adicionais foi aprovado antecipadamente. Análise de lifetimes, limites do core e plano de checkpoints em [SEARCH_SETTINGS_DIAGNOSTIC_PLAN.md](docs/SEARCH_SETTINGS_DIAGNOSTIC_PLAN.md). Instrumentação futura e recompilações precisam de identidade própria; não substituem a build histórica instalada.

## Procedimento original de instalação da 0.2.2

## 1. Backup e instalação

1. Desligue o console. Faça backup do SD, especialmente `luma/plugins` e `3ds/UniversalGameGuide`, no computador. Preserve também os pacotes 0.2.1 e seus símbolos, necessários para comparar o teste #2.
2. Extraia **UniversalGameGuide-PTBR-Hardware-Test-v0.2.2-alpha.zip** na raiz do SD. Ele instala **MINIMAL-BOOT** em `luma/plugins/default.3gx`. Nenhum ELF/MAP vai para o cartão; configuração e progresso existentes não são sobrescritos.
3. Confirme que não há outro .3gx selecionado na pasta específica `luma/plugins/0004000000053F00/`. Essa pasta tem prioridade sobre default.3gx. Mova plugins concorrentes para o backup durante o teste; não exclua o backup.
4. Arquive/remova o marcador antigo `3ds/UniversalGameGuide/logs/boot-stage.txt` para não confundir tentativas. Se já existe dump antigo, preserve-o e anote seu nome.
5. Recoloque o SD. Abra Rosalina (atalho padrão **L + D-Pad baixo + SELECT**) e marque **Plugin Loader: Enabled**. Mantenha inicialmente o mesmo Luma 13.1.1, console e jogo do teste #2 para isolar a mudança no plugin. Não é necessário atualizar firmware/Luma para este experimento.
6. Abra **Super Mario 3D Land**, inicialmente sem pressionar qualquer hotkey.

## 2. MINIMAL-BOOT primeiro

Esta variante mantém o CRT, initLib/stack_adjust.s e alocador do CTRPF. Usa uma thread e logging SD; não inicializa OSD, GSP, fontes, som, HID, menu, core ou guias. Mantém o layout de heap do SDK para testar a mesma operação de mapeamento. Aplicativos do sistema passam pelo bypass sem heap/SD/UI.

**Resultado esperado (confirmado no teste #3 para o console relatado):** o jogo inicia normalmente e permanece com imagem, som e input. **Nenhuma notificação ou overlay deve aparecer. START + SELECT + A não faz nada nesta variante.** Encerre/desligue normalmente e examine o arquivo de boot no computador.

O marcador deve identificar `UGG 0.2.2-alpha / minimal-boot`, incluir `STAGE 0x03 CTRPF heap allocation and linked constructors returned` e `STAGE 0x10 MINIMAL-BOOT ready`, sem erros nos resultados de FS/loader. Deve listar Title ID, heapVA/heapSize recebidos do loader, heap newlib e versão codificada do Luma. O tamanho do newlib não é RAM livre total do console. O arquivo só existe se o FS/SD funcionar; ausência de marcador não identifica sozinha a causa.

Se houver crash, pare aqui. Preserve o dump novo e o SHA-256 do .3gx instalado. Não avance ao MINIMAL/FULL. Se o jogo inicia mas não há marcador, informe essa diferença antes de avançar.

## 3. MINIMAL com interface

Com o console **desligado**, copie `diagnostics/default-minimal.3gx` sobre `luma/plugins/default.3gx`. Arquive/remova o boot-stage anterior. Essa é a segunda variante, não o MINIMAL-BOOT.

Abra o mesmo jogo. O resultado esperado é a notificação `UGG MINIMAL 0.2.2 carregado`. Use **START + SELECT + A**, solte os botões e confira Title ID/heap/log na tela. Pressione **B**, confira imagem, som e input do jogo. O MINIMAL não lê guias, configuração, catálogo, mapas ou busca. Arquive o marcador como `boot-stage-minimal.txt` no computador e registre sucesso/falha de cada ação.

## 4. FULL depois

Somente após confirmar MINIMAL, desligue e copie `diagnostics/default-full.3gx` para `luma/plugins/default.3gx`. Arquive/remova o marcador. Teste na ordem: jogo sem hotkey → hotkey → catálogo → texto PT-BR → B → busca → spoiler → mapa/touch → favorito/progresso. O pacote contém seis guias reduzidos: Mario 3D Land, Pokémon X/Y, Ocarina of Time 3D, Kirby Triple Deluxe e Luigi's Mansion 2/Dark Moon. Não são guias completos nem jogos fisicamente certificados.

No FULL/MINIMAL, R durante a janela de inicialização pode pular a UI, mas ocorre **após** alocação do heap; não evita uma falha anterior. A recuperação confiável é desabilitar o Plugin Loader ou remover/mover default.3gx com o console desligado.

Depois do primeiro resultado documentado, teste HOME/retorno, sono/retorno e encerramento. Não assuma que passar no boot garante esses fluxos. Registre variante e ação. Em caso de crash, pare e não misture resultados de variantes.

## Recuperação e evidências

Desligue conforme instruções da tela do Luma. No computador, mova `luma/plugins/default.3gx` para o backup; se necessário desative o Plugin Loader no Rosalina. Confira também qualquer plugin específico por Title ID. Não restaure automaticamente o plugin 0.2.1 que já crashou. Guias, config/progresso próprios e saves do jogo não precisam ser apagados.

Envie: modelo exato, versão Luma, variante, jogo/Title ID/região quando conhecidos, ação anterior à falha, foto com PC/LR, SHA-256 de `luma/plugins/default.3gx`, `diagnostics/BUILD.json` e boot-stage daquela tentativa (se existir). O dump ARM11 costuma ficar em **SD:/luma/dumps/arm11/**; copie o arquivo mais novo daquela execução e preserve o nome. Se a tela apontar CTRNAND, informe o caminho e a foto; este teste não pede alteração na NAND. Não envie ROMs, CIAs comerciais, saves, firmware, chaves ou credenciais.

Para análise no PC, extraia **UniversalGameGuide-Debug-Symbols-v0.2.2-alpha.zip**. O diagnostics.py histórico desse ZIP valida ELF/plugin; use a ferramenta atual da main para exigir também MAP e o hash instalado. Ele contém as três combinações .3gx/.elf/.map, BUILD.json, licenças e diagnostics.py. Use exatamente o trio correspondente ao plugin instalado. Exemplo, com devkitARM no PATH:

```sh
python /caminho/do/repositorio/scripts/diagnostics.py DUMP_A_SEARCH.dmp --variant full --elf default-full.elf --map default-full.map --plugin default-full.3gx --manifest BUILD.json --installed-sha256 HASH_CONFIRMADO_NO_SD
```

O nome acima é apenas exemplo; informe o nome real e o hash confirmado no SD. A ferramenta atual recusa ELF/plugin/MAP de hashes diferentes ou identidade instalada não correspondente. PC do Luma já está ajustado; não subtraia quatro novamente. Candidatos da stack não constituem backtrace confirmado. Dumps brutos ficam privados/ignorados pelo Git por conterem memória do processo.

## Limites

Boot trace experimental: BSS 3 KiB, até 40 writes por execução, nenhum acesso SD antes de fsInit; erro SD encerra novas gravações. Debug Logging normal do FULL continua OFF. O marcador não é handler de exception nem captura um crash anterior ao FS. Fonte e estrutura do loader foram revisadas antes do probe; nenhuma chamada de pausa do jogo é feita pelo MINIMAL-BOOT.

Referências primárias: [CTRPF pin](https://gitlab.com/thepixellizeross/ctrpluginframework/-/tree/a502818c7586179d320caf8e897238d3491b5a29), [Luma 13.1.1](https://github.com/LumaTeam/Luma3DS/tree/v13.1.1), [auditoria da ABI](https://github.com/danipaises/3ds-Universal-Game-Guide/blob/main/docs/HEAP_INITIALIZATION_AUDIT_0.2.2.md), [histórico 0.2.1](https://github.com/danipaises/3ds-Universal-Game-Guide/blob/main/docs/history/HARDWARE_RETEST-0.2.1.md).
