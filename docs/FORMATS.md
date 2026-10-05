# Formatos do console

Inteiros little-endian; campos de string terminados em NUL, UTF-8 validado. Versões incompatíveis são recusadas. JSON e Markdown são apenas fontes de contribuição. Não mudar limites de C++ e Builder isoladamente.

| Magic | Layout |
|---|---|
| UGT1 | Cabeçalho 8 bytes: magic + count u32. Até 4.096 registros ordenados, 168 bytes cada: Title ID u64, Game ID 64 bytes, nome 96 bytes. Busca binária por ID. |
| UGG1 | Cabeçalho 12 bytes: magic, count u32, CRC32 do índice. Até 1.024 páginas; registro 208 bytes: slug48, título96, flags u32, offset u32, tamanho u32, CRC32 do texto, mapa48. Texto concatenado, até 8.192 bytes por página; pack até 4 MiB. |
| UGS2 | Cabeçalho 12: magic, count u32, fingerprint do índice UGG1. Até 131.072 registros ordenados: palavra64 + página u32. Busca por prefixo com lower_bound; lê só os registros correspondentes, em blocos de até 256. Não carrega a Pokédex inteira nem garante busca por substring arbitrária. |
| UGM1 | Cabeçalho 12: magic, níveis u32, CRC32 das dimensões; de 1 a 3 pares cols/rows u32. Tiles nomeados `<map>-<zoom>-<x>-<y>.ugi`; níveis ordenados de menor para maior resolução. |
| UGI1 | Cabeçalho 16: magic, width u32, height u32, CRC32. Dados RGB565 LE; máximo 320×192. Um tile carregado por vez. |
| UGC1 / UGC2 | 32 bytes: magic, hotkey u32, flags u32, idioma16, CRC32 dos 28 primeiros bytes. UGC1: spoilers 0/1. UGC2: bit0 mostrar spoilers, bit1 toque OFF, bit2 logging ON, bit3 lembrar página OFF; bits restantes recusados. Lê ambos, escreve UGC2. Apenas pt-BR/en-US; en-US ainda sem conteúdo. |
| UGR1 | Cabeçalho20: magic, fingerprint antigo u32, novo u32, count u32, CRC32 dos registros. Até 1.024 u32: página antiga → índice novo; FFFFFFFF significa removida. Exige fingerprints, tamanho, CRC e índices válidos, sem duplicatas de destino. |
| UGP2 | 276 bytes: magic, fingerprint, última página, linha de rolagem (quatro u32 incluindo magic); bitsets de favoritos e conclusão com 128 bytes cada; CRC32 final. Slots limitados a 1.024. |

UGP2 e UGS2 são as versões distribuídas nesta alpha; protótipos UGP1/UGS1 não são migrados. O fingerprint evita que um índice rearranjado atribua progresso à página errada. Na 0.2, UGR1 migra o estado dos seis guias oficiais da 0.1 por slug, preservando marcadores, conclusão e última página quando o destino existe. Estado inválido não é aplicado. Atualização incremental de packs no console continua fora do escopo; o usuário instala outro ZIP com o jogo fechado. A migração aqui é do estado, não um atualizador.

CRC32 detecta corrupção acidental e não autentica o conteúdo. SHA-256 acompanha o ZIP e os arquivos de distribuição. Nenhum mecanismo permite baixar ou executar código durante o jogo.

O formato UGG1 e demais índices continuam compatíveis. A configuração UGC2 não é lida pela 0.1: backup é necessário para rollback. O perfil hardware-test usa state/test-<idioma>-<game>.bin para evitar aplicar marcas de um índice reduzido ao guia completo.
