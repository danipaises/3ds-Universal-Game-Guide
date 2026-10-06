# Search e Settings — preparação para dumps físicos

Base examinada: `809dc8b2a8b61f62c46714c2c2615aa745393bc5`, VERSION 0.2.2-alpha. Consulta em 2026-10-06. CTRPF 0.8.0 fixado em `a502818c7586179d320caf8e897238d3491b5a29`; fontes locais obtidas com os hashes de `data/dependencies.lock.json`.

**Nenhuma causa raiz foi confirmada.** Relato físico: Old Nintendo 3DS / Luma 13.1.1 / Super Mario 3D Land / 0004000000053F00. MINIMAL-BOOT/MINIMAL PASS; FULL PARTIAL PASS; Search e Settings ARM11 CRASH. Os dumps A e B e o hash instalado ainda faltam. **Esta preparação não foi testada em hardware real.**

## Caminhos e lifetimes

| Aspecto | Offline Search | Settings |
|---|---|---|
| Entrada UGG | `overlay()` opção 2 ou X; `pageList(..., true)` → X → `searchGuide()` | `overlay()` opção 5; tela sem guia → opção 2 → `settings()` |
| UI CTRPF | `Keyboard keyboard(text)`, `SetMaxLength(64)`, `Open(query)` em QWERTY | `options` com nove strings → `choice(title, options)` → `Keyboard k(title, items)` → `Open()` com opções |
| Retorno/cancelamento | `Open != 0` retorna antes do core; query local copiada pelo SDK | índice negativo não aciona nenhuma opção; alterações só após `choice` retornar |
| Core | `guide.search(query, config.spoilers, matches)`; depois `pageList(matches, label)` | alterações em `config` global; validação da hotkey via encode/decode de objetos locais |
| SD | `.ugs` associado ao `.ugg`, cabeçalho UGS2/fingerprint/tamanho; lower_bound e blocos de até 256 × 68 bytes | carregamento em `main()`, antes da hotkey; persistência em `saveBeforeReturn()` ao fechar o overlay, não ao entrar em Settings |
| Escrita | nenhuma escrita do índice; progresso/config e eventual log ao fechar o overlay | `config.bin` 32 bytes; `.tmp`/`.bak` na camada SD. Falhas de escrita oferecem retry/retorno |

Os dois caminhos vivem dentro de `PauseGuard` do overlay. O SDK `KeyboardImpl::Run()` consulta `ProcessImpl::IsPaused` e só solicita pausa própria se necessário; não mudar essa interação sem analisar PC/LR e fonte fixada. `SystemImpl`/Controller/OSD/renderer/input/fonte/serviços do CTRPF são compartilhados. Nem QWERTY nem a lista de opções fazem parte do MINIMAL; o PASS do MINIMAL não valida esses componentes.

Não há `MenuEntry`/`MenuFolder`, callbacks de menu ou `SetCompareCallback`/`OnKeyboardEvent` próprios de UGG nesses caminhos. O cleanup de `overlay` é o destrutor local `ReleasePages`; a lambda de `splitLines` captura referências locais e roda sincronamente antes do retorno. Lambdas do core (`field`, deduplicação de páginas) são chamadas síncronas de algoritmos, não callbacks guardados pelo SDK.

`Keyboard` possui `std::unique_ptr<KeyboardImpl>` no header fixado. O destrutor de Keyboard tem corpo vazio, mas a destruição do membro libera o impl. O impl copia o texto; `Populate` cria `TouchKeyString`, que possui sua própria `std::string _content`, e o destrutor do impl deleta essas teclas. O ponteiro `_owner` aponta para o Keyboard ainda vivo durante `Run`. Callbacks `_compare`/`_onKeyboardEvent` são inicializados a nullptr pelos construtores examinados. As opções de Settings ficam vivas durante `choice`; temporários de título sobrevivem à chamada síncrona. Isso não demonstra ausência de erros em todos os caminhos internos do SDK.

`query`, `matches`, opções e teclados são objetos locais; seus objetos de controle usam stack e conteúdos/impl usam heap. A busca mantém `guide.pages` global; `matches` vive durante a chamada síncrona `pageList`. `ReleasePages` libera páginas/linhas/body ao sair do overlay. Não foi identificada uma referência local explicitamente retida por UGG depois desse retorno. Pico de stack/heap, OOM e buffers do SDK em hardware continuam UNKNOWN.

## Limites, hipóteses e evidência necessária

O core rejeita consulta vazia/curta, UTF-8 inválido, índice ausente, tamanho/fingerprint incorreto, contagem excessiva, strings sem NUL e páginas fora do limite. O índice é offline e não lê conteúdo comercial nem memória específica do jogo. Busca por prefixo pode produzir múltiplas páginas; spoilers são filtrados. Settings lê UGC1/UGC2 com CRC, valida hotkey/idioma/flags e escreve UGC2. Preferências inválidas não são aplicadas pelo decode.

Um componente compartilhado é **Keyboard/KeyboardImpl**, porém Search usa QWERTY e Settings usa Populate/lista. Registrar como área de investigação, não como causa comum. Também examinar renderer/event loop/fonte e orçamento de stack/heap se os dumps apontarem para eles. O código de arquivos/índice só é alcançado após o teclado de Search retornar; o arquivo de config não é lido ao entrar em Settings. O relato atual não informa a primeira instrução que falha em cada fluxo.

Testes nativos cobrem o core/Storage em PC e o logger com stubs. Não vinculam Keyboard/renderer/loader do CTRPF. Não simular esse SDK com stubs inventados para declarar uma correção de lifetime ou de UI. Ciclos de objetos do core e config são regressões de dados; Search → Back → Search e Settings → Back → Settings in-game continuam pendentes.

## Instrumentação existente e plano condicionado

Reusar `UGGBootStage`/`UGGBootResult` em `boot.cpp`, sem segundo logger. Buffer fixo BSS 3 KiB, até 40 writes, label até 160 caracteres, SD apenas após FS, falha interrompe writes. Logging normal vem OFF. `recorded` grava cada estágio apenas uma vez por processo; saturação, FS inválido ou marcador antigo tornam ausência de estágio inconclusiva.

Search hoje registra estágio decimal 23 (`0x17`) **depois de Keyboard::Open**, antes da busca, e 24 (`0x18`) depois dela. Não registra construtor/Open nem retorno do resultado/Back. Settings não possui checkpoints dedicados. Os stages 16/17 do FULL indicam entrada do main/config carregada, não abertura de Settings.

Não alterar o runtime histórico antes de obter os dumps. Se um novo probe for justificado, inserir somente chamadas com labels literais, sem montar strings/alocar por frame. Plano de IDs ainda não implementado:

| ID decimal | Label / posição futura |
|---|---|
| 28 | SEARCH_STAGE_01 antes do construtor Keyboard |
| 29 | SEARCH_STAGE_02 após construtor/SetMaxLength, antes de Open |
| 30 | SEARCH_STAGE_03 após Open, inclusive cancelamento |
| 31 | SEARCH_STAGE_04 após retorno da lista de resultados |
| 32 | SETTINGS_STAGE_01 antes de montar opções |
| 33 | SETTINGS_STAGE_02 antes do construtor em choice |
| 34 | SETTINGS_STAGE_03 após construtor, antes de Open |
| 35 | SETTINGS_STAGE_04 após Open |
| 36 | SETTINGS_STAGE_05 antes de config write em save |
| 37 | SETTINGS_STAGE_06 após tentativa de config write |

Verificar IDs livres, limite de writes e FS antes de implementar. Registrar Result/retorno com `UGGBootResult`, sem query, nomes pessoais ou dumps no log. Uma variante instrumentada terá hashes próprios, ELF/MAP/BUILD.json próprios e necessidade de novo reteste; nunca reutilizar aprovação física do binário histórico. Não aumentar memória nem modificar pausa/loader por hipótese.

## Receber e analisar A e B separadamente

1. Preservar dump bruto privado/ignorado, nome original e SHA-256. Identificar A — Offline Search ou B — Settings e ação exata (abrir teclado, digitar, confirmar, voltar, salvar etc.). Guardar foto, boot-stage e modelo/Luma/Title ID.
2. Confirmar SHA-256 do `default.3gx` instalado no SD e comparar ao trio FULL do pacote usado. Conferir version, commit, variant, hashes 3GX/ELF/MAP e toolchain antes de addr2line. O manifest schema 1 histórico não informa todos os campos novos: completar a conferência com [procedência histórica](RELEASE_PROVENANCE_0.2.2.json), lock e evidência da toolchain; não inventar campos nem substituir o manifest por uma recompilação atual.
3. FULL histórico: 3GX `ea96f45a5f870f1e9ba0b3916a177b88be6794ed82e9ba387bc28fb358b0d702`; ELF `5bd2c9d1c0c4a6c0b99c3fed5036bd40186f6b427366f5f8840de33675dec1b6`; MAP `288c46577ad93bfe95fc8497956fecab0fccf1767cdaac98f82096381f9a3c38`. Tag e3b78dc; VERSION 0.2.2-alpha. Bytes equivalentes não mudam a identidade histórica do manifest.
4. Usar a ferramenta atual conforme [HARDWARE_RETEST](../HARDWARE_RETEST.md), passando ELF, MAP, plugin, manifest e hash instalado confirmados. Ela rejeita hashes divergentes; a conferência de commit/versão/toolchain é adicional e obrigatória, não é validada integralmente por `verify_identity`.
5. Registrar Title ID, tipo de exceção, acesso, PC/LR/SP/CPSR e registradores relevantes. O parser atual entrega exceptionType numérico e registradores, mas não decodifica access type; confirmar acesso pela foto e instrução/fault metadata disponível. Se não determinável: UNKNOWN. Não inferir Write apenas por analogia ao crash 0.2.1.
6. Resolver PC/LR somente quando dentro do ELF correspondente. Stack words são **candidatos**, não backtrace confirmado; o PC já vem ajustado pelo Luma. Explicitar função/arquivo/linha UNKNOWN quando símbolos ou endereço não permitirem resolução. Examinar cada dump antes de comparar possíveis pontos comuns.

Após causa demonstrada: correção mínima, regressões, novo build/mesmo commit de artefatos e reteste. Só então preparar 0.2.3-alpha. Checklist em [HARDWARE_RETEST](../HARDWARE_RETEST.md). Nenhum dump real foi recebido nesta preparação.

## Release workflow revisado

`release.yml` reutiliza `build.yml`. Checkout oficial sem ref explícita usa o evento da tag (`GITHUB_SHA`); valida VERSION/tag/HEAD. PC executa pytest, Ruff, Builder, core/boot ASan/UBSan em GCC 13/14. ARM usa imagem por digest, recompila três ELF/MAP, produz 3GX, verifica ABI e gera bundle/instalador/símbolos/SOURCE. BUILD.json schema 2 identifica mesmo commit, dirty=false, toolchain, dependências e hashes. `release_assets.py` confere todos os arquivos versionados do SOURCE contra commit e recusa símbolos misturados/checksums inválidos.

Publish tem contents:write somente nesse job, baixa o artifact do SHA, prepara assets locais, recusa Release existente, cria draft com --verify-tag, baixa/confere SHA256SUMS e só então publica. Alpha/beta/rc usam --prerelease (qualquer sufixo SemVer é prerelease). Dispatch na main não publica. O Builder anteriormente recusava rc; a regressão desta preparação corrige essa divergência sem mudar VERSION ou workflow.

Release v0.2.2-alpha consultada em 2026-10-06: prerelease=true, draft=false, tag histórica e3b78dc; notas já declaram os dois crashes e FULL PARTIAL PASS. Nada alterado remotamente. Não houve publicação/execução remota de workflow nesta preparação. Futuras tags ainda exigem validação do run real; inspeção estática não comprova um publish futuro.
