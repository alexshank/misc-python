## S3 Multi-Region Access Points (Global)

- Dynamically routes request to lowest latency buckets
  - Different S3 buckets, but with regional replication enabled (Bi-directional Cross-Region Replication)
  - must have bucket versioning enabled
- Failover control active/passive or active/active
  - active, in this case, means you can write to multiple regions/buckets and have it synced
- S3 is NOT A GLOBAL SERVICE BY AWS DEFINITION
