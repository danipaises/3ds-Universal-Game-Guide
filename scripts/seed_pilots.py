#!/usr/bin/env python3
"""Initial, original PT-BR pilot content. Refuses to overwrite contributor edits."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(gid, sources, pages):
    base = ROOT / "guides/pt-BR" / gid
    if (base / "guide.json").exists():
        raise SystemExit(f"{gid}: já existe; editar o guia, não reexecutar o seed")
    base.mkdir(parents=True, exist_ok=True)
    index = []
    for ident, title, body, refs, spoiler, mapid in pages:
        file = ident + ".md"
        (base / file).write_text("# " + title + "\n\n" + body.strip() + "\n", encoding="utf-8")
        p = {"id": ident, "title": title, "file": file, "spoiler": spoiler, "sources": refs}
        if mapid:
            p["map"] = mapid
        index.append(p)
    metadata = {
        "schemaVersion": 1,
        "gameId": gid,
        "language": "pt-BR",
        "coverage": "pilot-partial",
        "license": "CC-BY-4.0",
        "pages": index,
    }
    (base / "guide.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    ss = [
        {
            "title": title,
            "url": url,
            "retrieved": "2026-10-04",
            "use": "Consulta de fatos; redação própria. Arte e texto da fonte não redistribuídos.",
        }
        for title, url in sources
    ]
    (base / "sources.json").write_text(json.dumps(ss, ensure_ascii=False, indent=2) + "\n")
    (base / "SOURCES.md").write_text(
        "# Fontes e autoria\n\nTexto original do projeto, CC BY 4.0. Referências consultadas em 04/10/2026; nenhum mapa ou captura dessas páginas foi copiado. Cada página declara seus índices de fontes em guide.json. Recomendações práticas são síntese editorial.\n\n"
        + "".join(f"- [{i}: {s['title']}]({s['url']})\n" for i, s in enumerate(ss))
        + "\nCobertura parcial: a lista de lacunas está na primeira página do guia.\n"
    )


def p(i, t, b, refs=(0,), s=False, m=""):
    return (i, t, b, list(refs), s, m)


write(
    "super-mario-3d-land",
    [
        (
            "Manual eletrônico Nintendo",
            "https://www.nintendo.com/eu/media/downloads/games_8/emanuals/nintendo_3ds_2/super_mario_3d_land/ElectronicManual_Nintendo3DS_SUPERMARIO3DLAND_EN.pdf",
        ),
        ("World 1-1", "https://www.mariowiki.com/World_1-1_(Super_Mario_3D_Land)"),
        ("World 1-2", "https://www.mariowiki.com/World_1-2_(Super_Mario_3D_Land)"),
        ("World 1-3", "https://www.mariowiki.com/World_1-3_(Super_Mario_3D_Land)"),
        ("World 1-4", "https://www.mariowiki.com/World_1-4_(Super_Mario_3D_Land)"),
        ("Special 1-Castle", "https://www.mariowiki.com/Special_1-Castle"),
        ("Completion", "https://www.mariowiki.com/Completion#Super_Mario_3D_Land"),
        ("Boom Boom", "https://www.mariowiki.com/Boom_Boom#Super_Mario_3D_Land"),
        ("Pom Pom", "https://www.mariowiki.com/Pom_Pom#Super_Mario_3D_Land"),
        ("Star Medal", "https://www.mariowiki.com/Star_Medal"),
    ],
    [
        p(
            "comecando",
            "Começando e cobertura",
            """Este piloto contém controles, as três Star Medals das fases 1-1 e 1-2, objetivos de conclusão e referências de chefes. O mapa é um roteiro esquemático, sem escala.

Ainda faltam os percursos de cada fase dos mundos 2–8 e Special, posições de todas as medalhas e estratégias da fase final. Portanto este guia não é um walkthrough completo.

Consulte uma fase por vez. Y cria um favorito; X marca a página consultada como concluída. Essas marcas não conferem o save de Mario.""",
        ),
        p(
            "controles",
            "Controles",
            """Circle Pad: mover. A/B: saltar. X/Y: correr e usar a habilidade disponível. L/R: agachar; no ar, realizar o ataque ao chão. Segurar o salto com Tanooki permite planar.

A tela inferior permite usar o item de reserva. O jogo salva após concluir uma fase; volte ao mapa antes de encerrar. Prefira guardar uma Super Leaf para trechos com plataformas estreitas.

A combinação do guia pode também ser recebida pelo jogo antes da pausa. Evite acioná-la no meio de um salto.""",
        ),
        p(
            "world-1-1",
            "1-1: percurso e três Star Medals",
            """Pegue a Super Leaf nos primeiros blocos e avance pelas pontes. Suba o trecho elevado; a engrenagem escondida nos blocos responde à cauda Tanooki. Os binóculos perto do fim ajudam a visualizar o mastro.

Medalha 1: corda sobre o rio, na segunda área de terra.
Medalha 2: perto do checkpoint, suba a árvore e use os Note Blocks para alcançar o cano; procure entre os blocos grandes da sala.
Medalha 3: corda entre as plataformas, antes da ilha do mastro.

Faça a coleta e o topo do mastro em tentativas separadas se necessário.""",
            (1,),
            m="world-1-1",
        ),
        p(
            "world-1-2",
            "1-2: percurso e três Star Medals",
            """Mantenha distância das bolas com corrente. A Fire Flower facilita lidar com as plantas, mas observe também o movimento das plataformas.

Medalha 1: atrás da roda que gira, depois da primeira curva à direita.
Medalha 2: sobre uma plataforma móvel, após a segunda bola com corrente.
Medalha 3: no fim do caminho estreito junto às plantas, além da ponte com correntes.

Atalho: perto dos Koopas, use um salto agachado a partir de um bloco para alcançar a borda superior. Siga à direita até o cano que leva ao World 2. Este atalho não completa as fases puladas.""",
            (2,),
            s=True,
        ),
        p(
            "colecionaveis",
            "Star Medals: organizar a coleta",
            """Cada fase comum tem três Star Medals. Observe os símbolos no mapa de seleção antes de repetir uma fase. Mystery Boxes também podem fornecer medalhas; por isso o total acumulado sozinho não identifica uma fase incompleta.

Algumas passagens exigem um total mínimo. Registre a fase com uma medalha faltando, prepare o power-up e volte a ela, em vez de procurar sem referência em todos os mundos.""",
            (0, 9),
        ),
        p(
            "boom-boom",
            "Chefe: Boom Boom",
            """Espere o giro terminar e salte na cabeça durante a abertura. Quando ele recolher os braços, afaste-se; insistir em pular durante o giro aumenta o risco de dano. Repita a sequência de espera e ataque, cuidando das mudanças de arena e de comportamento nas lutas posteriores.""",
            (7,),
            True,
        ),
        p(
            "pom-pom",
            "Chefe: Pom Pom",
            """Evite os projéteis e aproxime-se quando ela estiver vulnerável. Depois do golpe, rec recue para não receber o contra-ataque. Nas arenas com plataformas móveis ou espaço menor, priorize o pouso seguro antes de atacar.""".replace(
                "rec recue", "recue"
            ),
            (8,),
            True,
        ),
        p(
            "luigi",
            "Desbloquear Luigi",
            """Conclua Special 1-Castle para resgatar e desbloquear Luigi. Depois escolha o personagem no mapa. A troca não apaga as medalhas obtidas.

Para a conclusão máxima, registre as fases terminadas com cada irmão; o objetivo de terminar com os dois é separado da coleta.""",
            (5, 6),
            True,
        ),
        p(
            "cinco-estrelas",
            "Cinco estrelas e fase final",
            """Objetivos do arquivo:
- Vencer World 8-Bowser’s Castle (2).
- Concluir as fases dos mundos normais.
- Concluir Special 8-Castle e vencer novamente World 8-Bowser’s Castle (2).
- Obter as 285 Star Medals das fases regulares.
- Terminar as fases com Mario e Luigi e alcançar todos os topos dos mastros.

As cinco estrelas abrem Special 8-Crown. Para estrelas brilhantes, não pode ter aparecido o Assist Block: ele surge após cinco mortes numa fase, mesmo que você não use a ajuda. Não confunda esse requisito com apenas evitar a White Tanooki Leaf.""",
            (6,),
            True,
        ),
        p(
            "faq",
            "FAQ e checklist",
            """O guia sabe em qual fase estou? Não. “Continuar” abre somente a última página consultada.

Posso usar PT-BR em uma cópia japonesa? Sim: a seleção do idioma do guia é independente da região cadastrada.

Marcar X completa a fase? Não. É uma anotação no SD; não altera o save.

Checklist por fase: três medalhas, topo do mastro, conclusão com Mario, conclusão com Luigi. A página atual pode ser favoritada para voltar depois.""",
            (0, 6),
        ),
    ],
)
write(
    "luigis-mansion-dark-moon",
    [
        ("Luigi’s Mansion: Dark Moon", "https://www.mariowiki.com/Luigi%27s_Mansion:_Dark_Moon"),
        ("Gloomy Manor", "https://www.mariowiki.com/Gloomy_Manor"),
        ("Haunted Towers", "https://www.mariowiki.com/Haunted_Towers"),
        ("Old Clockworks", "https://www.mariowiki.com/Old_Clockworks"),
        ("Secret Mine", "https://www.mariowiki.com/Secret_Mine"),
        ("Treacherous Mansion", "https://www.mariowiki.com/Treacherous_Mansion"),
        ("Boo em Dark Moon", "https://www.mariowiki.com/Boo#Luigi.27s_Mansion:_Dark_Moon"),
    ],
    [
        p(
            "comecando",
            "Começando e cobertura",
            """Luigi’s Mansion 2 e Dark Moon identificam a mesma aventura de 3DS. Este guia organiza as mansões, os controles, os sistemas de captura e o planejamento da coleção.

Ainda faltam soluções sala a sala, os 65 percursos das gemas e estratégias detalhadas de cada missão e chefe. Não é um walkthrough completo. Use o checklist como acompanhamento manual, sem leitura do save.

O mapa mostra a sequência das mansões; não é uma planta dos cômodos.""",
            m="mansions",
        ),
        p(
            "controles",
            "Lanterna, Poltergust e Dark-Light",
            """Circle Pad move Luigi. R aspira; L sopra. A carrega o Strobulb, cuja luz atordoa fantasmas. Y usa o Dark-Light para revelar objetos ocultos. X interage ou olha para cima; B olha para baixo e ajuda a correr ou esquivar conforme a situação.

Atordoe primeiro, aspire depois e puxe contra o movimento do fantasma. Procure uma janela segura para carregar o ataque. A tela inferior mostra o mapa; START abre a pausa do jogo.""",
        ),
        p(
            "gloomy-manor",
            "Gloomy Manor: reconhecimento",
            """A primeira mansão introduz equipamentos e exploração. Na missão inicial procure o Poltergust 5000; depois a história apresenta o Strobulb e o Dark-Light.

Volte a salas já visitadas após conseguir o Dark-Light. Objetos que desapareceram deixam pistas no ambiente. Confira portas e escadas no mapa antes de subir ou descer.

A primeira peça da Dark Moon é protegida pelo Grouchy Possessor. Depois da luta, compare o total de gemas da mansão com as 13 posições da coleção.""",
            (1,),
        ),
        p(
            "haunted-towers",
            "Haunted Towers: exploração vertical",
            """As torres introduzem uma estrutura mais vertical e vegetação que interfere no percurso. Quando um caminho parece terminar, confira andares e conexões no mapa.

Observe plantas e elementos que respondem ao Poltergust. A mansão tem sua própria série de 13 gemas; as coletadas na primeira mansão não contam aqui.

Harsh Possessor encerra a sequência principal da região.""",
            (2,),
            True,
        ),
        p(
            "old-clockworks",
            "Old Clockworks: engrenagens e tempo",
            """A fábrica exige atenção às máquinas, ao relógio e aos caminhos que ligam diferentes pisos. Antes de acionar um mecanismo, observe o que muda na sala para conseguir voltar.

Aspiração e sopro podem interagir de maneiras diferentes com objetos. Se um trajeto abrir, registre a sala de origem no mapa para retomar a busca de itens.

Overset Possessor é o chefe desta mansão.""",
            (3,),
            True,
        ),
        p(
            "secret-mine",
            "Secret Mine: gelo e profundidade",
            """A mina troca a exploração ampla por setores menores com gelo e desníveis. Examine a ligação entre o chalé e os trechos subterrâneos no mapa.

Mantenha espaço para reagir aos ataques e não trate o piso escorregadio como uma superfície comum. Antes de sair de uma sala, confira objetos revelados pelo Dark-Light.

Shrewd Possessor guarda a peça desta região. A coleção também reúne 13 gemas.""",
            (4,),
            True,
        ),
        p(
            "treacherous-mansion",
            "Treacherous Mansion: reta final",
            """A última mansão reúne salas de exposição e ameaças de diferentes tipos. Faça um reconhecimento das conexões entre alas antes de enfrentar uma missão com pressão de tempo.

Reutilize as técnicas de atordoar, remover proteção e puxar contra o fantasma. Durante sequências de combate, preservar vida costuma ser mais útil do que interromper a captura para recolher uma moeda isolada.

A campanha aproxima-se da conclusão após as missões desta mansão. Não confunda o chefe da mansão com a batalha final da história.""",
            (5,),
            True,
        ),
        p(
            "boos",
            "Boos e Dark-Light",
            """Para localizar um Boo, procure objetos invisíveis e use o Dark-Light. Recolha os Spirit Balls para restaurar o objeto. Depois acompanhe o Boo e aproveite a abertura para capturá-lo.

Os Boos da mansão contribuem para liberar sua missão bônus. Consulte a coleção e repita a missão apropriada; o marcador do guia apenas registra sua própria anotação.""",
            (6,),
            True,
        ),
        p(
            "colecao",
            "Coleção e metas de conclusão",
            """Cada uma das cinco mansões possui 13 gemas: 65 ao todo. Planeje a busca por mansão e acompanhe as lacunas da coleção.

Metas distintas: concluir a campanha; conseguir três estrelas nas missões; completar a coleção do Vault, incluindo gemas, Boos, upgrades e fantasmas pertinentes. ScareScraper possui conteúdo próprio e depende de suas regras e disponibilidade de participantes.

Este guia ainda não apresenta a localização individual de cada gema nem um checklist completo dos fantasmas.""",
            (0, 1, 2, 3, 4, 5),
            True,
        ),
        p(
            "dicas",
            "Quando uma sala parece bloqueada",
            """Confira o andar, a missão atual e o mapa. Tente o Dark-Light se houver um objeto ausente ou uma marca estranha. Observe se o mecanismo reage ao sopro ou à aspiração.

Um objeto relevante pode exigir interação de perto. Uma porta aparentemente inacessível pode ter acesso pelo piso vizinho. Marque a página da mansão como favorita e retome a busca ao conseguir um novo equipamento.""",
        ),
    ],
)
write(
    "kirby-triple-deluxe",
    [
        ("Kirby: Triple Deluxe", "https://wikirby.com/wiki/Kirby:_Triple_Deluxe"),
        ("Fine Fields", "https://wikirby.com/wiki/Fine_Fields"),
        ("Lollipop Land", "https://wikirby.com/wiki/Lollipop_Land"),
        ("Old Odyssey", "https://wikirby.com/wiki/Old_Odyssey"),
        ("Wild World", "https://wikirby.com/wiki/Wild_World"),
        ("Endless Explosions", "https://wikirby.com/wiki/Endless_Explosions"),
        ("Royal Road", "https://wikirby.com/wiki/Royal_Road"),
        ("Sun Stone", "https://wikirby.com/wiki/Sun_Stone"),
        ("Completion", "https://wikirby.com/wiki/100%25_completion#Kirby:_Triple_Deluxe"),
        ("Controls", "https://strategywiki.org/wiki/Kirby%3A_Triple_Deluxe/Controls"),
    ],
    [
        p(
            "comecando",
            "Começando e cobertura",
            """Este guia apresenta a sequência de regiões, Sun Stones, Hypernova e metas de 100%. O desenho mostra a progressão em Floralia, sem copiar os mapas do jogo.

Ainda faltam as posições de todas as Sun Stones e Rare Keychains, percursos de cada fase e estratégias completas dos modos extras. Cobertura de piloto, parcial.""",
            m="floralia",
        ),
        p(
            "controles",
            "Movimento e habilidades",
            """Circle Pad/D-Pad: mover. A: saltar; saltos repetidos permitem flutuar. B: aspirar ou usar a Copy Ability; com algo na boca, B cospe e baixo engole. L/R: proteger-se; combine com a direção para esquivar quando a habilidade permitir.

Os golpes mudam conforme a habilidade. Confira o tutorial e a lista de comandos antes de descartar uma habilidade útil para um puzzle.""",
            (9,),
        ),
        p(
            "hypernova",
            "Hypernova e profundidade",
            """Miracle Fruit ativa Hypernova, que substitui temporariamente a habilidade atual e permite aspirar objetos enormes. Explore tanto o primeiro plano quanto o fundo: a mudança de camada é parte dos puzzles.

Ao encontrar um obstáculo, observe o objeto inteiro e a direção em que ele pode se mover. Hypernova dura até o fim da fase; não é uma habilidade comum para levar livremente a outra fase.""",
        ),
        p(
            "fine-fields",
            "Fine Fields",
            """A primeira região apresenta os elementos básicos de plataforma e alternância entre planos. O chefe é Flowery Woods. Recolha as Sun Stones necessárias para abrir a porta do chefe e volte depois para as que ficaram faltando.

Antes de sair por uma porta, examine passagens laterais e objetos que exigem uma habilidade. Não confunda um Keychain comum com a Sun Stone necessária à progressão.""",
            (1,),
        ),
        p(
            "lollipop-land",
            "Lollipop Land",
            """O segundo conjunto de fases leva a Paintra. A região exige observar o cenário e separar elementos de fundo de caminhos realmente acessíveis.

Para buscar colecionáveis, faça uma tentativa de exploração em vez de correr direto à saída. Preservar a habilidade certa pode ser necessário para interagir com um objeto próximo de uma porta.""",
            (2,),
        ),
        p(
            "old-odyssey",
            "Old Odyssey",
            """Kracko encerra a terceira região. Planeje os saltos e mudanças de plano antes de avançar para uma porta de passagem única.

Se perder a habilidade necessária a um puzzle, confira inimigos próximos antes de abandonar a coleta. A indicação de Sun Stones na seleção da fase ajuda a saber se vale repetir o trecho.""",
            (3,),
        ),
        p(
            "wild-world",
            "Wild World",
            """A quarta região culmina em Coily Rattler. Observe caminhos alternativos e mecanismos; a rota mais evidente pode levar somente à saída.

Em confrontos, priorize reconhecer a sequência do ataque. Flutuar evita alguns perigos de chão, mas não substitui a esquiva quando o chefe ataca o espaço aéreo.""",
            (4,),
        ),
        p(
            "endless-explosions",
            "Endless Explosions",
            """A quinta região leva ao confronto com Pyribbit. Observe onde o chefe vai reaparecer e não se aproxime de um ataque só para manter o dano contínuo.

Revise as Sun Stones faltantes antes da reta final. Quando um objeto puder ser aspirado com Hypernova, espere uma oportunidade segura para iniciar a ação.""",
            (5,),
        ),
        p(
            "royal-road",
            "Royal Road",
            """Esta região tem 16 Sun Stones. A distribuição nas fases normais é: 6-1 = 3; 6-2 = 1; 6-3 = 3; 6-4 = 1; 6-5 = 4. A fase de chefe exige sete pedras anteriores da região e a conclusão de 6-5.

As fases EX possuem três pedras em 6-7 EX e uma em 6-8 EX. Em Story Mode a sequência de chefes inclui Masked Dedede e Queen Sectonia. Dededetour muda a sequência e os adversários; não use uma descrição de Story Mode como solução automática desse modo.""",
            (6,),
            True,
        ),
        p(
            "sun-stones",
            "Sun Stones e fases EX",
            """Há 100 Sun Stones. A porta do chefe de cada região exige uma quantidade local; o total de pedras de outra região não substitui essa exigência.

Colete todas as pedras anteriores da região para liberar a fase EX correspondente. Royal Road tem uma segunda fase EX acessível após a primeira. Os ícones da seleção mostram o que ficou para trás; repita a fase com foco na pedra que falta.""",
            (7,),
            True,
        ),
        p(
            "cem-por-cento",
            "Checklist de 100%",
            """- Vencer Flowered Sectonia em Story Mode.
- Obter 100 Sun Stones e os 256 Keychains.
- Concluir Dededetour.
- Concluir The Arena e The True Arena.
- Completar todos os estágios de Dedede’s Drum Dash, incluindo Distant Traveler.
- Concluir o modo Single Player de Kirby Fighters com cada uma das dez habilidades, em qualquer dificuldade.

Uma etapa marcada no guia é apenas uma anotação. O percentual oficial é calculado pelo próprio jogo.""",
            (8,),
            True,
        ),
    ],
)
write(
    "zelda-ocarina-of-time-3d",
    [
        (
            "Walkthrough e objetivos por capítulo",
            "https://www.zeldadungeon.net/ocarina-of-time-walkthrough/",
        ),
        (
            "Inside the Great Deku Tree",
            "https://www.zeldadungeon.net/ocarina-of-time-walkthrough/inside-the-great-deku-tree/",
        ),
        (
            "Forest Temple",
            "https://www.zeldadungeon.net/ocarina-of-time-walkthrough/forest-temple/",
        ),
        (
            "Ocarina of Time 3D — Nintendo",
            "https://www.nintendo.com/en-gb/News/2011/A-legend-returns-in-magical-3D-this-June-252755.html",
        ),
    ],
    [
        p(
            "comecando",
            "Começando e cobertura",
            """Este piloto cobre o início em Kokiri Forest, a primeira dungeon e o acesso ao Forest Temple. A sequência geral é um lembrete de objetivos; não substitui soluções sala a sala.

Ainda faltam mapas de dungeons, os 36 Heart Pieces, as 100 Gold Skulltulas, a cadeia de trocas e percursos detalhados dos templos seguintes. Master Quest tem puzzles diferentes: as soluções abaixo são para a aventura normal.

O mapa é um esquema dos primeiros objetivos, sem escala geográfica.""",
            (0, 1, 3),
            m="first-objectives",
        ),
        p(
            "controles",
            "Usar o inventário do 3DS",
            """Organize os itens na tela inferior antes de entrar em uma dungeon. Use a mira e o travamento de alvo para observar o inimigo, defender e atacar durante a abertura.

No 3DS, a tela de toque reduz o número de interrupções para trocar equipamento. Confira o manual e o esquema exibido no próprio jogo: os botões da versão Nintendo 64 citados em walkthroughs antigos não correspondem diretamente aos do 3DS.

Guarde o jogo com frequência. Fechar o guia não salva sua aventura.""",
            (3,),
        ),
        p(
            "kokiri",
            "Kokiri Forest: espada e escudo",
            """Mido só libera o caminho quando Link tem espada e escudo. Vá à área de treino, atravesse o pequeno túnel e contorne a pedra que rola para chegar ao baú da Kokiri Sword.

Recolha 40 Rupees e compre o Deku Shield na loja. Equipe os dois itens e volte a Mido. Aprenda a defesa e o travamento de alvo antes de entrar na Great Deku Tree.""",
            (1,),
        ),
        p(
            "deku-tree",
            "Deku Tree: roteiro inicial",
            """Suba pela sala central para encontrar o mapa e alcançar a sala do Fairy Slingshot. Use o estilingue para criar o caminho de volta, acertar alvos e remover inimigos nas paredes.

Procure a Compass na área superior. Do alto, salte sobre a teia central para rompê-la e alcançar o subsolo. Use Deku Sticks acesos para queimar teias; controle o tempo da chama.

Mais adiante, reflita as sementes dos Deku Scrubs. Na sala dos três, a ordem é 2–3–1. A informação recebida abre o caminho ao chefe.""",
            (1,),
            True,
        ),
        p(
            "gohma",
            "Queen Gohma",
            """Trave o alvo no olho. Quando ele ficar vermelho, use o Slingshot ou uma Deku Nut para atordoar e ataque com a espada. Ao subir ao teto, observe outra janela com o olho exposto, em vez de apenas esperar os filhotes.

Após vencer, pegue o Heart Container antes de usar a saída luminosa. O contêiner do chefe é separado dos Heart Pieces encontrados fora das dungeons.""",
            (1,),
            True,
        ),
        p(
            "primeiros-objetivos",
            "Da floresta ao Temple of Time",
            """A rota principal passa pelas três pedras espirituais: Kokiri’s Emerald, Goron’s Ruby e Zora’s Sapphire. As dungeons correspondentes são Deku Tree, Dodongo’s Cavern e Jabu-Jabu’s Belly.

Depois obtenha a Ocarina of Time e avance ao Temple of Time para chegar à Master Sword. Este resumo não cobre os puzzles intermediários nem indica que os locais ficam imediatamente acessíveis.""",
            (0,),
            True,
        ),
        p(
            "hookshot",
            "Hookshot: obter e usar",
            """Como adulto, visite o cemitério de Kakariko e faça a corrida com o fantasma de Dampé para obter o Hookshot. Ele permite prender-se a superfícies apropriadas, atingir alvos e recolher tokens fora do alcance.

Depois vá ao Sacred Forest Meadow. Toque Saria’s Song para Mido liberar a passagem nos Lost Woods. Na entrada do Forest Temple, use o Hookshot no galho sobre a escadaria.""",
            (2,),
            True,
        ),
        p(
            "forest-temple",
            "Forest Temple: pontos de orientação",
            """Na sala inicial, suba as vinhas e salte entre os galhos para encontrar uma Small Key. No salão principal, as quatro Poe Sisters retiram as chamas: restaurá-las é um objetivo central.

O Fairy Bow permite acionar os olhos e mudar corredores. Para acessar a Boss Key, use o arco no olho prateado acima da porta da sala dos blocos; o corredor deixa de ficar torcido e abre um novo caminho.

Este é um resumo de orientação, não uma sequência completa de todas as chaves.""",
            (2,),
            True,
        ),
        p(
            "adulto",
            "Templos da aventura adulta",
            """Objetivos de equipamento e chefe:
- Forest Temple: Fairy Bow; Phantom Ganon.
- Fire Temple: Megaton Hammer; Volvagia.
- Water Temple: Longshot; Morpha.
- Shadow Temple: Hover Boots; Bongo Bongo.
- Spirit Temple: Mirror Shield; Twinrova.

Ice Cavern e Bottom of the Well fornecem recursos úteis à progressão. Volte a áreas anteriores com o equipamento novo para procurar colecionáveis. Este guia ainda não descreve os percursos desses templos.""",
            (0,),
            True,
        ),
        p(
            "colecionaveis",
            "Colecionáveis e acompanhamento",
            """Existem 36 Heart Pieces e 100 Gold Skulltulas. Quatro Heart Pieces formam um contêiner; os Heart Containers dos chefes são obtidos separadamente.

Anote local, idade de Link e período do dia ao encontrar um token inacessível. Alguns objetivos exigem retornar como criança ou adulto.

Este piloto não contém a lista individual completa. Marcar esta página como concluída não confirma que sua coleção chegou a 100%.""",
            (1, 2),
            True,
        ),
    ],
)
write(
    "pokemon-x",
    [
        (
            "Walkthrough X/Y, índice",
            "https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pok%C3%A9mon_X_and_Y/",
        ),
        (
            "Início e Santalune",
            "https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pok%C3%A9mon_X_and_Y/Part_2",
        ),
        (
            "Lumiose e Camphrier",
            "https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pok%C3%A9mon_X_and_Y/Part_3",
        ),
        (
            "Liga",
            "https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pok%C3%A9mon_X_and_Y/Part_15",
        ),
        (
            "Pós-game",
            "https://bulbapedia.bulbagarden.net/wiki/Walkthrough:Pok%C3%A9mon_X_and_Y/Part_16",
        ),
        ("Mega Evolution", "https://bulbapedia.bulbagarden.net/wiki/Mega_Evolution"),
        ("Breeding", "https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_breeding"),
    ],
    [
        p(
            "comecando",
            "Começando e cobertura",
            """Este guia cobre a sequência principal de cidades e rotas, o início em Santalune e sistemas de batalha. A Pokédex factual é consultada por espécie; os dados de X e Y aparecem identificados.

Ainda faltam puzzles e treinadores de todos os trechos, locais de todos os itens/TMs, eventos e disponibilidade por presentes, trocas e Friend Safari. Encontros selvagens listados não representam todos os métodos de obtenção.

Não há necessidade de serviço online para consultar o guia. Recursos do jogo que dependiam de serviços encerrados não são restaurados pelo plugin.""",
            m="kalos-route",
        ),
        p(
            "batalhas",
            "Equipe e batalhas",
            """Mantenha diferentes tipos na equipe para enfrentar os ginásios. Considere o tipo do golpe e os tipos defensivos do alvo: um Pokémon com dois tipos pode receber dano multiplicado por ambos.

Antes de uma sequência longa, cure a equipe e reponha itens. Um golpe de mesmo tipo do usuário recebe STAB; a vantagem de tipo não garante vitória se houver grande diferença de nível.

As fraquezas da Pokédex mostram somente a tabela de tipos, sem imunidades fornecidas por habilidades, itens ou efeitos de campo.""",
        ),
        p(
            "santalune",
            "Rotas 2–4 e Santalune",
            """Route 2 e Santalune Forest introduzem captura e variedade de tipos. Fletchling ajuda contra Bug; Pikachu pode aparecer na floresta e na Route 3, mas não é um encontro garantido.

Em Santalune, vença o confronto na entrada do ginásio para receber os patins. O ginásio de Viola tem Surskit, Bug/Water, e Vivillon, Bug/Flying. Fire não é uma resposta universal contra a equipe por causa do tipo Water de Surskit.

Após a primeira insígnia, Alexa fornece o Exp. Share. Ajuste sua utilização conforme a equipe que deseja treinar e siga pela Route 4.""",
            (1,),
        ),
        p(
            "rota-principal",
            "Roteiro de Kalos: primeira metade",
            """Vaniville → Route 1 → Aquacorde → Route 2 → Santalune Forest → Route 3 → Santalune.

Depois: Route 4 → Lumiose sul → Route 5 → Camphrier. Visite Route 6 e Parfum Palace antes de prosseguir pela Route 7 e Connecting Cave.

Continue por Route 8, Ambrette, Route 9 e Glittering Cave. A parte inferior da Route 8 leva a Cyllage. Routes 10 e 11, Geosenge e Reflection Cave levam a Shalour.

A ordem indica a progressão principal; não substitui os eventos que abrem cada passagem.""",
        ),
        p(
            "rota-final",
            "Roteiro de Kalos: segunda metade",
            """Shalour → Route 12 → Coumarine → Route 13 e Power Plant → Lumiose.

Depois: Route 14 → Laverre e Poké Ball Factory → Route 15 → Dendemille → Frost Cavern → Route 17 → Anistar.

Resolva os eventos de Team Flare em Lumiose e Geosenge. Continue por Route 18, Couriway e Route 19 até Snowbelle. Route 20 e Pokémon Village antecedem o último ginásio. Routes 21 e 22 e Victory Road levam à Liga.""",
            s=True,
        ),
        p(
            "ginasios",
            "Ginásios: planejar a cobertura",
            """Santalune — Viola: Bug.
Cyllage — Grant: Rock.
Shalour — Korrina: Fighting.
Coumarine — Ramos: Grass.
Lumiose — Clemont: Electric.
Laverre — Valerie: Fairy.
Anistar — Olympia: Psychic.
Snowbelle — Wulfric: Ice.

Cheque os tipos secundários das espécies e não dependa só da especialidade do líder. Distribua funções de ataque e cura entre a equipe.""",
            s=True,
        ),
        p(
            "liga",
            "Elite Four e Champion",
            """A Elite Four de Kalos reúne Malva (Fire), Siebold (Water), Wikstrom (Steel) e Drasna (Dragon). Você escolhe a ordem das quatro salas; entrar em uma batalha encerra aquela escolha até vencê-la.

Leve recuperação de HP e PP e golpes com cobertura variada. Depois das quatro vitórias, enfrente Diantha. A equipe da Champion não segue um único tipo; sua Gardevoir pode Mega Evoluir.""",
            (3,),
            True,
        ),
        p(
            "mega",
            "Mega Evolutions",
            """Mega Evolution é temporária e ocorre durante a batalha. O treinador precisa dos recursos apropriados e o Pokémon deve segurar sua Mega Stone. Apenas uma Mega Evolution pode ser usada por batalha.

Charizard possui duas formas Mega, associadas a pedras diferentes. As formas e habilidades mudam; não use a tabela defensiva do Charizard normal para interpretar a forma Mega.

A lista completa de pedras e seus locais ainda precisa ser adicionada a este guia.""",
            (5,),
            True,
        ),
        p(
            "breeding",
            "Breeding: preparar um objetivo",
            """O Day Care da Route 7 permite criar Eggs com parceiros compatíveis. Defina se deseja obter uma espécie, natureza, habilidade ou Egg Move antes de montar os pais.

Itens como Everstone e Destiny Knot ajudam no planejamento da herança. Faça a coleta e a eclosão com espaço livre na equipe. IVs, habilidades e movimentos são sistemas distintos: um resultado favorável em um deles não garante todos os demais.

Este piloto ainda não descreve todos os grupos de ovos nem cada regra de herança de X/Y.""",
            (6,),
        ),
        p(
            "pos-game",
            "Após a Liga",
            """Volte a Vaniville e explore os novos objetivos de Lumiose e Kiloude. Battle Maison e Friend Safari são sistemas diferentes: a primeira organiza batalhas, enquanto o segundo depende dos amigos cadastrados e das condições de desbloqueio.

Há uma sequência de missões do Looker e uma melhoria do Mega Ring. Registre o objetivo atual em um favorito. O guia ainda não contém o passo a passo dessas missões.""",
            (4,),
            True,
        ),
        p(
            "faq",
            "FAQ: espécie, rota e progresso",
            """Pesquise o começo do nome: “Charizard”, “Pikachu” ou “Route 2”. A busca ignora maiúsculas e acentos comuns do português. Termos de pelo menos duas letras evitam listas muito amplas.

As páginas de espécies informam a forma normal, a geração dos dados e as limitações. Sem encontro selvagem listado não significa que a espécie seja impossível de obter.

Uma anotação de progresso no guia não altera equipe, itens, Pokédex ou save do jogo.""",
        ),
    ],
)
print("Cinco pilotos originais criados. Editar arquivos Markdown para continuar.")
