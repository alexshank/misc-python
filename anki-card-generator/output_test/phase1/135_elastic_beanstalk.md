## Elastic Beanstalk

- good for re-platforming on premise to cloud
- developer-oriented view of deploying an application
- supports the main platforms (e.g., Java with Tomcat)
- single or multi-container docker configuration
- managed service
- three architecture models
  - single instance (development)
  - high-availability with load balancer
  - worker tier
- web server vs worker environment
  - decoupling application into two tiers
  - cron.yaml for periodic tasks
- blue / green deployments (zero downtime)
  - Route53 + entirely new "stage" environment for v2
