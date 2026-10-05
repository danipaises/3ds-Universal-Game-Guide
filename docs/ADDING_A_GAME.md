# Adicionar um jogo

1. Adicione um slug estável a `data/games.json`: nome, franquia, categoria, plataforma, `titleIds` por região, `guides` por idioma, hardwareStatus e cobertura regional. Atualize `data/franchises/<franquia>.json`. Não use região para escolher idioma.
2. Inclua cada variante em `data/title-id-evidence.json`, com URL, nome observado, data, hash do snapshot e verificação. Title ID de aplicação deve começar em 00040000 e ter 16 dígitos hexadecimais maiúsculos. Não derive de updates, DLC, serial ou da variante de outra região. Se desconhecido, deixe sem ID e declare a pendência.
3. Crie `guides/pt-BR/<slug>/guide.json`, arquivos Markdown, `sources.json` e `SOURCES.md`. Use os pilotos como formato. O índice tem schemaVersion=1, gameId, language, license=CC-BY-4.0, coverage=starter/pilot-partial/complete e pages. Cada página declara id, title, file, spoiler e sources (índices da lista de fontes); map/keywords são opcionais. Declare section em cada página e requiredSections, remaining e reviewed no índice. Complete exige reviewed=true e todas as seções obrigatórias presentes; essa validação estrutural não substitui revisão humana de fatos e completude.
4. Adicione mapas próprios em assets e registre autor, fonte, licença, URL/referência local, consulta e SHA-256 em ASSET_LICENSES.json. Declare o mapa em assets/maps.json. Há 1–3 níveis de zoom e até 2048×2048 na origem. Sem arte do jogo copiada automaticamente.
5. Execute `python3 builder.py validate --lang pt-BR`, `bash scripts/test.sh`, Ruff e build quando alterar C++. A página final tem até 8 KiB UTF-8; pack até 4 MiB/1.024 páginas. O título do campo tem até 95 bytes UTF-8, não 95 caracteres.
O Builder atualiza COVERAGE.md e CONTENT_GAPS.md com as lacunas exatas.
6. Regenere TITLE_ID_AUDIT.md e SUPPORTED_GAMES.md quando alterar o catálogo. Abra PR com fontes, o que foi revisado e quais testes foram realmente executados.

Conteúdo de app utilitário como Bank/Pokédex fica em categoria separada e pode ter instruções de uso em vez de walkthrough. Virtual Console, demos e updates não entram por coincidência no nome. Crossovers Mario com Donkey Kong direto são incluídos; a série Donkey Kong independente é excluída desta etapa.

Arquivos `dex-*` de X/Y são gerados e identificados por generatedBy. Faça correções no gerador/dado histórico com fonte, em vez de editar um arquivo que será sobrescrito na regeneração. Condições modernas não substituem regras da geração VI.
