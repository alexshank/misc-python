## EC2 Image Builder

- automate the creation of Virtual Machiens or container images
- free and only pay for underlying resources
- publish AMI to multiple regions and multiple accounts
- steps
	- spawn Builder EC2 Instance
	- create AMI from the instance
	- spawn new test instance with the new AMI
	- run tests to validate the AMI's functionality / security
- can integrate with CICD pipeline via AWS CodePipeline
