## CloudTrail - SA Pro

- Solutions Architecture: Delivery to S3
- Solutions Archtecture: Multi Account, Multi Region Logging
  - Use S3 bucket resource policy for cross-account access.
  - "Security account for audit"
-
- Solutions Archtecture: Alert for API Calls
  - Can trigger on aggregates of API calls
  - e.g., a lot of denied calls, a lot of resource deletions, etc.
- Solutions Archtecture: Organizational Trail
  - Must be created in the Management account!!
  - S3 bucket with account numbers as object key suffix
- 15 mins delivery of CloudTrail events
  - EventBridge is the fastest reactive way
