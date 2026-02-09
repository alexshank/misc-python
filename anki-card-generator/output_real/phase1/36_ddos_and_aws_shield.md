## DDoS and AWS Shield

- overview of types of attacks
- AWS Shield Standard to protect yourself at no cost
- AWS Shield Advanced is premium service for 24/7 DDoS protection
- AWS WAF - filter requests with rules
- CloudFront and Route52 have Shield enabled by default, a lot of work to attack
  - good because stops attack at the edge before your services
- be ready to auto scale (more $$$)
- serve static resources via S3 / CloudFront
