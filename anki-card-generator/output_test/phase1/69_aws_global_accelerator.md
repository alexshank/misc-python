## AWS Global Accelerator

- use AWS internal network to route traffic to your applications faster
- 2 "Anycast IPs" created for your application
- these IPs send traffic directly to Edge Locations
- targets are EIP endpoints, EC2 instances, ALB, NLB, public or private
  - public or private what though???
- client IP address is NOT preserved for EIP endpoints
- has health checks, failovers, disaster recovery
- security
  - only need to whitelist 2 IPs
  - DDoS protection with AWS Shield
- superior to CloudFront when dong non-HTTP things
  - proxies packets at edge to applications running in one or more AWS regions
  - ex: UDP, TCP, MQTT, VOIP
- also superior for HTTP things that require static IP addresses
- OR deterministic, fast regional failover (intelligent routing, no client cache issue because static IP)
