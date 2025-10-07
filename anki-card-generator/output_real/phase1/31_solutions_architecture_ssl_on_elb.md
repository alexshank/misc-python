## Solutions Architecture - SSL on ELB

- Using NLB, user data scripts on your EC2 instances to install SSL certs (via SSM Parameter Store, IAM permissions)
  - Alternative is to offload SSL coompute to CloudHSM (SSL Acceleration)
  - more secure because private key never leaves HSM device
