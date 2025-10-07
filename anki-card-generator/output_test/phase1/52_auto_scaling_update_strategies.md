## Auto Scaling Update Strategies

- many different ways to update an Auto Scaling Group (ASG)
  - should be aware of them all
- Target Groups are a way you could split traffic between separate ASGs
- further separation achieved by Weighted Route 53 CNAME records
  - requires a second Application Load Balancer (ALB)
  - allows separate, manual testing
  - reliant on clients being well-behaved with DNS queries
