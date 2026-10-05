> Atualização 2026-10-05: teste #1 falhou no carregamento. Para testar 0.2.1-alpha, use [HARDWARE_RETEST](HARDWARE_RETEST.md). O texto anterior abaixo é referência histórica, não validação física.

# Instalar Universal Game Guide 0.2.0-alpha

**0.2.0-alpha: TESTED ON REAL HARDWARE — CURRENT RESULT: CRASH ON PLUGIN LOAD; 0.2.1-alpha: NEEDS HARDWARE RETEST.** Esta é uma alpha para testes. Os guias são parciais.

1. Desligue completamente o 3DS e faça backup do cartão SD, em especial `luma/plugins/` e `3ds/UniversalGameGuide/`.
2. Para o primeiro teste, use `UniversalGameGuide-PTBR-Hardware-Test.zip` e siga `HARDWARE_TEST.md`, que vem nele. O pacote completo chama-se `UniversalGameGuide-PTBR-v0.2.0-alpha.zip`.
3. Extraia o ZIP na **raiz do SD**. Devem existir `SD:/luma/plugins/default.3gx` e `SD:/3ds/UniversalGameGuide/titles.bin`. Não crie uma pasta extra com o nome do ZIP.
4. Se já houver outro `default.3gx`, guarde-o antes da substituição. Um plugin em `luma/plugins/<TitleID>/` tem prioridade e pode impedir a abertura deste guia. Preserve seus arquivos durante o teste.
5. Use o Luma3DS com Plugin Loader oficial (pesquisa/build desta alpha: 13.4). Abra Rosalina, normalmente **L + baixo + SELECT**, e ative **Plugin Loader**. Reinicie o título depois de ativar.
6. Comece por **Super Mario 3D Land**. Abra o jogo normalmente e pressione **START + SELECT + A**; solte os três botões. O resultado esperado é o menu de guia. Esse resultado ainda precisa ser confirmado no console.
7. **A** abre; **B** volta; D-Pad/Circle Pad ou toque navegam. No índice, **X** busca; numa página, **X** marca conclusão e **Y** alterna favorito; **L/R** mudam página. Mapas oferecem botões de pan e **L/R** para zoom.
8. Em Configurações, ajuste hotkey, spoilers, toque, logging e última página. O logging vem **OFF**. Diagnóstico mostra versão, Title ID, Game ID, páginas e informações de heap. O guia PT-BR independe da região do jogo.
9. Para sair, pressione **B** no menu ou selecione **Voltar ao jogo**. Preferências/progresso ficam na pasta do guia; o plugin não escreve no save do jogo.

Caso ocorra travamento, desligue o console antes de remover o SD. Desative o Plugin Loader no Rosalina ou renomeie `default.3gx` para `default.3gx.disabled` no computador. Segurar **R** ao iniciar o jogo tenta pular a inicialização do overlay; esse mecanismo também **não foi testado em hardware** e não impede falhas anteriores à entrada do plugin.

Ao atualizar, faça backup do progresso. O ZIP não inclui `config.bin` nem arquivos binários de `state/`, portanto não os sobrescreve. A versão 0.2 lê configuração 0.1; a 0.1 não lê o novo formato UGC2. Para reverter, restaure também o backup da configuração. A migração dos seis pilotos usa IDs de páginas preservados.

O pacote de teste usa arquivos de progresso `state/test-pt-BR-<game-id>.bin`, separados da versão completa. Para passar ao pacote completo, extraia o novo ZIP; o arquivo VERSION troca o perfil. Arquivos de teste antigos podem permanecer no SD sem interferir.

Fontes, ferramentas, testes e documentação de desenvolvimento estão no SOURCE.zip separado. Avisos de licença e atribuição necessários acompanham o instalador. O plugin não baixa conteúdo ou executáveis.
