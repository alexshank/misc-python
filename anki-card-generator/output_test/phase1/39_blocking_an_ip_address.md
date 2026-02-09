## Blocking an IP Address

- NACL would be first line of defence within your public subnet
- ALB adds another line of defense (EC2 can be in private subnet with private IP)
  - can use Connection Termination at ALB, so ALB uses its own Security Group setup and makes separate connection to the EC2 instance.
  - this is the same for ALB or NLB.
- WAF then pairs with the ALB to filter IP addresses, and do much more defensive things
- NACL filtering is not helpful if clients are going through CloudFront first
  - in that case, put WAF on the CloudFront
  - could additionally use CloudFront Geo Restriction
