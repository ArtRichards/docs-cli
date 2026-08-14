# Body links — every supported form, resolving

Lifecycle: active
Role: notes
Project: bodylink-clean
Updated: 2026-05-20

## Supported forms

One line per recognised form of the M27 grammar. Every destination below
resolves to an entry that exists in this tree, so the whole tree is clean.

- plain destination: [the target](target.md)
- dot-slash prefix: [the target](./target.md)
- fragment preserved, never validated: [a heading](target.md#a-heading)
- non-Markdown destination (Q7): [the data file](data.yaml)
- directory destination (Q7): [the subdirectory](sub/)
- nested destination: [the deep doc](sub/deep.md)
- angle destination: [the target](<target.md>)
- double-quoted title: [the target](target.md "The target")
- single-quoted title: [the target](target.md 'The target')
- parenthesised title: [the target](target.md (The target))

## Reference definition

A reference definition carries a destination of its own, so it is validated
even though the uses below never are.

[the-target]: target.md "The target"
