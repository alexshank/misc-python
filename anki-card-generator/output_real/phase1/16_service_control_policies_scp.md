## Service Control Policies (SCP)

- "Management account can do anything, no matter what!"
- Explicit allows (FullAWSAccess) needed at every OU and account (even root)
  - Management Account would still have full access, but nested OUs would not
- Cannot restrict access for Service-linked roles
- IAM Policy Evaluation Logic (shouldn't memorize, but should make sense)
- Restricting specific Tags on AWS resources
  - exam question: ForAllValues or ForAnyValue
- Can deny entire regions via SCP
- Are tag-based IAM conditions only available in SCPs???
- AI training and backup policies
