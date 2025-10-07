## Elastic Load Balancers - Part 2

- cross-zone load balancing
  - cross-zone load balancing (availability zone)
    - evenly across all EC2 instances
  - without cross-zone load balancing
    - distributed between instances of each AZ
  - CLB (disabled by default, no charges if enabled)
  - ALB (always on, no charges)
  - NLB (disabled by default, charges if enabled)
  - GLB (disabled by default, charges if enabled)
- sticky sessions (session affinity)
  - same instance always serves client by using cookies
  - request routing algorithms
    - least outstanding requests (CLB and ALB)
    - round robin (CLB and ALB)
    - flow hash (NLB)
