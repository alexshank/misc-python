## IAM Conditions

- restrict API calls by IP address (aws:SourceIp)
- restrict by region (aws:RequestedRegion)
- restrict by the EC2 instance tags (ec2:ResourceTag)
  - related: aws:PrincipalTag/Department
- require user to have MFA (aws:MultiFactorAuthPresent)
- bucket vs object level S3 permissions
- aws:PrincipalOrgID
  - e.g., bucket resource policy allowing access for an entire AWS Organization
