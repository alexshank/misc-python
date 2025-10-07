## Route 53 - Part 2

- private vs public Hosted Zones
- must enable VPC settings for internal private DNS / Private Hosted Zone
  - enableDnsHostnames
  - enableDnsSupport
- how does DNS Security Extensions (DNSSEC) work exactly???
  - only for Public Hosted Zones
- third-party registrar by updating registrar's NS record
- health checks are only for public resources (not the same as Public Hosted Zone???)
  - they can publish CloudWatch Metrics
- health check types
  - an endpoint
  - other health checks (Calculated Health Checks)
  - CloudWatch Alarms (full control)
- about 15 global health checkers will check endpoint health
- first 5120 bytes of the response can be used to pass or fail the check
- for private endpoints, health checkers don't have access to the VPC or on-premise resource
  - solution is CloudWatch Metric, CloudWatch Alarm, health check looks at Alarm
