BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS '{table_name}' AS 
    SELECT * FROM read_parquet('{output_dataset_path}', hive_partitioning = true);
COMMIT;