> Atualização 2026-10-05: teste #1 falhou no carregamento. Para testar 0.2.1-alpha, use [HARDWARE_RETEST](../HARDWARE_RETEST.md). O texto anterior abaixo é referência histórica, não validação física.

# Checklist real — todas as linhas pendentes

**Não testado em hardware real.** Preencher cada execução com modelo exato, versão Luma, versão do jogo/update, Title ID observado, região, hash do .3gx, horário e resultado. Não enviar ROMs ou saves.

| Plataforma | Estado |
|---|---|
| Old Nintendo 3DS | Pendente |
| Old Nintendo 3DS XL | Pendente |
| New Nintendo 3DS | Pendente |
| New Nintendo 3DS XL | Pendente |
| New Nintendo 2DS XL | Pendente |
| Nintendo 2DS original | Pendente adicional |

Para cada modelo e piloto:

- [ ] Jogo inicia com o loader desabilitado e habilitado; anotar diferença.
- [ ] Luma seleciona default.3gx; testar prioridade de plugin específico sem apagá-lo.
- [ ] Title ID real é reconhecido corretamente; testar USA/EUR/JPN e KOR/TWN quando disponíveis.
- [ ] START+SELECT+A abre; soltar a combinação não seleciona uma opção acidentalmente.
- [ ] Alterar hotkey, fechar, reiniciar e conferir persistência e conflito com Rosalina personalizado.
- [ ] Segurar R antes do lançamento e verificar bypass; depois soltar e iniciar novamente para ativar o guia. Comparar com desativação completa do Plugin Loader.
- [ ] Logging OFF não grava latest.log durante gameplay; ON grava versão, modelo, ID e carregamento ao fechar/exportar. Falha anterior ao init não é registrada.
- [ ] Diagnóstico mostra perfil, idioma efetivo, guia/páginas/mapas e heap newlib, sem apresentar esse valor como RAM total.
- [ ] Touch OFF desativa seleção e teclado por toque; D-Pad e botões ainda permitem busca/configuração. Reativar e conferir persistência.
- [ ] Lembrar página OFF mantém favoritos/conclusão, mas reabre a primeira página; ON restaura a posição.
- [ ] Instalar sobre 0.1 usando cópias de config/estado e verificar migração por slug. Fazer backup antes: 0.1 não lê a nova configuração UGC2.
- [ ] Pacote Hardware-Test usa estado test-pt-BR separado; instalar release normal volta ao estado normal, preservando ambos.
- [ ] D-Pad, Circle Pad, A/B, L/R, X/Y e repetição de direção.
- [ ] Toque nas sete linhas, bordas e cabeçalho; nenhum acesso fora de índice.
- [ ] Texto “ação, evolução, Pokémon, coração” legível em PT-BR, inclusive num console japonês.
- [ ] Pausa visual e de lógica; fechar sem artefatos, som perdido ou botões presos.
- [ ] HOME, tampa/sono e encerramento enquanto guia/teclado/mapa estão abertos; voltar normalmente.
- [ ] Busca Charizard, Hookshot e Route 2; medir tempo da consulta e carga da Pokédex.
- [ ] Spoiler oculta texto, título, resultados de busca e acesso ao mapa até revelar.
- [ ] Favoritos, conclusão e última página persistem; o save do jogo fica intacto.
- [ ] Tiles, limites de pan, dois níveis de zoom e leitura só do tile corrente.
- [ ] Software nativo desconhecido mostra o ID correto e grava unknown-title.txt / logs/unknown_titles.log somente ao selecionar Anotar.
- [ ] Tela de diagnóstico permite selecionar Anotar/Voltar/Configurações por D-Pad/Circle Pad e toque.
- [ ] Título reconhecido sem guia, pack ausente, CRC inválido e cartão cheio são tratados.
- [ ] Falha de escrita preserva config/estado anterior ou backup; interrupção de energia em aparelho de teste.
- [ ] Aviso de falha de gravação: tentar novamente/voltar com botões e toque; sono/saída não ficam bloqueados no aviso.
- [ ] Pico de RAM e estabilidade em sessão longa; títulos de memória estendida no Old 3DS.
- [ ] Guarda de software de sistema: Settings, applets, gerenciamento de microSD. Manter loader desabilitado nesse uso até validação.
- [ ] Escritas próprias/plugin/framework só em 3ds/UniversalGameGuide; observar separadamente configuração e .swap do Luma. Nenhuma alteração de save/NAND/ROM.
- [ ] Estratégia padrão vs MODE3 em Old 3DS e títulos de memória estendida; não assumir que default.3gx configura o modo antes do lançamento.

Não executar remoção física do SD com o console ligado como rotina de teste. Para corrupção controlada, modificar cópias do pack com o aparelho desligado. Um resultado em um título/modelo não preenche a matriz inteira.
