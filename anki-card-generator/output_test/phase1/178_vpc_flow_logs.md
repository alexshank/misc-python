## VPC Flow Logs

- capture IP traffic going into your interfaces
  - VPC Flow Logs
  - Subnet Flow Logs
  - Elastic Network Interface (ENI) Flow Logs
- can send to various data sources (e.g., Kinesis Data Firehose)
- capture network information from AWS managed interfaces too
  - ELB
  - RDS
  - WorkSpaces
  - Transit Gateway
  - etc.
- has specific format
- query the logs using Athena on S3 or (for streaming analysis) CloudWatch Logs Insights
  - are all CloudWatch Logs Insights for streaming data???
- CloudWatch Contributor Insights for highest traffic
- inbound public IP traffic can make it to NAT Gateways, but is then dropped!!!
