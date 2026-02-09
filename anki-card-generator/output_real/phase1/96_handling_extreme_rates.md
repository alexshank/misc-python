## Handling Extreme Rates

- architecture discussion
- ALB throughput limits only 10,000 RPS???
- SQS and SNS have unlimited throughput, essentially
- SQS FIFO has 3,000 RPS (with batching)
  - 300 RPS without batching???
- Kinesis is 1 MB/s in, 2 MB/s out PER SHARD
- S3 prefix throughputs limited by KMS if data is encrypted
- caching is a key cost reduction strategy!!!
- this is one of the best architecture slides in the course!!!
