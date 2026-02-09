## Amazon SES (Simple Email Service)

- managed service to send emails securely, globally and at scale
- inbound and outbound emails
- reputation dashboard, performance insights, anti-spam feedback
- supports DomainKeys Identified Mail (DKIM) and Sender Policy Framework (SPF)
	- are these meaningful???
- shared, dedicated, or customer-owned IPs
- Configuration Sets
	- customize and analyze your email send events
	- event destinations
		- Kinesis Data Firehose (for email metrics)
		- SNS (for immediate bounce and complaint feedback)
	- IP pool management
		- separate email reputations based on IP you send with
