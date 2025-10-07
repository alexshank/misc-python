## Amazon ElastiCache

- ElastiCache is to get managed Redis or Memcached
  - analogous to RDS for relational databases
- requires heavy application code changes
- user session store is very common use case for ElastiCache
  - creates "stateless" application???
- Redis (should review how it works in general???)
  - Read Only File Feature (Append Only File - AOF)
    - restore from backup, data durability
  - read replicas across AZs, auto-failover
- Memcached (should review how it works in general???)
  - non-persistent
  - multi-node for sharding
  - multi-threaded architecture
  - backup and restore if you're using the serverless (not self-managed) version
