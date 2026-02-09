## AWS STS (Security Token Service)

- Security Token Service (STS) assume role within...
  - your account
  - another account
  - identity federation (3rd party authenticated users)
  - AWS services (Lambda, for example)
- Again, STS will drop all your current permissions
- Least privelege + auditing using CloudTrail (require MFA, CLI, etc.)
- External ID (secret between you and 3rd party, chosen by 3rd party)
- Confused Deputy (exam question)
- GetFederationToken API call probably NOT on the exam
