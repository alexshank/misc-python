## VPC Endpoint Policies

- JSON policies to control access to services
  - works in combination with IAM user policies or service-specific policies
  - can force their application by restricting traffic that does NOT come from the VPC
    - e.g., "aws:sourceVpce" condition (single VPC Endpoint)
    - e.g., "aws:sourceVpc" condition (NOT the VPC, but all VPC Endpoints within the VPC)!!!
- S3 bucket policies can only affect PUBLIC IP addresses
  - so, aws:SourceIp condition doesn't work on VPC Endpoints
- note all of the potential things blocking a private EC2 instance from accessing S3
