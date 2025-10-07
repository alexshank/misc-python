## AWS Client VPN

- connect from your computer to private network in AWS or on-premise
- uses OpenVPN
- uses private IP (of, e.g., an EC2 instance)
- single Client VPN ENI can be used with VPC peering or S2S VPN
  - note that this might mean your traffic goes through AWS to get to your on-premise network
- integrates with Internet Gateway or NAT Gateway so clients can access internet
  - don't client's use public internet for the initial Client VPN connection???
- also integrates with Transit Gateway
