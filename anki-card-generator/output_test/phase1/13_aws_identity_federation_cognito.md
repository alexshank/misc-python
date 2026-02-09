## AWS Identity Federation & Cognito

- Identity Federation (users outside AWS get access to your account)
  - e.g., your company already uses Active Directoy
  - need a "trust relationship" between identity provider and AWS
  - STS AssumeRoleWithSAML
- Customer Identity Broker Application pushes the burden of appropriate IAM Role determination to the Custom Identity Broker
- For some reason, the flow is slightly different (extra step) to go to the Management Console?
- Use special Policy Variables to actually restricted the authenticated users to certain resources
