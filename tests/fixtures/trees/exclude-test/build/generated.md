no metadata at the head
# Generated H1

This file is deliberately malformed (no Lifecycle / Role / Project /
Updated metadata block) so the exclude-test fixture proves that
`[exclude] dirs = ["build"]` in the sidecar .docs.toml is the only
reason `docs check` exits 0 — without the exclusion, this file would
surface as malformed.
