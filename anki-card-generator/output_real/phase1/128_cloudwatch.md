## CloudWatch

- CloudWatch Metrics
  - EC2 Detailed Monitoring bumps CW Metrics from 5 mins to 1 min
  - EC2 RAM is NOT a built-in metric
- CloudWatch Alarms
  - can be intercepted by EventBridge (powerful)
  - can trigger actions like EC2 terminate, auto-scaling, or SNS
- CloudWatch Dashboards
  - can display both metrics and alarms
  - can display metrics of multiple regions
- CloudWatch Synthetics Canary
  - scripts that monitor your services by acting like users
  - screenshots of UIs, API calls, real workflows
  - checks more than just if a service is responsive
  - can trigger CloudWatch Alarms
  - written in NodeJS or Python
  - headless browser
  - "Blueprints"???
  - probably based on Selenium or Puppeteer???
