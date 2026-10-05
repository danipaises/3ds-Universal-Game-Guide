# Dados factuais de geração VI

`gen6.json` contém 721 espécies em suas formas padrão, com tipos, atributos base, habilidades (ocultas sinalizadas), multiplicadores de dano, evolução, números regionais de Kalos, registros de área/método/versão e movimentos por nível para X/Y.

O console não lê esse JSON: o gerador escreve páginas editoriais factuais, e o Builder cria UGG1/UGS2. O runtime consulta um índice limitado e só carrega a página solicitada. Regiões de distribuição do jogo não selecionam o idioma.

Fonte PokéAPI/BSD-3-Clause no commit fixado por source-lock.json. Tabelas históricas corrigem tipos, atributos e habilidades para geração VI. A evolução por amizade usa 220, com referência específica; valores modernos não são tratados como históricos. Dados alterados em research/pokeapi são recusados antes da geração.

Limitações: formas Mega e outras formas alternativas não estão completas; disponibilidade por presentes/trocas/eventos/Friend Safari e condições de encontro não é exaustiva. Um registro de presente é rotulado como presente, não como encontro selvagem. Ausência de registro não significa impossibilidade de obter a espécie. A tabela de fraquezas ignora habilidades, itens e estado do campo. TMs/HMs, tutors, Egg Moves e condições especiais ainda precisam de revisão editorial.

Para regenerar: `python3 scripts/fetch_data_sources.py pokemon`, depois `python3 scripts/generate_pokedex.py`. O gerador atualiza páginas dex-* em X/Y e preserva suas páginas editoriais. Mudar o conteúdo pode mudar o fingerprint e reiniciar marcadores; migração por slug ainda não existe. Não importar flavor text, sprites ou arte de jogos.
