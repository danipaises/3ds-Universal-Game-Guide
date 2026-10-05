# Emulação

Azahar é a alternativa open source atual pesquisada; a release consultada é 2126.1.2. Sua infraestrutura possui loader 3GX, mas há um relato de falha em Linux no próprio repositório. Suporte do emulador não significa compatibilidade confirmada deste plugin.

O AppImage oficial foi baixado e conferido com o digest publicado: SHA-256 `1ea15020334ee2e8fd16fbb3911fa7eafa8111e311c54dd4387b61b2ea742df6`. O runtime de AppImage falhou inicialmente num caminho com espaços; extrair em `/tmp/ugg-azahar-2126` permitiu iniciar. A conexão gráfica precisou de execução fora do sandbox, com perfil isolado do projeto.

O projeto criou `tests/emulator/main.c`, compilado em `.3dsx` com libctru 2.7.0. Duas sondagens de 12/15 segundos iniciaram o processo de emulação. O log da última confirmou `System_PluginLoader: true` e `System_PluginLoaderAllowed: true`, mas também `Failed to find title id for ROM (Error 0)` e `unknown / unimplemented function ConfigureNew3DSCPU`. Não houve log do marcador de 60 frames. O processo foi encerrado pelo timeout; não contar boot completo, renderização ou retorno como aprovados.

O [código do loader desta release](https://github.com/azahar-emu/azahar/blob/2126.1.2/src/core/hle/service/plgldr/plgldr.cpp) exclui aplicações com a entrada padrão de homebrew. O `.3dsx` de teste não reproduz um título comercial nativo nem valida a injeção do overlay. **O plugin não foi testado com sucesso em emulador.** Nenhuma ROM, CIA comercial ou arquivo de sistema proprietário foi baixado. Os testes C++ em PC não emulam pausa, GSP ou FS do console.

Para um teste autorizado com software adequado e obtido legalmente: consulte a documentação oficial da versão instalada; habilite seu loader 3GX, coloque os arquivos na pasta SDMC emulada e registre Title ID, versão do emulador/renderer, logs e resultados. Faça a matriz de input, spoilers e retorno ao jogo. Esta etapa não substitui Old e New 3DS reais. A fixture própria serve somente para sondar o ambiente e é distribuída como fonte, fora do runtime instalável.

Referências: [release oficial](https://github.com/azahar-emu/azahar/releases/tag/2126.1.2), [issue #1125](https://github.com/azahar-emu/azahar/issues/1125), [FAQ oficial](https://azahar-emu.org/pages/faq/).
