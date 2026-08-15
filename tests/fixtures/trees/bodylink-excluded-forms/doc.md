# Body links — every excluded form, silent

Lifecycle: active
Role: notes
Project: bodylink-excluded-forms
Updated: 2026-05-20

## Forms outside the grammar (D1)

Not one of these names a destination the tool resolves, and every one of them
would resolve to nothing if it did — so any finding from this document is an
over-fire.

- image: ![a diagram](diagram.png)
- autolink, URL shaped: <https://example.com>
- autolink, path shaped: <plan.md>
- raw HTML anchor: <a href="plan.md">the plan</a>
- shortcut reference use: [plan]
- collapsed reference use: [plan][]
- full reference use: [x][plan]
- backslash-escaped opt-out: \[the plan](plan.md)

## Destination kinds that are never resolved (D2)

- empty: [nothing]()
- fragment only: [this section](#forms-outside-the-grammar-d1)
- schemed, https: [example](https://example.com/plan.md)
- schemed, mailto: [mail](mailto:someone@example.com)
- protocol-relative: [host](//example.com/plan.md)
- root-absolute: [server root](/root-absolute.md)

## Code is never scanned (D2)

A fenced block:

```
- [<path>](<path>) — _role_ — <description>. Updated YYYY-MM-DD.
```

An inline code span: `[the plan](plan.md)` renders as a link elsewhere.
