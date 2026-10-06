# Instalar o teste Universal Game Guide 0.2.2-alpha

**ALPHA — REAL HARDWARE TESTED / FULL PARTIAL PASS.** A 0.2.2 passou em MINIMAL-BOOT/MINIMAL e boot/UI/guia/retorno do FULL no Old Nintendo 3DS + Luma 13.1.1. **Pesquisa Offline e Configurações provocam ARM11 crash: evite essas opções.** Não é versão estável. Os ZIPs históricos preservam rótulos antigos de reteste.

1. Desligue o console e faça backup do SD e de qualquer plugin existente.
2. Extraia **UniversalGameGuide-PTBR-Hardware-Test-v0.2.2-alpha.zip** na raiz do SD, sem criar pasta extra. O plugin ficará em `luma/plugins/default.3gx`.
3. Siga [HARDWARE_RETEST.md](HARDWARE_RETEST.md) para ativar Plugin Loader e iniciar Super Mario 3D Land.
4. Primeiro teste **MINIMAL-BOOT**: o jogo deve iniciar sem interface ou hotkey do guia. Depois de desligar, confira `3ds/UniversalGameGuide/logs/boot-stage.txt`. Esse resultado passou no console do teste #3; cada nova build ou outro ambiente precisa de reteste.
5. Apenas após confirmação, substitua default.3gx com o MINIMAL de diagnostics; depois teste FULL. As instruções explicam a troca e os resultados esperados de cada variante.

Em caso de crash, pare, preserve dump/foto/log/BUILD.json e desative o Plugin Loader ou mova default.3gx para o backup com o console desligado. Confira também plugins específicos por Title ID. Não restaure automaticamente o plugin antigo que já falhou.

ELF/MAP ficam no **Debug-Symbols.zip do computador**, nunca no SD. SOURCE.zip contém desenvolvimento separado. O instalador não contém config.bin nem arquivos de progresso binários: não sobrescreve o estado existente nem modifica saves do jogo. Logging normal continua OFF; o marcador de boot é limitado e específico desta build de teste.
