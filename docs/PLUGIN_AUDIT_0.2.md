> Atualização 2026-10-05: teste #1 falhou no carregamento. Para testar 0.2.1-alpha, use [HARDWARE_RETEST](../HARDWARE_RETEST.md). O texto anterior abaixo é referência histórica, não validação física.

# Auditoria do plugin — 0.2.0-alpha

0.2.0-alpha: TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD; 0.2.1-alpha: NEEDS HARDWARE RETEST. Análise de fonte, compilação ARM e suíte portátil; sem métricas físicas de heap/FPS ou teste de touch/GSP.

## Corrigido/implementado

Configuração antiga lida, novo formato limitado com CRC; combinações impossíveis com direções opostas recusadas; logging OFF e buffer limitado; controles de toque e última página; diagnóstico; memória do pack liberada ao sair; guarda antes de leitura; fallback de idioma quando arquivo preferido está ausente; estado antigo migrado por slug; existência de guia sem leitura a cada frame; teclado de busca com limite e atalho X no índice/menu. Mapa e tile inválidos geram erro/log. Catálogo desconhecido, corrompido e jogo conhecido sem guia têm mensagens distintas.

## Mantido após revisão

Lookup UGT1 binário, UGG1 com validação de offsets/tamanhos/CRC, UGS2 ordenado, leitura de um tile RGB565, estado/favoritos/progresso em pasta própria, pausa/resume RAII, framework com game-HID/CRO/ActionReplay desativados. SDK instala hook genérico GSP de overlay: não modificar ROM não significa ausência de hook no processo em runtime.

## Limites materiais

OOM antes da guarda ou em alocações subsequentes não foi simulado no SDK. Flush/rename com perda física de energia não foi testado; backup e temporário reduzem a perda, mas não oferecem uma transação garantida pelo hardware. Bypass R depende de inicialização básica bem-sucedida. Teclado, toque, HOME, tampa, carga de memória estendida Old3DS, GSP e interação com outro plugin precisam de teste. Plugin específico por TitleID tem prioridade sobre default.3gx, portanto não há promessa de composição de dois plugins.

Os logs limitados não são crash dumps e não conseguem registrar uma falha anterior à execução. O programa não faz benchmark nem acompanha continuamente a RAM do jogo. As instruções de recuperação estão em HARDWARE_TEST.md.
