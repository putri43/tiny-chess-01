# tiny-chess-01

Original 4 KB chess engine for make.fun tiny-chess-01.

`main.py` (4,086 bytes, Python 3.13, stdlib only) is the whole engine:
0x88 board, alpha-beta with PVS, quiescence, transposition table,
killers/history, null-move pruning, late-move reductions, fixed
45,000-node budget, iterative deepening to depth 7, piece-square
evaluation. It plays through the env at MAKEFUN_ENV_URL.

`src.py` (uncommitted working copy) is the readable source that
`makefun compress` packed into `main.py`.

MIT licensed. Built by an AI coding agent for @amber-kestrel-87.
