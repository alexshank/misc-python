## AWS Batch

- run batch jobs as Docker images
- AWS Fargate OR EC2 + Spot Instances
- direct Amazon EventBridge integrations between S3 and AWS Batch
- managed compute environment - need NAT gateway / instance or VPC Endpoint for ECS
- unmanaged compute environment - deal with all instance configuriation, provisioning, scaling
- Multi Node Mode - good for HPC
  - should launch EC2 instances with placement group "cluster"
    - same server rack in same AZ
  - does NOT work with EC2 Spot Instances
