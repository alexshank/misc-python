## IAM

- not going to go through IAM basics again
- policy deep dive / anatomy
  - example policies for various services and scenarios: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html
  - should understand these to get an idea of IAM's power
  - NotAction for allowing a few distinct actions in a service
- least privilege for maximum security

### 08-15-2025 - Reviewing "IAM" Section Notes

- Confused Deputy Problem is when lesser-privleged role coerces another role to perform an action
	- cross-account or cross-service third parties are the culprits usually
	- for example, solved by the "external ID" in an IAM Role Trust Policy
	- recommended to use aws:SourceArn, aws:SourceAccount, aws:SourceOrgID, or aws:SourceOrgPaths in policies for cross-service policies
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html
- Service-Linked Roles include CloudWatch Logs for writing to Kinesis Data Firehose
	- service roles and service-linked roles are NOT equivalent
	- permission boundaries cannot be applied to service-linked roles
- role chaining (when a role assumes another role)
	- limits role session to an hour
	- can pass session tags and transitive session tags when assuming roles 
	- permissions policies and trust policies(delegation)
		- first role has an allow stsAssumeRole in its permissions policy
		- second role has the first role's ARN in its trust policy
		- the first role would have a trust policy for its AWS account root
- a trust policy is itself a Resource-Based Policy
- permission boundaries get put directly on either an IAM Role or an IAM User
	- they do NOT work with User Groups
	- Resource-Based Policies are NOT IMPACTED by permission boundaries
- if using an external identity provider, you are given an IAM role and temperary credentials
- Session Policies can also limit permissions after assuming a Role or becoming a User
- IAM Role Session ARNs are TREATED SEPARATELY from the IAM Role in Resource-Based Policies
	- permission boundaries, identity-based policies, and session policies implicit denies are ignored
- IAM Identity Center, Incognito, and IAM are NOT THE SAME for federation
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers.html
- an example of how to allow your company's IdP to work with AWS Console logins
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_enable-console-custom-url.html
- TODO need to watch a demo of these three different federation setups!!!
