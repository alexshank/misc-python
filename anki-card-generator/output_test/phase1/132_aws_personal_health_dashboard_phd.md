## AWS Personal Health Dashboard (PHD)

- global service
- shows how AWS outages directly impact you
- key word is "maintenance" - shows all maintenance events from AWS
- accessible through the AWS Health API
- aggregate across multiple accounts with AWS Organizations
- can react to AWS Health events for your AWS account via EventBridge
  - CANNOT be used to intercept public events from AWS Service Health Dashboard
    - use the RSS feed???
- good (and rare) demo given
