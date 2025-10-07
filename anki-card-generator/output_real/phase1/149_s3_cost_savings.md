## S3 Cost Savings

- another summary of S3 Storage Classes and their best use cases
- can move objects manually or through S3 Lifecycle configurations
- other savings options
  - S3 Lifecycle Rules
  - compress objects to save space
  - S3 Requester Pays (typically, the owner of the bucket pays for everything)
    - owner STILL PAYS for storage, but not the request or the data transfer
    - e.g., share dataset across a lot of accounts
    - do not create an IAM role to assume, or you will end up paying still!!!
