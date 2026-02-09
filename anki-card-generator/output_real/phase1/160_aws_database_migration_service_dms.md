## AWS Database Migration Service (DMS)

- resilient and self-healing database migration
- source database remains available during the migration
- hetergenous migrations
- Continuous Data Replication using CDC???
- an EC2 instance is required to perform the tasks
- many sources and targets
  - note that Redshift, Kinesis Data Streams, and OpenSearch are targets but NOT sources
- AWS Schema Conversion Tool (SCT)
  - for converting schemas between different database engines
  - works alongside DMS on the EC2 instance
  - not needed if source and target engine are the same
  - for OLTP and OLAP
- various useful and specific points on the "Good things to know" slide
- can combine Snowball and DMS for very large volumes of data
  - speed of Snowball and CDC of DMS
