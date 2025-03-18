# Seqqurat

Tool for extracting seq-was from GWAS Catalog


## Run seqqurat

1. Build the study database

```{bash}
DB_PATH=gwas.db
# Download the original study index from GWAS Catalog website
wget https://www.ebi.ac.uk/gwas/api/search/downloads/studies/v1.0.3.1
uv sync --frozen
# Build the database
uv run seqqurat study-index tests/data/gwas-catalog-v1.0.3.1-studies-r2025-03-08.tsv $DB_PATH
```

2. Extract the seq-was studies
```{bash}
uv run seqqurat extract-seq-was $DB_PATH
```

> [!TIP]
> Currently we support only `v1.0.3.1` version schema of the GWAS Catalog study index.


## Development

> [!NOTE]
> Run `make dev` before starting development.


### Adding new scripts

To add new sql scripts one should add them in the `seqqurat/sql` directory.


## Disclaimer

All of above is easily achievable from the `duckdb` command line without python overhead.
This repository is a proof of concept how the duckdb can be utilized to run arbitrary SQL queries within the python package.