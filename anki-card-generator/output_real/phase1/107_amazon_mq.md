## Amazon MQ

- SQS / SNS are cloud-native services
- traditional on premise applications use open protocols like MQTT, AMQP, Openwire, etc.
- Amazon MQ is a managed message broker service for Rabbit MQ and ActiveMQ
    - doesn't scale as much as SQS / SNS
    - runs on servers, which you can run in Multi-AZ with failover
    - has both queue (SQS) and topic (SNS) features on each server
- can migrate these current services to Amazon MQ
    - IBM MQ
    - TIBCO EMS
    - Rabbit MQ
    - ActiveMQ
