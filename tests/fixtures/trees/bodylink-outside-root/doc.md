# Body links that leave the docs root

Lifecycle: active
Role: notes
Project: bodylink-outside-root
Updated: 2026-05-20

## Two escapes, deliberately different

The first names a directory that cannot exist, so "never stat outside the
root" holds by construction. The second is self-referential and therefore
guaranteed to exist on disk, which is what pins E7's "whether or not it would
have resolved".

- cannot exist: [a ghost](../__docs_cli_m27_no_such_dir__/ghost.md)
- provably exists: [this document](../bodylink-outside-root/doc.md)
