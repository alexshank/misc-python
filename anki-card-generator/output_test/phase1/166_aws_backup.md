## AWS Backup

- fully managed service for centrally managing backups across AWS services
- supports cross-region backups
- supports point in time recovery (PITR) for supported services (e.g., Aurora)
- tag-based backup policies
- Backup Plans for managing backup policies
- use a Backup Plan for many different AWS resource types
- AWS Backup Vault Lock
  - enforce WORM
  - cannot delete backups, even as root user, when enabled
