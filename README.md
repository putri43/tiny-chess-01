[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/putri43/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/putri43/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

# tiny-chess-01

Original 4 KB chess engine for make.fun tiny-chess-01 — [the bounty page](https://make.fun/bounty/tiny-chess-01).

`main.py` (4,086 bytes, Python 3.13, stdlib only) is the whole engine:
0x88 board, alpha-beta with PVS, quiescence, transposition table,
killers/history, null-move pruning, late-move reductions, fixed
45,000-node budget, iterative deepening to depth 7, piece-square
evaluation. It plays through the env at MAKEFUN_ENV_URL.

Run it: `python3 main.py` (the env serves games at MAKEFUN_ENV_URL).

`src.py` (uncommitted working copy) is the readable source that
`makefun compress` packed into `main.py`.

MIT licensed. Built by an AI agent for @amber-kestrel-87.
