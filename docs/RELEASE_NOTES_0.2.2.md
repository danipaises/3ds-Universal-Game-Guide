# 3DS Universal Game Guide v0.2.2-alpha — Hardware Retest

**ALPHA / PRE-RELEASE / Stable: NO.** Versão histórica de teste. Evidência física relatada pelo testador: **Old Nintendo 3DS + Luma3DS 13.1.1**, Super Mario 3D Land, Title ID `0004000000053F00`.

| Variante / função | Resultado real |
|---|---|
| MINIMAL-BOOT | PASS — jogo iniciou sem ARM11 crash |
| MINIMAL | PASS — boot, hotkey, interface, Title ID e B para voltar |
| FULL boot / main UI | PASS |
| Hotkey / game detection / guide / navegação básica / retorno ao jogo | PASS |
| Offline Search | **FAIL — ARM11 CRASH** |
| Settings | **FAIL — ARM11 CRASH** |
| FULL overall | **PARTIAL PASS** |
| Mapas, salvamento de configurações, abertura repetida, HOME/sono/swap | Ainda não validados fisicamente |

**Bugs conhecidos:** Pesquisa Offline e Configurações provocam crashes em hardware. Evite essas duas opções durante uso normal. Dumps separados A (Search) e B (Settings) ainda são necessários; nenhuma causa comum é presumida. Esta versão não está estável e o FULL não foi aprovado integralmente.

## Download e instalação

TESTADOR / USUÁRIO: baixe somente **UniversalGameGuide-PTBR-Hardware-Test-v0.2.2-alpha.zip**. Faça backup do SD e do plugin existente, desligue o console, extraia na raiz do SD e ative o Plugin Loader no Rosalina. O ZIP instala MINIMAL-BOOT primeiro: sem overlay/hotkey. Com o console desligado, copie `diagnostics/default-minimal.3gx` e depois `diagnostics/default-full.3gx` para `luma/plugins/default.3gx`, conforme o reteste controlado. No MINIMAL/FULL, **START + SELECT + A** abre a interface e B volta. Há seis guias piloto parciais.

**Não instale Debug-Symbols.zip nem SOURCE.zip no SD.** São arquivos de desenvolvimento/diagnóstico. ELF/MAP ficam separados. Em caso de problema, desligue e mova `luma/plugins/default.3gx` para o backup ou desative o Plugin Loader; confira plugins específicos por Title ID que tenham prioridade. Não apague saves/configurações.

## Procedência preservada

Tag `v0.2.2-alpha` → commit **e3b78dc3611530ee0a9d667bc7961c057a51ad9f**. Os três ZIPs foram recuperados do [CI original concluído](https://github.com/danipaises/3ds-Universal-Game-Guide/actions/runs/37365978186), sem regeneração: hashes iguais aos da entrega anterior. SOURCE conferido contra todos os 2.477 arquivos versionados desse commit, mais o bundle upstream.

Classificação: **HARDWARE-TESTED**, conforme relato do testador sobre versão e variantes; a confirmação criptográfica do arquivo instalado no SD ainda está pendente. **CI-REBUILT** fica reservado a novas compilações, que nunca substituem silenciosamente estes assets. Antes de simbolizar os próximos dumps, confirmar o SHA-256 do FULL instalado e o BUILD.json/ELF/MAP exatos.

Os ZIPs históricos contêm rótulos `NEEDS HARDWARE RETEST` anteriores ao teste, inclusive na tela MINIMAL e em BUILD.json. Permanecem intactos para preservar identidade. As notas desta Release e a documentação da main registram o resultado posterior. MINIMAL exibiu heap newlib de 8.172.600 bytes e boot log result 00000000; isso é observação relatada, não medição de RAM livre nem motivo para aumentar memória.

SHA-256 dos plugins preservados:

```text
MINIMAL-BOOT 7167f564c2ed90c08d09ee8b35654e3ddabf34801e2192590b3f5d82afe1405a
MINIMAL      ec3ab2ad151710d08cbef4ae579e36c4dc7be560deb8a532a6170c2c156fc238
FULL         ea96f45a5f870f1e9ba0b3916a177b88be6794ed82e9ba387bc28fb358b0d702
```

SHA-256 dos downloads:

```text
6a90982412d9a18d6beecfe123a18385610ae55fc953f3fb4bd788fd9d9d603e  UniversalGameGuide-PTBR-Hardware-Test-v0.2.2-alpha.zip
f7a370c526f648a71a923a2341636b513d0dadeef55e97094b2283e677a5f9db  UniversalGameGuide-Debug-Symbols-v0.2.2-alpha.zip
d60bc06ac6ff993584b030a745d593cb65ae28cd626aa1e1eb372c7a22b877ae  3DS-Universal-Game-Guide-SOURCE-v0.2.2-alpha.zip
```

A correção da ABI de heap permite inicialização nas variantes testadas. Isso não demonstra que todos os crashes foram corrigidos. A próxima versão só será preparada após analisar os dois dumps e criar regressões; nenhum número de versão foi alterado nesta etapa.
