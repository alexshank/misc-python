## Transit Gateway

- a way to understand your network topology as it gets complicated
- controls transitive peering between thousands of...
  - VPC
  - on-premise
- regional resource, but can work cross-region
  - via Transit Gateway peering
- share them across accounts with Resource Access Manager (RAM)
  - major use case for RAM!!!
- supports IP Multicast between your AWS services (only service that offers this)
  - access NAT Gateway, NLB, PrivateLink, and EFS of other VPCs
- need to understand the architecture diagram discussed???
- route tables can restrict transitive peering
  - comprehensive peering is the default??? seems off???
- integration with Direct Connect Gateway
- inter and intra region peering to create meshes
  - billed hourly for each peering attachment
  - only billed for data processing between regions
