## Comparison of Solutions Architecture

- good target CPU utilization for ASG is between 40-70%
- ALB and Lambda is something like 10-20x cheaper than API Gateway and Lambda
  - can use AWS WAF with the ALB and Lambda solution
- soft limits of 10,000 requests per second and 1000 concurrent Lambda for API Gateway
