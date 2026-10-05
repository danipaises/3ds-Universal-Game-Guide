# Pesquisa técnica — consulta em 2026-10-04

## Decisão implementada

Um `.3gx` universal, formato v2, em `/luma/plugins/default.3gx`, sem um binário por jogo. CTRPluginFramework 0.8.0 fornece serviços de SD, fonte de sistema, input, buffers e pausa. Dados de catálogo e conteúdo são convertidos no PC em packs limitados; o console não faz parsing de JSON. A decisão foi confrontada com o código do loader e do framework, além de templates e projetos existentes. Respostas tipadas do MCP Jev foram consultadas como segunda opinião, sem tratar probabilidades como validação física. O diagnóstico doctor exigido pela estação não foi confirmado; veja os registros de revisão e o relatório.

## Fontes primárias e evidências

| Tema | Fonte | Constatação e decisão |
|---|---|---|
| Release do firmware | [Luma v13.4](https://github.com/LumaTeam/Luma3DS/releases/tag/v13.4) | Release oficial consultada: publicada em 2026-04-02. Não usar tutoriais de forks antigos para habilitar suporte que já existe no Luma oficial. |
| Seleção universal | [file_loader.c, v13.4](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/file_loader.c) | Procura plugins específicos por Title ID e oferece fallback `default.3gx`. Um plugin específico instalado anteriormente pode impedir o universal de ser selecionado. |
| Formato | [3gx.h](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/include/plugin/3gx.h) e [3gxtool oficial](https://gitlab.com/thepixellizeross/3gxtool) | Magic `3GX$0002`. O conversor antigo Nanquitas GitHub produziu 0001 e foi rejeitado para este build. O conversor atual é fixado no commit 57e3160a. |
| Memória | [memoryblock.c](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/memoryblock.c) | Bloco padrão de 5 MiB; caminhos diferentes para New/Old e modos de memória. O plugin declara 5 MiB e memória privada; isso não demonstra disponibilidade em todos os jogos de Old 3DS. |
| Framework estável | [CTRPF 0.8.0](https://gitlab.com/thepixellizeross/ctrpluginframework/-/tree/0.8.0) | Commit a502818c. Fonte oficial, não apenas um mirror. Build sem LTO para combinar a biblioteca com o compilador atual; warnings do upstream não são convertidos em erro, mas nosso código usa `-Werror`. |
| Title ID e pausa | [Process.hpp](https://gitlab.com/thepixellizeross/ctrpluginframework/-/blob/0.8.0/Library/include/CTRPluginFramework/System/Process.hpp) | `Process::GetTitleID`, `Pause` e `Play` usados. Pausa depende da infraestrutura gráfica do processo; retornar ao jogo requer teste real. |
| Input | [Controller.hpp](https://gitlab.com/thepixellizeross/ctrpluginframework/-/blob/0.8.0/Library/include/CTRPluginFramework/System/Controller.hpp) | D-Pad e Circle Pad possuem máscaras combinadas. Toque usa coordenadas da tela inferior. Não há injeção de botões nem leitura específica de memória de um jogo. |
| UTF-8 e desenho | [Screen.hpp](https://gitlab.com/thepixellizeross/ctrpluginframework/-/blob/0.8.0/Library/include/CTRPluginFramework/Graphics/Screen.hpp) | Fonte de sistema com DrawSysfont; 400×240 superior, 320×240 inferior. Textos são validados como UTF-8 e quebrados por largura medida; não depender de emoji. Glyphs e fonte regional ainda precisam de teste. |
| Cartão SD | [File.hpp](https://gitlab.com/thepixellizeross/ctrpluginframework/-/blob/0.8.0/Library/include/CTRPluginFramework/System/File.hpp) | Leitura por offset e tamanho; CRC por página/tile. Escrita restrita a config, estado e diagnóstico dentro da pasta própria. |
| devkitARM/libctru | [devkitPro](https://devkitpro.org/wiki/Getting_Started), [libctru](https://github.com/devkitPro/libctru) | Imagem oficial devkitpro/devkitarm fixada: r68-1 e libctru 2.7.0-1 constatados no ambiente. Não instalar toolchain de origem desconhecida. |
| Rosalina | [wiki oficial](https://github.com/LumaTeam/Luma3DS/wiki/Rosalina) | Atalho padrão L+baixo+SELECT. START+SELECT+A não o inclui; configurações personalizadas são verificadas quando disponíveis no framework. |
| Emulação | [Azahar 2126.1.2](https://github.com/azahar-emu/azahar/releases/tag/2126.1.2) e [issue do loader](https://github.com/azahar-emu/azahar/issues/1125) | Há suporte a 3GX e relatos de falhas por plataforma. Não substituir teste de Old/New 3DS por emulação; nenhum jogo comercial foi baixado. |
| default em software de sistema | [issue Luma #2254](https://github.com/LumaTeam/Luma3DS/issues/2254) | Relato atual em v13.4 com gerenciamento de microSD. Implementada guarda de categoria antes de inicializar serviços/graphics; a mitigação ainda não foi verificada no console. |

## Comparação e alternativas

O BlankTemplate do framework confirma a ligação e a organização de um plugin, mas contém um patch NFC não necessário ao guia; ele não foi copiado. O mirror GitHub de CTRPF e o converter antigo serviram como comparação, não como versão final. Plugins existentes que lidam com memória de Pokémon não foram usados como requisito de operação deste projeto.

Uma aplicação `.3dsx` independente não atende ao overlay dentro de um jogo. Implementar o leitor diretamente no Rosalina exigiria distribuir/manter um firmware personalizado e ampliar o escopo de segurança. Por isso o plugin do Luma é a base preferida nesta alpha. Não se conclui que CTRPF seja compatível com todo software nativo: essa matriz continua em aberto.

## Adaptações e limites verificáveis

`docs/CTRPF_FILESYSTEM.patch` documenta a derivação do framework: saídas em pasta própria, dependências fixadas, bypass de heap/gráficos para categorias de software não nativas e remoção dos hooks de CRO e redirecionamento HID usados por outros recursos. O bypass mantém respostas ao protocolo de HOME, sono, swap e saída: o [loader oficial aguarda essas respostas](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/plgloader.c). O hook gráfico genérico permanece necessário nos jogos. Não há patch por jogo, alteração de ROM ou save. A guarda consulta a extensão SVC de Title ID que o próprio framework utiliza.

O loop personalizado usa APIs internas SystemImpl para eventos de sono/saída e OSD para troca de buffers. Essa dependência está fixada em 0.8.0; uma atualização do framework exige revisão e novos testes. A pausa é pareada com retomada por RAII. HOME, fechamento da tampa, encerramento durante leitura do SD e títulos com modos de memória diferentes são casos bloqueadores para anunciar versão estável.

A fonte do framework reserva aproximadamente 1 MiB para seu heap auxiliar, além da infraestrutura gráfica e do heap C++. O core lê no máximo 152.256 bytes de índice na carga dos packs atuais, até 8 KiB de texto e um tile RGB565 de até 122.880 bytes. Isso é limite observado nos testes de PC, não medição do pico de RAM no console. O firmware mantém seu próprio orçamento e pode não alocar o plugin em um título específico.

No código v13.4, o loader também aceita um bloco de 2 MiB. Ele não foi escolhido para esta derivação não perfilada: o heap auxiliar de 1 MiB, buffers e restante do framework precisam de espaço antes dos dados do guia. Reduzir essa reserva exige medir as alocações e rever subsistemas; compilar não demonstraria que 2 MiB bastam.

O [loader](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/plgloader.c) começa na estratégia SWAP. No Old 3DS, HOME pode descarregar o bloco do plugin em `/luma/plugins/.swap`; essa é uma escrita do firmware, distinta da camada SD do projeto. O [gerenciador de memória](https://github.com/LumaTeam/Luma3DS/blob/v13.4/sysmodules/rosalina/source/plugin/memoryblock.c) contém caminhos que reiniciam o console em falhas de alocação/swap. O parser do guia não controla essa recuperação do firmware.

O Luma oferece MODE3 por parâmetros de carregamento e ajusta o modo de memória antes da aplicação. Este default.3gx não configura MODE3 antecipadamente nem altera parâmetros persistentes do loader. Carregar títulos de memória estendida no Old 3DS não está assegurado; uma solução de pré-lançamento deve ser investigada e validada antes de prometer todos esses títulos. A alpha não representa suporte universal confirmado em todos os modelos.

A combinação de abertura pode chegar ao jogo antes que a pausa ocorra. O guia não intercepta nem reescreve input no processo. Pausa em lutas online não é garantida nem proposta; o objetivo é consulta offline. Configuração e progresso ficam no SD. A preferência pt-BR jamais é inferida de USA/EUR/JPN.

## Auditoria incremental 0.2 (2026-10-04)

Mantidos Luma13.4, .3gx v2 e CTRPF0.8.0 fixados. O loader oficial não apresenta um bypass por botão para este plugin nos arquivos file_loader.c/plgloader.c consultados. O bypass R é uma derivação nossa do startup CTRPF: lê HID depois de inicializar serviços básicos e antes de Screen/scheduler/GSP/OSD; sinaliza continuação e mantém acknowledgments do loader. O firmware já alocou memória do plugin nessa etapa. Não elimina falhas no loader, não foi testado em hardware e não deve ser apresentado como função oficial do Luma.

System::IsNew3DS informa família Old/New, não o modelo comercial exato. getMemFree é a função de allocator do libctru/newlib e informa reserva disponível no heap próprio, não memória livre total do jogo/console. Uma guarda de 1 MiB antes de abrir o pack limita o risco, mas não prova que todas as alocações do framework ou SD falhem de forma recuperável. Testes de OOM real ainda pendentes.

UGGTouchEnabled mascara apenas flags locais de Controller CTRPF; Touch::IsDown e o teclado do SDK consultam esses flags. UseGameHidMemory permanece false; não injetamos entrada no jogo. Key::Up/Down/Left/Right inclui D-Pad e Circle Pad no header verificado. Process::Pause/Play é usado por RAII; buffers de páginas, texto e linhas são liberados antes do retorno. Suspensão, HOME e retomada requerem teste físico.

Logging não roda no loop de gameplay: eventos ficam num buffer de até 4 KiB e são escritos ao fechar o overlay ou exportar diagnóstico. O histórico de títulos é limitado e gravado somente por escolha explícita do usuário. A leitura de existência de guia ausente foi movida para fora do loop de frames. Busca continua UGS2 binária, sem varrer texto.

Fontes técnicas: [loader Luma13.4](https://github.com/LumaTeam/Luma3DS/tree/v13.4/sysmodules/rosalina/source/plugin), [CTRPF fixado](https://gitlab.com/thepixellizeross/ctrpluginframework/-/tree/a502818c7586179d320caf8e897238d3491b5a29), [libctru2.7.0](https://github.com/devkitPro/libctru/tree/v2.7.0). API e implementação foram consultadas nas fontes baixadas com hash. Nenhuma conclusão de compatibilidade física deriva disso.
