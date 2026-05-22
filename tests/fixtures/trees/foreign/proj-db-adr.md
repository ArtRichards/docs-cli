# Use a Single Relational Database

We considered three options for the persistence layer: a single relational
database, a relational database paired with a document store, and a pure
document store.

## Decision

We will use a single relational database for all persistence.

## Rationale

The data is highly relational and the query patterns are well understood. A
second store would add operational surface — backups, migrations, monitoring
— for no benefit the relational engine cannot already provide. If a genuine
document-shaped workload appears later, this decision can be revisited.
