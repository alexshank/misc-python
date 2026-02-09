## Amazon Inspector

- automated security assessements
- AWS System Manager (SSM) agent on EC2
- Inspector ONLY works for:
  - EC2
  - Amazon ECR container images
  - Lambda Functions
- Uses a database of CVE for package vulnerabilities
- Network reachability for EC2
- Results sent to AWS Security Hub
- Send findings to EventBridge as well
- there is a risk score associated with all findings
