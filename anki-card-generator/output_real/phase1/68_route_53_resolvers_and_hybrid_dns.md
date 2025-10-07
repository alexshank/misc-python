## Route 53 - Resolvers and Hybrid DNS

- Route 53 Resolver is what typically answers DNS queries
  - what is a local domain name for an EC2 instance???
  - is an VPC EC2 domain name visible to a public Hosted Zone???
  - are EC2 domain names separate from things you put in a private or public Hosted Zone??? somewhat built-in feature of Route 53???
- Hybrid DNS = resolving DNS queries between VPC and your network (other DNS resolvers)
- Inbound Endpoint (your network resolves AWS resources)
- Outbound Endpoint (Route 53 Resolver resolvers your network resources)
  - Resolver Rules are used to implement this (most specific match)
    - Conditional Forwarding Rules (Forwarding Rules)
    - System Rules
    - Auto-defined System Rules
  - Resolver Rules can be shared across accounts using AWS RAM
    - managed centrally in one account
    - multiple VPCs send DNS queries to the target IP defined in the rule
- endpoints are associated with one or more VPCs in the same AWS region
- create in two AZs for high availability
- need to link on-premise network via AWS VPN or Direct Connect
