## VPC Endpoints

- allow you to connect to AWS Services using a private endpoint instead of www network
- VPC Endpoint Gateway (for S3 and DynamoDB)
  - VPC Endpoint Interface for all other AWS services
  - check DNS Setting Resolution in VPC or route tables!!!
  - cannot be extended out of the VPC to VPN, DX, TGW, or peeering!!!
- VPC Endpoint Interface (an Elastic Network Interface)
  - get a private endpoint interface hostname
  - public hostname of the AWS service then resolves to private endpoint interface hostname
  - CAN be accessed from DX and Site-to-Site VPN!!!
  - difference between VPC peering and Site-to-Site VPN???
