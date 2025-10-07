## S3 Security

- Glacier has all data encrypted under AWS control
- SSL / TLS via https (recommended)
  - enforced with aws:SecureTransport
- S3 Access Logs are best effort, may go to a different bucket, might take hours to deliver
- pre-signed URLs for download and uploads (give your credentials via a URL)
  - allow logged-in users to download a video
  - allow a user to upload to a very specific location
- "elastic IPs are public IPs, by the way"
- public bucket: AWS:SourceIP
- private bucket: AWS:SourceVpce or AWS:SourceVpc
- WORM for data retention
