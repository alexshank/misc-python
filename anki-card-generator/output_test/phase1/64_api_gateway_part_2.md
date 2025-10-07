## API Gateway - Part 2

- Usage Plans and API Keys
- WebSocket functionality
  - DynamoDB example
  - @connections for replies to clients
  - uses HTTP POST with IAM Sig V4
- private API Gateway APIs
  - only accessible from VPC with a VPC Interface Endpoint
  - VPC Interface Endpoint can be used for multiple private APIs
  - can use aws:SourceVpc and aws:SourceVpce in API Gateway resource policies
    - this includes across AWS accounts
