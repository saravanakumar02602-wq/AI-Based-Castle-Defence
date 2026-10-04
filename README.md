# AI Castle Defence

A Python and Pygame tower-defence game where a classical AI commander leads enemy troops through a grid battlefield toward your keep. Build and upgrade defensive towers, shape enemy routes with walls, and adapt your strategy as automatic assault waves grow stronger.

## Features

- **Classical AI decision-making:** knowledge representation, rule-based reasoning, state-space search, Minimax, and Alpha-Beta pruning.
- **A* pathfinding:** enemies navigate around terrain and player-built defences; the commander can re-evaluate routes as the battlefield changes.
- **Three tower types:** rapid single-target Archer, slowing Shadow Mage, and area-damage Heavy Cannon.
- **Active Meteor Strike:** target a battlefield area for a powerful attack; the ability recharges after five seconds.
- **Automatic waves and tactical rewards:** survive each assault to choose gold, gate repair, or a permanent tower-damage increase.
- **Veteran enemies:** from wave 16, enemy troops gain increasingly strong damage-absorbing shields.
- **Pygame presentation:** animated troops, visible projectiles, impact effects, sound effects, HUD, menus, and end-of-game screens.

## Requirements

- Python 3.10 or newer
- Pygame 2.6 or newer

The dependencies are listed in [`requirements.txt`](./requirements.txt).

## Installation

Open a terminal in the project directory and create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, run the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the game

From the project directory:

```powershell
python main.py
```

If using the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe main.py
```

Choose **Start Game** from the main menu. Waves begin automatically after the preparation period.

## How to play

### Build your defence

1. Choose a tower card in the HUD.
2. Left-click an open battlefield tile to build the selected tower.
3. Left-click an existing tower to upgrade it (up to Level 3).
4. Right-click a valid tile to build a wall. Right-click an existing wall to remove it.

| Defence | Cost | Damage | Range | Role |
| --- | ---: | ---: | ---: | --- |
| Archer Tower | 100 gold | 20 | 3 tiles | Fast, single-target attacks |
| Shadow Mage | 175 gold | 12 | 3 tiles | Slows enemies on impact |
| Heavy Cannon | 250 gold | 42 | 2 tiles | Area damage around the impact |
| Wall | 50 gold | — | — | Changes routes; cannot block every route to the keep |

Tower range is measured in grid steps. Towers can be upgraded twice; each upgrade increases damage and range.

### Manage resources and waves

- Start with **500 gold** and a keep with **250 integrity**.
- Earn gold from defeating enemies, passive income, and completing waves.
- After a wave, choose one reward: **+150 gold**, gate repair of up to **25% of maximum integrity**, or **+20% tower damage**.
- Enemy counts, health, damage, and movement speed increase as waves progress. Waves from 16 onward also add enemy shields and more frequent captains.
- Use **Meteor Strike** to damage nearby enemies. Its five-second cooldown starts after a valid strike.

### Controls

| Input | Action |
| --- | --- |
| Left-click tower card | Select a tower |
| Left-click open battlefield tile | Build the selected tower |
| Left-click an existing tower | Upgrade the tower |
| Right-click battlefield tile | Build or remove a wall |
| Left-click Meteor Strike, then battlefield | Choose and cast a Meteor Strike |
| `1`, `2`, `3` | Select Archer, Mage, or Cannon |
| `M` | Select or cancel Meteor Strike targeting |
| `P` | Pause or resume |
| `R` | Restart the game |
| `Esc` | Cancel Meteor targeting, or exit during gameplay |

## AI overview

Enemy decisions use the project's classical AI components rather than machine learning:

1. The **knowledge base** represents relevant game facts.
2. The **rule engine** identifies immediate actions such as changing route, attacking, or retreating.
3. **State-space reasoning**, **Minimax**, and **Alpha-Beta pruning** evaluate strategic choices.
4. **A*** searches the battlefield for a route, guided by a Manhattan-distance heuristic.

The AI implementation is primarily in [`ai/`](./ai/), with enemy decision orchestration in [`ai/commander.py`](./ai/commander.py).

## Run the tests

Run the automated AI regression suite from the project directory:

```powershell
python test.py
```

The suite checks heuristic calculations, A* route finding and obstacle handling, knowledge representation, state-space reasoning, rules, Minimax, Alpha-Beta pruning, terminal states, and state copying.

## Project layout

```text
.
├── ai/                 # Search, pathfinding, rules, and AI reasoning
├── battlefield/        # Grid, cells, and map layout
├── entities/           # Castle, enemies, and towers
├── systems/            # Waves, combat, resources, and game state
├── ui/                 # HUD and menus
├── main.py             # Application entry point
├── game.py             # Pygame loop and gameplay coordination
├── settings.py         # Window, grid, and gameplay settings
├── requirements.txt    # Python dependencies
└── test.py             # Automated AI regression suite
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`:** activate the virtual environment and run `python -m pip install -r requirements.txt`.
- **The game opens and closes immediately:** run `python main.py` from a terminal so any startup error remains visible.
- **No sound:** the game generates sound effects when Pygame's audio mixer is available; verify that the system has a working audio device.

## License

No license is currently specified. Ask the project owner before redistributing or reusing this project.