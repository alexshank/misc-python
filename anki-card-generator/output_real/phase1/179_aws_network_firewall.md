## AWS Network Firewall

- ways to control your networks
  - NACLs
  - Amazon VPC security groups
  - AWS WAF
  - AWS Shield and AWS Shield Advanced
  - AWS Firewall Manager
- to protect the your entire VPC, use AWS Network Firewall
  - from Layer 3 to Layer 7
  - need to review network layers???
  - can inspect any traffic / connections to the VPC
- under the hood, uses AWS Gateway Load Balancer
- can manage rules cross-account with AWS Firewall Manager
- allow, drop, or alert on traffic rules
- Active flow inspection for intrusion-prevention
- send logs of rule matches to various destinations (e.g., S3)
- "north-south" traffic enters / leaves your network
- "east-west" traffic stays within your network
