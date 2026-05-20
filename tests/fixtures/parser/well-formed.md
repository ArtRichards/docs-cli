# Well-formed test doc

Status: active
Role: spec
Project: parser-tests
Updated: 2026-05-20

Related:
- pairs-with: well-formed-companion.md

## Purpose

This is a well-formed doc used by the parser tests. The metadata block follows the convention exactly: H1, blank line, contiguous `Label: value` lines, blank line, content sections.

## Notes

A second section to confirm the parser stops at the first blank line after the metadata block (not at the next H2 or end of file).
