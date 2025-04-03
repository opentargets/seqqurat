BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS '{table_name}' AS 
    SELECT * FROM '{output_dataset_path}';
COMMIT;