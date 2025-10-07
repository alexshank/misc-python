## CloudFront - Part 1

- a Content Deliver Network (CDN)
- 225+ Point of Presence
- 13 Regional Edge Caches
- Origins include S3 and uses Origin Access Control (OAC)
- VPC Origin for to deliver traffic to private networks
- Custom Origin (HTTP)
  - API Gateway for greatest control
  - or just API Gateway Edge
  - S3 Bucket configure as a website
  - Why not HTTP-S though???
- S3 Cross Region Replication better for servicing only a few specific regions
- use customer header with secret between CloudFront and Custom Origin
- SGs for only whitelisting the CloudFront Edge IPs
