# Seqqurat

Tool that allows building [OpenTargets Platform outputs](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/25.03/output/) OLAP database via duckdb python interface.

## Requirements

- uv
- duckdb command line interface

## Run seqqurat

### Loading OpenTargets datasets

To build the local sql database with duckdb and open targets outputs data follow the examples below:

```{bash}
# Download all data output from the ftp server.
rsync -rpltvz --delete rsync.ebi.ac.uk::pub/databases/opentargets/platform/25.03/output .
# Load the datasets
uv sync
uv run seqqurat build-ot-db --output-datasets-path output ot.db
```

The above command will load all output datasets to the duckdb local database under
the `ot.db` file. The loading of full 25.03 downloads should take ~6minutes on 16G memory machine with 8 cores (tested on Mac M1). The size of the database is ~26GB for 25.03 release.

To view the database locally you must install the duckdb cli client. If it is installed view the database with

```{bash}
# install duckdb cli
curl https://install.duckdb.org | sh
```

```{bash}
# Open the Open Targets outputs database
duckdb -ui ot.db
```

Now you can explore the Open Targets output data in your browser SQL client!

### Exome sequencing analysis

To extract the seqwas study accessions from GWAS Catalog do following procedure

1. Build the study database

```{bash}
# Download the original study index from GWAS Catalog website
wget https://www.ebi.ac.uk/gwas/api/search/downloads/studies/v1.0.3.1
uv sync --frozen
# Build the database
uv run seqqurat study-index v1.0.3.1 --db-path gwas.db
```

Now you can query the `study_index` table using `duckdb cli`

2. Extract the seq-was studies to the parquet file

```{bash}
uv run seqqurat extract-seqwas gwas.db --output-path seqwas.parquet
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
This repository is a proof of concept how the duckdb can be utilized to enable fast load of SQL OLAP queries to create a full usable database from scratch.
