# RogueCraft

Trabalho desenvolvido para a disciplina de Laboratório de Programação de Jogos
do curso de Ciência da Computação (UFF, 2026.1).

Autor: Rodrigo Fernandes Ribeiro

## Sobre o jogo

RogueCraft é um jogo de sobrevivência em ondas com câmera em vista de cima. A
cada onda nascem inimigos ao redor do jogador, que precisa sobreviver enquanto
coleta recursos espalhados pelo chão. Com os recursos é possível craftar
projéteis mais fortes. Ao limpar uma onda, o jogador escolhe uma entre três
cartas (um novo projétil, um recurso para desbloquear ou uma bênção passiva).
A cada cinco ondas surge um chefe. A partida termina quando a vida do jogador
chega a zero.

A única dependência externa é a biblioteca PPlay, fornecida pela disciplina, que
encapsula o pygame. Todo acesso a teclado, mouse, imagem, som e tela passa pela
PPlay; o jogo não chama o pygame diretamente.

## Como executar

Requisitos: Python 3 e pygame instalado (utilizado internamente pela PPlay).

Na raiz do projeto, execute:

```
python main.py
```

### Controles

- WASD: movimentação.
- Mouse: mira; clique esquerdo atira. Segurar o botão carrega um tiro especial.
- ESPACO: dash na direção do movimento.
- 1 / 2 / 3: escolhem uma das três cartas entre as ondas.
- ENTER: inicia a partida e reinicia após o fim de jogo.
- ESC: sai.

## Arquitetura

O loop principal (`main.py`) é curto e funciona como uma máquina de estados
(`menu`, `playing`, `choosing`, `game_over`). Ele lê o `delta_time`, calcula a
câmera e delega a lógica da partida ao `WaveManager`. As entidades de mundo
herdam de `GameObject` (PPlay), que fornece posição, tamanho e teste de colisão.

Mapa resumido dos arquivos:

- `main.py`: loop do jogo, máquina de estados e cálculo da câmera.
- `entity/player.py`: movimentação, dash, ataque, i-frames e animação.
- `entity/wave_manager.py`: orquestra ondas, spawn, colisões e fim de onda.
- `entity/enemy/`: `Enemy` base e variantes (melee, ranged lento, ranged rápido, chefe).
- `entity/projectile/`: `Projectile` base, tiers do jogador e projéteis dos inimigos.
- `entity/resource/`: `Resource` base e os recursos (madeira, pedra, ferro, cristal, ouro).
- `entity/passives/`: bênçãos de velocidade, fúria e vitalidade.
- `entity/inventory.py`: estoque de recursos, projétil equipado e auto-craft.
- `entity/hud.py`: vida, recursos, cartas de escolha, popups e menus.
- `entity/environment.py`: chão infinito, vegetação procedural e chuva.
- `entity/music_manager.py`: troca a trilha conforme a fase da partida.
- `entity/loaders.py`: configuração centralizada de sprites e sons.
- `PPlay/`: motor fornecido pela disciplina.

## Detalhes de implementação

### Câmera e coordenadas

Não há uma classe de câmera. Existe apenas o par `(cam_x, cam_y)`, calculado em
`main.py` a partir da posição do jogador (`cam_x = player.x - largura/2`) e
repassado a quem desenha. Todo objeto do mundo aparece na tela pela regra
`tela = mundo - câmera`. Como a câmera deriva da posição do jogador, ele fica
sempre fixo no centro e é o mundo que rola por baixo. As colisões acontecem todas
em coordenadas de mundo.

### Movimento, projéteis e independência de FPS

O padrão que se repete em quase todo o jogo é
`posição += direção * velocidade * dt`. A direção é sempre normalizada, ou seja,
transformada em um vetor de comprimento 1: calcula-se a distância pelo teorema de
Pitágoras (`math.sqrt(dx*dx + dy*dy)`) e dividem-se as componentes por ela. Assim
a velocidade fica igual em qualquer ângulo. A diagonal do WASD e as salvas do
chefe usam o fator `0.7071` (`1/raiz(2)`), o componente de um vetor unitário a 45
graus. Multiplicar pelo `dt` torna o deslocamento independente da taxa de quadros.

Os projéteis seguem movimento retilíneo com velocidade constante e um `lifetime`
que decrementa por `dt`; o alcance efetivo é `velocidade * lifetime`. O projétil
não testa colisão sozinho: quem resolve projétil contra alvo é o `WaveManager`,
mantendo baixo acoplamento.

### Inimigos

`Enemy` é uma classe-base parametrizada (Template Method): a estrutura de mover,
animar, atirar e tomar dano fica na base, e cada subclasse apenas passa números no
construtor. O movimento parte sempre da direção normalizada até o jogador. Os
inimigos de longa distância mantêm o jogador a uma distância confortável de forma
simples: quando ficam mais perto do que a distância preferida, andam para trás (a
direção é invertida) em vez de colar nele. Por cima disso há uma separação leve,
que soma um empurrão para longe de cada vizinho muito próximo, evitando que os
inimigos se empilhem.

### Chefe

O `EnemyBoss` sobrescreve o update para rodar uma máquina de cinco estados
(hovering, descending, landing, attacking, vanishing) em ciclo, com sprite, regras
de dano e duração próprios por estado. Ao terminar de pairar, ele tira uma foto da
posição atual do jogador e desce em linha reta até esse ponto, usando o mesmo
padrão de movimento do resto do jogo (`posição += direção * velocidade * dt`).
Como o alvo fica congelado, dá para desviar saindo do lugar. O `WaveManager`
continua tratando o chefe como um `Enemy` qualquer, exemplo de polimorfismo.

### Recursos, inventário e auto-craft

Cada recurso coletável tem sprite, nome e chance de spawn. O `Inventory` guarda o
estoque por tipo, os recursos desbloqueados e o blueprint atual. Sempre que um
recurso é coletado ou um blueprint é escolhido, o inventário tenta craftar: se o
estoque cobre o custo, o projétil equipado passa a ser o novo e um popup avisa.
O projétil equipado é tratado como uma estratégia (Strategy): o jogador instancia
a classe equipada sem saber o tier.

### WaveManager

Costura tudo: faz o spawn de inimigos e recursos em círculo ao redor do jogador
(`cos`/`sin`), atualiza as entidades, resolve as colisões na ordem correta, poda
as listas (remove mortos, projéteis expirados e recursos fora da margem da tela) e
decide o fim da onda. A quantidade de inimigos e a escala de vida e dano crescem a
cada onda.

### Cenário procedural

O `EnvironmentRenderer` desenha um chão infinito calculando apenas os tiles
visíveis a partir da câmera. A vegetação é procedural e determinística: a decisão
do que nasce em cada tile é tomada uma única vez e guardada, de modo que a mesma
planta reaparece no mesmo lugar quando o jogador volta. A chuva é composta por
gotas e respingos em coordenadas de mundo, desenhados como o chão, de forma que o
jogador atravessa a chuva em vez de ela segui-lo.
