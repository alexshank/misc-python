## VPC Peering

- connect two VPC privately using AWS' network
  - make them behave as if they're a single network
  - must not have overlapping CIDRs (IPv4)!!!
- NOT transitive
- you must update route tables for VPCs to properly work together
- across regions and AWS accounts
- longest prefix match for resolving routes
- where do route tables live??? in each VPC??? between them???
- no edge to edge routing possible
  - this includes NAT Gateway + IGW setup
  - why are both NAT Gateway and IGW needed together usually???
  - a solution will be explained in a later lecture
