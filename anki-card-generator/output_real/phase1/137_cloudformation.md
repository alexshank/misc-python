## CloudFormation

- Infrastructure as Code (IaC)
- backbone of Service Catalog service (and many others)
- DeletionPolicy to retain data
  - Retain, Snapshot, or Delete (Default, except for AWS::RDS::DBCluster)
- custom resources via Lambda
  - AWS resource not yet supported
  - on premise resource
  - emptying S3 bucket before being deleted
  - fetch an AMI id
  - anything you want!
- StackSets - updates stacks across multiple accounts and regions
  - Administator and Trusted accounts
  - Automatic Deployment for AWS Organization or OUs
- CloudFormation Drift for detecting manual configuration changes
- Secrets Manager integrations and automatic password rotation for RDS
- resource importing is possible via templates, deletion policies, and unique identifiers for each target
  - CANNOT IMPORT RESOURCE INTO MULTIPLE STACKS
