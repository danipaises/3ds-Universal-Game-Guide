# Regras deste projeto

- Consulte também as instruções de desenvolvimento do usuário. Preserve trabalho existente.
- Não adicionar ROMs, CIAs comerciais, saves, chaves de console, firmware proprietário ou credenciais.
- O runtime lê somente dados limitados e lazy do SD; não usar JSON pesado, download online, AR codes, patches específicos ou inspeção de memória específica de jogo.
- Escritas ficam exclusivamente na pasta própria do projeto. Mudanças de pausa, HOME, sono ou protocolo do loader exigem revisão da fonte oficial fixada.
- Todo Title ID precisa de evidência identificável. Não inferir região nem transformar ID de update/DLC em ID-base.
- Registre cobertura editorial real em cada guide.json. Catálogo reconhecido, guia parcial e compatibilidade física são estados distintos.
- Produza prosa própria PT-BR. Fatos consultados têm SOURCES.md; assets precisam de autoria, licença, origem e SHA-256. Não copiar walkthroughs ou arte sem permissão.
- Execute Ruff, scripts/test.sh e o build ARM quando aplicáveis. Atualize docs/CTRPF_FILESYSTEM.patch via scripts/prepare_framework.py, nunca editando apenas .deps.
- Para pacote: bundle_sources.py, Builder package e verify_release.py. Fontes acompanham a release em SOURCE.zip separado; o ZIP do usuário não contém desenvolvimento. Confira licenças no runtime e que configuração/progresso de usuários não são sobrescritos pelo ZIP.
- Atualize PROJECT_STATUS.md e TEST_REPORT.md com evidência. Sem console físico: **Não testado em hardware real.** Compilação e testes do core não demonstram experiência in-game.
