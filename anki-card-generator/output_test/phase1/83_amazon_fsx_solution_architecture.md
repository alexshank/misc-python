## Amazon FSx - Solution Architecture

- AWS DataSync to migrate Single AZ FSx to Multi-AZ FSx
- can also do backup and restore (has some downtime)
- decrease FSx Volume size with AWS DataSync and separate, smaller FSx instance
- FSx for Lustre can lazy load S3 files
