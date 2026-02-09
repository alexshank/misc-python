## Amazon Athena

- serverless query service for S3 data
  - built on Presto and standard SQL language
- Presto = distributed SQL query engine designed for fast, interactive querying of large datasets from various sources
- can be good for VPC Flow Logs, ELB Logs, CloudTrail trails, etc.
- columnar data helps cost by reducing scans
  - parquet or ORC data formats
  - possibly use AWS Glue for transformations
- compress (reduce retrievals) and partition datasets (reduce scans)
- big files (>128 MB) to minimize overhead
- Federated Query can be run using Data Source Connectors
  - HBase in EMR???
  - results written back to S3
