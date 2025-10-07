## Amazon EFS (Elastic File System)

- mounting???
- can be mounted on many EC2 instances
- bill by GB used, not provisioned (unlike EBS)
- doesn't work for Windows AMIs
- Security Groups for configuring access
- limit to one VPC, then one ENI (mount target) per AZ
- Performance Mode vs Throughput Mode???
- Storage Classes or Storage Tiers???
- EFS One Zone-IA???
- on-premise server must use the IPv4 of the ENI (not DNS)
  - EC2 instance can use VPC peering and DNS
- AWS Site-to-Site VPN???
- combine IAM permissions with EFS Access Points
  - POSIX users and groups
- can use resource-based policies too, like with S3
- Cross-Region Replication
  - provides RPO and RTO
  - does NOT affect provisioned throughput
