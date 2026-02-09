## Lambda@Edge and CloudFront Functions

- CloudFront Functions are deployed to Edge Location
  - between users and CloudFront
  - millions of request per second
  - transformations before hitting cache
- Lambda@Edge Functions are deployed to Regional Edge Cache
  - VM-based isolation???
  - older
  - thousands of request per second
  - can change all combinations of Viewer/Origin Request/Response
  - transformations before and after hitting cache
- CloudFront Functions have VERY small execution time, memory, and package size
  - just for headers, no access to request body
- how would CloudFront Functions do JWT auth without network calls???
- does CloudFront Functions have access to method, path, etc???
