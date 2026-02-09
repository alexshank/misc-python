## Study Group Questions

- you can suspend and resume Amazon EC2 Auto Scaling processes (e.g., Terminate)
- "awsvpc" networking mode gives ECS Tasks same networking properties as EC2 instances
- use API Gateway if there is mention of API keys
- EC2 instance termination protection does not stop auto-scaling events / termination
- Elastic IP Addresses must be public??? Not in private subnets???
- enableDnsHostnames vs enableDnsSupport
  - enableDnsHostnames allows instances with assigned public IPs to have corresponding DNS hostnames in the <region>.compute.amazonaws.com domain.
  - enableDnsSupport enables DNS resolution within the VPC, meaning your instances can resolve the DNS names of other instances.
- how does ECS Anywhere work (more implementation details)???
- AWS AppSync is not for session data, it's a GraphQL service
  - ElastiCache (Redis) would be more appropriate for session data

# Section 06 - Storage
