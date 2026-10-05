# Avisos de terceiros

O código original do plugin, Builder e testes usa MIT. As bibliotecas vinculadas e dados mantêm licenças distintas. A release distribui fontes próprias e `third-party-source.zip` no SOURCE.zip separado, com os arquivos originais fixados, patches e avisos. O instalador contém os avisos legais completos em LICENSES.txt; os dois ZIPs devem permanecer disponíveis juntos. As marcas Nintendo, Mario, Pokémon, Zelda e Kirby pertencem a seus titulares; não há afiliação oficial.

| Componente | Origem / versão | Licença / distribuição |
|---|---|---|
| CTRPluginFramework | The Pixellizer Group, 0.8.0 / a502818c | Licença própria de três condições; texto integral em docs/licenses/CTRPF.txt. Permite redistribuição e modificação sob suas condições. Não rotular o binário inteiro como MIT nem afirmar certificação OSI desta licença. Fonte fornecida junto do binário; derivação documentada. |
| Linker script 3gx.ld | CTRPF 0.8.0 | Mesmos avisos do upstream; não é criação original MIT. |
| libcwav | mariohackandglitch, 4fc8b11 | zlib, aviso no README original e docs/licenses/LIBCWAV.txt; som de menu desabilitado. Fonte é incluída porque a biblioteca faz parte do link do framework. |
| libncsnd | mariohackandglitch, 667cf998 | wxWindows Library License com exceção de link + notices zlib/libctru e LGPL2; texto integral em docs/licenses/LIBNCSND.md e fontes originais. |
| libctru | devkitPro, 2.7.0 | zlib; docs/licenses/LIBCTRU.txt. Fornecida pela imagem oficial de toolchain; fonte oficial disponível em github.com/devkitPro/libctru. |
| 3gxtool | The Pixellizer Group, 57e3160a | MIT no README; ferramenta de build, não executável instalado no console. O source archive preserva também avisos de headers como cxxopts. |
| yaml-cpp | jbeder, 0.8.0 | MIT, somente conversor de build; texto integral no source archive. |
| dynalo | maddouri, 411199d | MIT, somente conversor de build; texto integral no source archive. |
| PokéAPI | Paul Hallett e contribuidores, bc92d3b | BSD-3-Clause, texto integral em docs/licenses/POKEAPI-BSD-3-Clause.txt. Dados numéricos/nomes e tabelas históricas; sem flavor text, sprites ou imagens. Estrutura/notas próprias não eliminam essa atribuição. |
| Metadados de títulos | hax0kartik/3dsdb e 3dsdb.com | Fatos de identificação regional com URLs e hashes em title-id-evidence.json. Sem ROMs, descrições extensas ou arte desses bancos. Verificação de catálogo não é certificação de compatibilidade. |

Dependências de ambiente, compilador e runtimes padrão mantêm seus próprios avisos e exceções de vínculo. As fontes de CTRPF também contêm créditos e avisos de subcomponentes, preservados integralmente no archive; não removê-los ao redistribuir.
