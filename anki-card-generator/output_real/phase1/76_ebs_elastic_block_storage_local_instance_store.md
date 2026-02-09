## EBS (Elastic Block Storage) & Local Instance Store

- network drive in specific AZ
- multiple could attach to a single EC2 instance
- six different types of EBS Volumes
  - see slides
- EBS backups (snapshots) are incremental
- EBS backups use IO
- recommended to detech EBS Volume before snapshots
- can create AMIs from snapshots
- Fast Snapshot Restore (FSR)???
- Amazon Data Lifecycle Manager vs AWS Backup???
- must enable auto encryption for new EBS Volumes
  - at account-level AND per region
- Local Instance Store or just Instance Store???
- EC2 Instance Store (physical, higher IOPS)
  - potential data loss
  - can't resize
  - backups operated by user
