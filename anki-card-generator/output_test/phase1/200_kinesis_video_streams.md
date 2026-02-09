## Kinesis Video Streams

- one video stream per producer (streaming device)
	- security cameras
	- smartphone
	- Kinesis Video Streams Producer library
- data stored in S3, but is inaccessible
- CANNOT output the stream data to your own S3 locations
	- use custom solution
- can consume with EC2
- can leverage Kinesis Video Stream Parser library
- integrates with AWS Rekognition for facial detection
- useful architecture diagram slide
