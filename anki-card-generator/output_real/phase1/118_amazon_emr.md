## Amazon EMR

- Elastic MapReduce
- helps create Hadoop clusters to analyze and process big data
- used to migrate away from on-premise Hadoop clusters
- can use hundreds of EC2 instances
- EC2 + EBS with HDFS (temporary storage)
- EMRFS has native integration with S3 (permanent storage)
  - is EMRFS set at EC2 level or EBS level???
- everything launched in single AZ for performance (but you'll lose data)
- Apache Hive for reading from DynamoDB table???
  - Apache Hive is a data warehouse built on top of Hadoop for SQL-like analyzing
- node types and purchasing options
  - master and core nodes good candidates for reserved instances
- instance configurations, know the various options
  - Uniform Instance Groups
  - Instance Fleet (like Spot Fleets)
    - still no autoscaling???
