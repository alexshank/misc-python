## AWS DataSync

- synchronize data (large data to and from places)
  - includes on-premise and other cloud providers
    - need appropriate protocol, e.g., NFS
    - these would need an appropriate client
- replication tasks are NOT continuous, are scheduled
- file permissions and file metadata are PRESERVED
- can setup bandwidth limits
- works for all S3 Storage Classes
- can work in the reverse direction
- AWS Snowcone if you have limited bandwidth
