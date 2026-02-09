## Amazon EKS - Elastic Kubernetes Service

- cloud agnostic
- supports EC2 or Fargate for containers
- any mention of "pods" = Amazon EKS
- should review how these would be exposed to public subnets???
- Managed vs Self-Managed vs No (Fargate) Nodes
- StorageClass manfiest on your EKS cluster
  - leverages Container Storate Interface (CSI)
  - multiple options, reference slides
- Amazon EFS is only option that works with Fargate!
