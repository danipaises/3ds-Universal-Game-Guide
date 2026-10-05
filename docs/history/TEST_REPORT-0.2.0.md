> Histórico do relatório anterior ao teste #1. Superado pelo crash em hardware informado em 2026-10-05; consulte [reteste](../../HARDWARE_RETEST.md).

# Relatório de testes — 0.2.0-alpha — 2026-10-04

**NOT TESTED ON REAL HARDWARE — NÃO TESTADO EM HARDWARE REAL.** Esta etapa não executou overlay em emulador. Resultados abaixo são de PC, análise de fonte e compilação; não comprovam boot, touch, pausa ou retomada no console.

| Verificação | Resultado observado |
|---|---|
| Baseline oficial | SOURCE/PTBR extraídos separadamente, hashes preservados e 1.604 arquivos próprios coincidentes. Os 17 testes Python originais, core e build ARM passaram antes dos incrementos. |
| Python / Builder | **31 testes passaram, zero falharam.** Catálogo/IDs, JSON duplicado, evidência, traversal/symlink, campos/UTF-8, texto/asset grande ou inválido, idioma/pacote vazio, seções/revisão, CRC, busca vinculada, migração, conteúdo de teste reduzido, licença, links e pacote sem sobrescrever estado. |
| Core C++ | C++20 com -Wall/-Wextra/-Werror e ASan/UBSan. **67 packs, 2.151 páginas e todos os 211 IDs** lidos. Lookup, idioma/fallback, busca, spoilers, favoritos/conclusão, config UGC1/UGC2 e hotkeys com direções opostas/diagonal, log limitado/falha de escrita, migração real e mapeamento inválido, mapas ausentes/corrompidos e rejeição de corrupção passaram. |
| Leitura limitada | Maior leitura individual instrumentada: **175.344 bytes**. Busca Charizard com menos de 40 leituras. Não é medição de RAM, latência ou FPS do 3DS. A busca usa índice gerado; o teste não varre textos do SD por consulta. |
| Lint | Ruff 0.14.14 e formatação de 17 arquivos Python passaram; ClangFormat 21.1.8 conferiu fontes C++ próprias. Bash validado sintaticamente. Actionlint 1.7.12 validou os três workflows, sem achados; checks shellcheck/pyflakes do actionlint foram desabilitados, com Ruff/Bash executados separadamente. |
| ARM / .3gx | **Sucesso** com imagem devkitPro fixada, devkitARM r68-1/GCC 16.1.0, libctru 2.7.0 e CTRPF 0.8.0. Magic 3GX$0002; **374.305 bytes**. Código próprio usa warnings como erro; warnings upstream continuam registrados. |
| Reconstrução completa | Duas execuções --clean recompilaram SDK, libs de áudio e plugin, com hash igual. Além disso, SOURCE extraído em pasta temporária vazia, dependências restauradas do bundle, testes e build completo passaram e produziram o mesmo .3gx. Isso não certifica todos os hosts/toolchains futuros. |
| Runtime completo | 203 arquivos, 202 hashes internos, 67 packs/2.151 páginas, 211 IDs, 249.895 registros de busca no total e 45 tiles. SHA-256, CRCs, vínculos, ordenação e caminhos conferidos. Sem código-fonte, scripts, toolchain, testes ou estado/configuração de usuário no ZIP. |
| Hardware-Test | 75 arquivos, seis packs/78 páginas, 22 IDs únicos/31 associações regionais, 4.963 registros de busca e 45 tiles. Mapas e três sondas da Pokédex por versão preservados; nenhuma Pokédex completa. Progresso de teste isolado. |
| SOURCE | Fonte própria, dados, guias, ferramentas, CI e bundle upstream separados. Seis archives upstream conferidos por hash, sem ELF/.3gx/cache dentro do SOURCE. Reconstrução independente executada. |
| Title IDs | 279 associações rechecadas diretamente contra seis snapshots com hashes: 166 cross-checked, 112 single-source, uma CHN NEEDS_VERIFICATION. São 211 IDs únicos. Tretta Lab permanece sem ID-base. Metadados comunitários não comprovam região oficial completa nem compatibilidade física. |
| Assets | Oito PNGs originais, nove mapas por jogo, hashes/licenças/limites validados. Os três novos esquemas foram inspecionados visualmente. Não há arte de terceiros sem licença redistribuída. Esquemas indicam objetivos; não são plantas completas das salas. |
| Links | 18 locais acessíveis. 251 URLs externas consultadas: 186 acessíveis, 65 bloqueadas por HTTP 403, zero 404/410. Bloqueio é pendência de acesso, não confirmação de conteúdo. Pesquisa factual também utilizou páginas disponíveis pela ferramenta web. |
| GitHub Actions | Workflows de PR/build, links e release por tag/manual preparados e lintados localmente. **Não executados no GitHub e nenhuma release publicada**: repositório remoto não informado. |

Comando principal: `UGG_LSAN=0 UGG_PYTHON=.venv/bin/python bash scripts/test.sh`. LeakSanitizer não inicia sob ptrace neste ambiente; ASan/UBSan permaneceram ativos. Em CI normal LSan fica habilitado. São 31 testes distintos, independentemente das repetições e da execução pelo SOURCE.

Hash do plugin:

```text
a1014ecf2f79c4666511b18291a51201175e7dd5e8d9609e7cd732d9eefafe8e
```

A primeira tentativa adicional de build sem acesso ao socket Docker falhou por permissão; foi reexecutada com autorização. A tentativa de rebuild usando make -B acionou o clone upstream de libcwav e falhou. O modo --clean final remove somente artefatos ARM e usa fontes já fixadas. Essas tentativas não foram contadas como sucesso.

A nova distribuição runtime tem aproximadamente 1,53 MiB comprimidos, contra 6,80 MiB do instalador anterior: redução de 77,5%, com mais conteúdo. A referência exata dos ZIPs é `dist/SHA256SUMS.txt`; regenerar relatórios de desenvolvimento altera o hash do SOURCE, sem alterar o executável.

## Pendências materiais

Todos os modelos, boot/loader, bypass R, hotkey, touch/teclado, font PT-BR em console regional, pausa/retorno, som, HOME/tampa/sono, pico de heap, memória estendida/MODE3, interação com plugins específicos e SD cheio/perda de energia continuam **sem teste real**. Guardas e backups não são prova de recuperação física. Não foram simuladas falhas de alocação no SDK antes/depois da guarda de heap. Logs não registram crashes anteriores à inicialização.

Conteúdo: **zero completos, 67 parciais e um ausente**. O volume de fichas não substitui walkthroughs, itens e colecionáveis ainda faltantes. [Lacunas exatas](../../CONTENT_GAPS.md), [cobertura](../../COVERAGE.md), [auditoria do plugin](../PLUGIN_AUDIT_0.2.md), [checklist físico](../HARDWARE_TEST_CHECKLIST.md).

A interface é nativa de 3DS; Playwright/DevTools não foram apresentados como teste do overlay. A sondagem de emulador registrada na etapa 0.1 é histórica e não valida este binário.
