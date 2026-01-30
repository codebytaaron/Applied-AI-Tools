# erlang-incident-update

Erlang CLI template that drafts incident status updates.

This repo is intentionally written in **Erlang** (not Python/JS) so GitHub shows a different language mix.

## Run
```bash
erlc main.erl
erl -noshell -s main main -s init stop
```

## Input format
Put your notes in `input.txt` (or pipe stdin). Output is printed to stdout.
