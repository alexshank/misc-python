## Storage Gateway - Advanced Concepts

- File Gateway: Extensions
  - could use File Gateway for an EC2 instance in a VPC to facilitate cloud migration
  - combine with S3 Events to get benefits of the cloud and serverless architectures
- File Gateway: Read Only Replicas
  - different on-premise data centers can quickly read data with low latency
- File Gateway: Backup and Lifecycle Policies
  - get benefits of moving S3 objects to infrequent access tiers to get file system cost savings
- File Architecture: Other possibilities
  - S3 object versioning to restore a file or entire file systems to specific version
    - use the "RefreshCache" API on the Gateway to be notified of restore
  - S3 Object Lock for Write Once Read Many (WORM) data
    - clients' new versions do not affect previous versions
