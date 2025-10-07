## Amazon EventBridge (formerly CloudWatch Events)

- many sources
- can use cron scheduling
- CloudTrail could intercept ANY API call
- produces JSON and sends that to destinations
- many destinations
- Default Event Bus vs Partner Event Buses
  - mostly SaaS companies
  - you can listen to these buses
- can create your own Custom Event Buses
- Resource-based Policies for cross-account access
- can archive and replay events
- Schema Registry can infer your bus's data's schema and do code generation
- Resource-based Policy specifically for each Event Bus
  - could use to aggregate all events from your AWS Organization in a single AWS account
