## AWS Transfer Family

- managed service for FTP/FTPS/SFTP file transfers in/out of S3 and EFS
- data transfer cost per GB
- provisioned endpoints cost per hour
- stores / manages user credentials within the service
  - all the typical integrations like Okta or LDAP
- could optionally use Route53 DNS records
- Endpoint Types
  - Public Endpoint (changing IP, can't whitelist, use domain name)
  - VPC Endpoint with Internal Access (static private IPs, VPN/DX, SGs/NACLs)
  - VPC Endpoint with Internet-Facing Access (attach an EIP, can setup SGs as firewall)
