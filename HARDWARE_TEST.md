# Hardware Test — 0.2.2-alpha

0.2.0-alpha: TESTED ON REAL HARDWARE — FAIL, crash durante carregamento.

0.2.1-alpha MINIMAL: TESTED ON REAL HARDWARE — FAIL em CTRPF::__system_allocateHeaps, Old/Luma 13.1.1.

0.2.2-alpha: **REAL HARDWARE TESTED: MINIMAL-BOOT PASS, MINIMAL PASS, FULL PARTIAL PASS.** Old Nintendo 3DS + Luma 13.1.1 / Super Mario 3D Land. Pesquisa Offline e Configurações: **FAIL — ARM11 CRASH**, dumps separados pendentes. Veja HARDWARE_RETEST.md; mapas e outros fluxos ainda precisam de teste.

O instalador começa com MINIMAL-BOOT (sem interface/hotkey), depois MINIMAL e FULL. Siga [HARDWARE_RETEST.md](HARDWARE_RETEST.md) para backup, instalação, resultados esperados, recuperação e símbolos correspondentes.
