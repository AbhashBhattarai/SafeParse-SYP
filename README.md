# SafeParse

SafeParse is a compiler I am writing in Python for my final-year project.
It reads a short spec file that describes a binary format (for example a UDP header)
and generates a memory-safe C parser from it.
A web interface with a database and login is also planned.

## Research question

How much faster is a C parser that merges consecutive bounds checks into a single
check compared to one that checks before every individual field read,
and does the merged version stay exactly as safe?

## Planned pipeline

```
spec file → lexer → parser → semantic checker → optimizer → code generator → C parser
```

Each step is a small, independent Python module so each part can be studied,
tested, and replaced without touching the others.

## Development plan

Code is added in small batches over the year as each part is studied, rebuilt,
tested, and verified:

| Batch | Contents |
| ----- | -------- |
| B1 | Project proposal, ERD, wireframes, UDP spec, skeleton |
| B2 | Lexer and lexer tests |
| B3 | Parser, semantic checker and their tests |
| B4 | Optimizer, code generator, CLI and their tests |
| B5 | Generated C headers and correctness harness |
| B6 | Web application and web tests |
| B7 | Differential fuzzing harnesses |
| B8 | Benchmark, results and experiment log |
| B9 | Learning guide, evaluation and paper draft |

## Status

- [x] Project proposal, ERD and wireframes
- [x] UDP spec (`specs/udp.spec`)
- [ ] Lexer
- [ ] Parser and semantic checker
- [ ] Optimizer and code generator
- [ ] C correctness harness
- [ ] Web application
- [ ] Fuzzing harnesses
- [ ] Benchmark and results
- [ ] Documentation and paper

## Honesty note

Parts of the implementation were generated with AI assistance and are being
studied, rebuilt, tested, and verified by me.
All evaluation results will come from my own runs with raw logs kept.

## How to run

Coming with the first code batch.

## Folder layout

```
docs/       wireframes and ERD
specs/      binary format spec files (plain text)
safeparse/  Python compiler source (added in later batches)
```

## Author

AbhashBhattarai — github.com/AbhashBhattarai
