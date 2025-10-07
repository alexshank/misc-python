## IAM Access Analyzer

- access advisor - uses data analysis to help you set permission guardrails confidently
  - provides service-last-accessed information for accounts in your organization.
  - determine the services not used by IAM users and roles.
  - can later implement permissions guardrails using SCPs that restrict access to those services
- access analyzer - lets you know if you've shared resources to outside accounts (Zone of Trust)
  - also lints your IAM policies' grammar, suggestions, etc.
  - generate policies based on real activity (via CloudTrail logs)
- assuming a role drops all of your existing permissions
