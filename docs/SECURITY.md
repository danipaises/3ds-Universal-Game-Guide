# Segurança e limites

O core lê somente catálogo, índice, texto e tiles da pasta do projeto. IDs usados em caminhos são slugs ASCII limitados e validados. Offset/tamanho, limites de contagem, CRC e UTF-8 são verificados antes de exibir conteúdo. Fontes malformadas, symlinks e traversal são recusados pelo Builder. JSON com chaves duplicadas é erro.

A camada SD permite escrita exclusivamente em `state/`, `config.bin`, `unknown-title.txt` e `logs/`, dentro de `3ds/UniversalGameGuide`. Logs têm limite de 4 KiB e vêm desligados; não há gravação contínua durante gameplay. Os caminhos auxiliares do framework foram movidos para `runtime/`. O destino existente é renomeado para `.bak`, depois o arquivo temporário ocupa o destino. Erros podem preservar um backup; perda de energia durante gravação ainda precisa de teste. Não afirmar atomicidade garantida do cartão.

Se a gravação de preferências/progresso falhar ao fechar o overlay, uma tela permite tentar novamente ou voltar ao jogo. Sono e encerramento têm prioridade sobre esse aviso. A interface desse caminho compila, mas ainda depende de teste real com cartão cheio/erro de escrita.

O firmware Luma mantém seus próprios arquivos de configuração e, no Old 3DS em estratégia SWAP, pode usar `/luma/plugins/.swap`. Isso não é uma escrita da camada SD deste projeto. Falhas desse swap podem causar reinício pelo loader, conforme seu código oficial. Não prometer recuperação segura de toda falha de SD somente porque páginas corrompidas são recusadas pelo nosso parser.

Não há leitura/escrita de save, chamadas de alteração de NAND, conteúdo comercial, downloader, cliente HTTP, execução de conteúdo do guia, AR codes ou busca de memória específica de jogo. O framework participa do processo e usa a infraestrutura gráfica do jogo para o overlay. Ele não é um sandbox e corrupção do próprio executável não pode ser recuperada pelo parser de guias.

Um plugin default pode ser escolhido pelo firmware para softwares além dos jogos. Para categoria diferente de 00040000, a derivação evita a alocação/mapeamento de heap, serviços de jogo e gráficos. Mantém somente o cliente do loader e respostas a sono, HOME, swap e saída; terminar a thread imediatamente deixaria notificações sem resposta. Ainda requer teste no sistema e não é uma prova de correção do loader. Desative o loader para gerenciamento de microSD até a combinação ser validada.

Spoilers: títulos de páginas protegidas são substituídos no índice e na tela inferior; a busca exclui essas páginas enquanto a preferência estiver oculta. Revelar A vale para a página atual. Conteúdo narrativo misturado em páginas não sinalizadas depende da revisão editorial, não de detecção automática.

Relatos de problema devem incluir modelo, versão Luma, Title ID e passos de reprodução. Não inclua ROMs, saves particulares, chaves de console, tokens ou dumps contendo informações privadas.
