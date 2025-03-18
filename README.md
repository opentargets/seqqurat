# Seqqurat

Tool for extracting seq-was from GWAS Catalog


## Run seqqurat

To extract the seqwas study accessions from GWAS Catalog do following procedure

1. Build the study database

```{bash}
DB_PATH=gwas.db
# Download the original study index from GWAS Catalog website
wget https://www.ebi.ac.uk/gwas/api/search/downloads/studies/v1.0.3.1
uv sync --frozen
# Build the database
uv run seqqurat study-index v1.0.3.1 $DB_PATH
```

Now you can query the `study_index` table using `duckdb cli` 

2. Extract the seq-was studies to the parquet file
```{bash}
uv run seqqurat extract-seqwas $DB_PATH --output-path seqwas.parquet
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
