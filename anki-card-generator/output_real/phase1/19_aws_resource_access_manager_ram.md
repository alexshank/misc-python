## AWS Resource Access Manager (RAM)

- avoids resource duplication (e.g., VPC subnets PRIMARILY)
  - there are a lot of VPC-specific considerations
  - e.g., cannot share security groups and default VPC
- should just briefly review the capabilities for the main services
- avoids "VPC peering"
- cannot view / modify / delete other resources, just talk to them ("view" as in through the management console???)
- "Security Groups from other accounts can be reference for maximum security"
  - need to get a concrete example of this???
- Route 53 Outbound Resolver and forwarding rules to your DNS
  - need to get a concrete example of this???
