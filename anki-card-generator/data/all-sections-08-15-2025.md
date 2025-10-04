# All Sections

Has the concatenated notes from all study sections. Note this is out of sync with the original docs, due to adding / editing details as I review content.

# Section 03 - Identity and Federation

## IAM

- not going to go through IAM basics again
- policy deep dive / anatomy
  - example policies for various services and scenarios: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html
  - should understand these to get an idea of IAM's power
  - NotAction for allowing a few distinct actions in a service
- least privilege for maximum security

### 08-15-2025 - Reviewing "IAM" Section Notes

- Confused Deputy Problem is when lesser-privleged role coerces another role to perform an action
	- cross-account or cross-service third parties are the culprits usually
	- for example, solved by the "external ID" in an IAM Role Trust Policy
	- recommended to use aws:SourceArn, aws:SourceAccount, aws:SourceOrgID, or aws:SourceOrgPaths in policies for cross-service policies
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html
- Service-Linked Roles include CloudWatch Logs for writing to Kinesis Data Firehose
	- service roles and service-linked roles are NOT equivalent
	- permission boundaries cannot be applied to service-linked roles
- role chaining (when a role assumes another role)
	- limits role session to an hour
	- can pass session tags and transitive session tags when assuming roles 
	- permissions policies and trust policies(delegation)
		- first role has an allow stsAssumeRole in its permissions policy
		- second role has the first role's ARN in its trust policy
		- the first role would have a trust policy for its AWS account root
- a trust policy is itself a Resource-Based Policy
- permission boundaries get put directly on either an IAM Role or an IAM User
	- they do NOT work with User Groups
	- Resource-Based Policies are NOT IMPACTED by permission boundaries
- if using an external identity provider, you are given an IAM role and temperary credentials
- Session Policies can also limit permissions after assuming a Role or becoming a User
- IAM Role Session ARNs are TREATED SEPARATELY from the IAM Role in Resource-Based Policies
	- permission boundaries, identity-based policies, and session policies implicit denies are ignored
- IAM Identity Center, Incognito, and IAM are NOT THE SAME for federation
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers.html
- an example of how to allow your company's IdP to work with AWS Console logins
	- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_enable-console-custom-url.html
- TODO need to watch a demo of these three different federation setups!!!

## 08-17-2025 - Learn Cantrill 

- trying to watch a demo of the three different federation setups
	- beginning to use https://learn.cantrill.io/ as a supplemental training material
	- has useful demos and scenarios
- detouring through Learn Cantrill's conent...
	- course intro content
	- AWS account setup demos
	- OSI Networking Layers overview
- OSI 7-Layer Networking Model
	- a CONCEPTUAL model, not always how networks are implemented
		- e.g., finding clear division between layer 4/5 not valuable
	- note that a "layer X" device has all lower layers as well
	- this means that an L3 router understands layers 1, 2, and 3
	- layer 1, physical, dumb, many collisions, copper/fiber/wifi
		- HUBS are dumb repeater devices on this layer
	- layer 2, data link, introduces frames, physical devices have pre-defined MAC addresses
		- uses carrier signal to know when coast is clear to send frame
		- random, increasing backoff
		- SWITCHES use MAC Address tables to avoid dumb repeating
		- each port is a separate collision domain!!!
	- layer 3, network, getting from one network to another (not LAN)
		- introduces the IP protocol (IPv4 vs IPv6)
		- the LAN networks do NOT have to have same L2 protocol
		- the IP packet is continuously encapsulated by different L2 frames at each network (hop)
		- the IP packet contains a field specifying the L4 protocol
		- IPv4
			- first two octets define the network, second two define the host (in the /16 prefix case)
			- subnet mask determines if packet needs to go to gateway (typically your router)
			- route tables and routes with most specificity are utilized
			- packets then repackaged for L2 transport via MAC Address translation (Address Resolution Protocol)
		- Address Resolution Protocol (ARP)
			- L2 broadcast to ask for MAC address of matching IP address
		- layer 4 will address the issues of...
			- no channels of communication (different conversations between same two IPs)
			- no ordering of packets
			- no delivery guaruntee
			- no flow control
		- Network Address Translation (NAT) used for multiple private IPs to share single public IP
	- layer 4/5, transport/session
		- TCP or UDP are typical layer 4 protocols
		- TCP
			- has segments that are each encapsulatted into an IP packet
			- introduces ports for multiple conversations
			- introduces sequence number and acknowledgement
			- introduces window for managing send/recieve volumes
			- connect via random (ephemeral) client port and known server port
				- NACLs (stateless) in AWS often have to whitelist these "high ports"
				- SGs (stateful) in AWS will allow inverse traffic back out
			- three-way handshake
				- common flags can be set (SYN, SYN-ACK FIN, ACK)
				- basically using two unique sequence numbers and ACKs
		- strictly speaking, managing state in the firewall would be a layer 5 technology
			- HTTP cookies would also be a layer 5 technology
	- layer 6, presentation, how to interpret or translate data to a standard format for other applications
		- HTTP using ASCII encoding is an example
		- often combined with / achieved by application layer
	- layer 7, application, what commands the interpreted data correspond to
		- for HTTP, "G-E-T" means GET and the command fetches data
- there are other networking models like the 5 layer TCP/IP model
- FTP could have a completely different layer 5, 6, 7 implementation
	- it could entirely ignore a L5 implementation
- don't worry too much about making everything fit perfectly into the conceptual frameworks

## 08-22-2025 - Learn Cantrill (Tech Fundamentals, Networking)

- Network Address Translation (NAT)
	- deals with IPv4 shortages
	- governing agencies give out public IPs to ISPs and then individuals
	- Static NAT is 1:1 private IP to public IP
		- AWS IGW is an example
	- Dynamic NAT is for when you have more private IPs than public IPs
	- Port Address Translation (PAT) aka "overloading"
		- map many private IPs to a single public IP
		- AWS NATGW is an example
	- IPv6 means you DO NOT need any form of address translation
	- public and private addresses CANNOT communicate over public internet
	- For PAT, the NAT device keeps track of / generates random public source ports
		- the private source ports of the private IP devices can conflict without issue
		- you CANNOT initiate a connection with a private device behind PAT
- IPv4 Addressing and Subnetting
	- you must be allocated a public IPv4 address
	- Internet Assigned Numbers Authority (IANA)
	- 4.29 billion IP addresses
	- address spaces
		- Class A (first octet, huge businesses in early days)
		- Class B (first two octets, fewer IPs for each network)
		- Class C (first three octets, for small businesses)
		- Class D and E also exist, but are their own topic
	- private IPs are carved out of the Class A, B, C address spaces
	- 172.31 private network is used for default AWS VPC
	- should still always aim to avoid private network IP address overlaps
	- subnetting = splitting an original network into multiple address spaces
	- use a suffix like /16 to specify the starting bits of a subnetwork
		- larger the prefix value, smaller the network
		- one /16 network == two /17 networks
		- /0 is the entire internet
		- /32 is a single IP address
	- typically have an even number of subnets, but could just split one of the halves again to get 3
- SSL and TLS
	- privacy and data integrity between client and server
	- TLS is newer version of SSL
	- combination of asymmetric and symmetric encryption
	- identity verification (typically only verify the server, but could do both)
	- reliable connection (detect alternations)
	- TLS begins with an established TCP connection
	- three main phases for initiation
		- cipher suites (server returns certificate with public key)
		- authentication (client checks server's certificate via a known CA)
			- operating system and browser vendors have list of trusted Certificate Authorities (CA)
			- server makes a Certificate Signing Request (CSR)
			- CA then generates a signed certificate for the server to use
		- key exchange (get from asymm to symm encryption for efficiency)
			- client creates pre-master key
			- pre-master key is shared via public key encrypt and private key decrypt
			- server and client each generate the same master secret
	- the application layer (e.g., HTTPS or FTPS) decides if TLS should be intiated
		- TLS is technically considered layer 6 presentation layer
		- TLS is practically considered layer 4 transport layer
 - Recovery Point Objective (RPO) and Recovery Time Objective (RTO)
	- Recovery Point Objective
		- maximum amount of data (time) that can be lost (stomached) by the organization
		- i.e., time between successful backups
		- may be different between systems (e.g., can't lose bank transactions, but could lose internal tool's data)
	- Recovery Time Objective
		- maximum tolerable length of time a system can be down
		- starts the second the error happens, ends when you hand the system back to the business folks
		- need good monitoring or you don't know the true start time of the outage
	- aim for GOLDILOCKS scenario (as close to the true business requirements as possible)
- VLANs, TRUNKS, and QinQ
	- remember LAN is a shared broadcast domain on network layer 2
	- remember each port of a switch is a separate collision domain
	- we want to separate broadcast domains to relevant parties (e.g., sales, security, IoT, whatever)
	- issue is dealing with physical hardware plugged into switches (what if devices are in separate buildings?)
	- Virtual Local Area Networks (VLANs) solve this issue
	- they add a VLAN ID to 802.1Q ethernet frames
	- creates up to 4096 broadcast domains in the same physical network
		- 802.1AD ethernet frames allow ISPs to use stacked VLANS
		- also called nested QinQ VLANs
		- introduces another field in the frames
		- advanced networking topic, out of scope
	- ACCESS and TRUNK ports on networking switches
	- now, your physical network is managed via switch software
	- you cannot communicate between these networks without layer 3 device (like a router)
	- Public and Privte VIFs in AWS Direct Connect work using VLANs
- DNS
	- funtionally, a big database for looking up IPs by domain name
	- DNS Zone = database containing records (e.g., "\*.netflix.com")
	- ZoneFile = file storing the zone on disk
	- Name Server (NS) server that hosts 1 or more Zones (1 or more ZoneFiles)
	- authoritive servers are the geniune source of truth
	- there are thirteen root DNS server IPs around the world (U of Maryland, NASA, etc.)
		- these thirteen IPs use any-cast so there are realistically many more servers
		- the IP protocol has unicast, broadcast, multicast, anycast, and geocast addressing models

## 08-26-2025 - Learn Cantrill (Tech Fundamentals, Networking, Continued)

- DNS
	- ".com" is an example of a Top Level Domain (TLD)
	- if a Name Server and its Hosted Zone(s) are pointed to by an Authoritative server, they are Authoritative
		- THIS ONLY FOLLOWS FOR AN AUTHORATIVE TLD NAME SERVER!!!
	- DNS resolver in your router or ISP handles most work on your behalf
	- a DNS query can resolve to another DNS name (poor performance)
	- Domain Registrars are NOT the same as DNS Hosting Provider
		- many companies server as both though
		- e.g., Route 53
- DNSSEC - secure version of DNS
	- two main benefits over standard DNS
		- (1) Data Origin Authentication
		- (2) Data Integrity Protection
	- DNS cache poisoning is one issue DNSSEC solves
	- DNSSEC adds additional response data to DNS (does not replace DNS)
	- Chain of Trust used to verify DNS resolving
	- asymm encryption used to verify RRSIG signature values
	- Resource Record Sets (RRSETs) are verified not, individual resource records
	- Zone Signing Key (ZSK) and Key Signing Key (KSK) are critical
	- Zone Signing Key is encapsulated in single zone
		- it can be rotated freely without impacting parent zone
	- DS Records are used for validation in the Chain of Trust
	- the Signing Ceremony is how the Trust Anchor is established
	- HSMs are used to never expose the keys
	- the public "." DNS Root KSK verifies the Absolute Trust
	- many people are involved for redundancy and security
	- ceremony is repeated every three months (roughly)
- Border Gateway Protocol (BGP)
	- decides how things are routed from point A to point B
	- made up of Autonomous Systems (AS)
		- routers controlled by one entity, aka a network
		- they are treated as black boxes by BGP
	- ASNs are uniquely allocated by IANA
		- can use reserved, private ASNs for private peering
	- BGP operates over tcp/179
		- peering needs to be manually configured though
	- ASPATH is the best path to the destination according to the peers
		- doesn't care about condition or link speed of the topology
	- iBGP and eBGP for internal / external communication
		- mostly work with eBGP in AWS
	- artificially lengthen path to tune traffic
		- e.g., avoid using sattelite AS every time
- Layer 7 Firewalls
	- layer 3 or 4 firewalls cannot see additional info like the HTTP method being used
	- you can decrpyt HTTPS, check contents, re-encrypt
	- you could even modify content at the firewall
	- doesn't have to be the HTTP protocol, could be others like SMTP
- IPSEC VPN Fundamentals
	- a set of protocols to setup secure tunnels across insecure networks
	- provides authentication and encryption
	- between two peers (local and remote)
	- called IPSEC Tunnels (for "interesting" traffic)
	- two main phases
		- IKE Phase 1 (slow and heavy)
			- creates phase 1 tunnel (IKE SA, "security association")
			- can be reused for multiple phase 2's, between interesting traffic
			- Diffy Helman key and exchange material are used to create symmetric key
		- IKE Phase 2 (fast and agile)
			- bulk symmetric encryption of "interesting" traffic
	- two types of VPNs
		- policy-based VPNs
			- Rule Sets match traffic and direct to a pair of Security Associations 
			- more difficult to setup, but give you different security fo different types of traffic
		- route-based VPNs
			- target matching the given IP prefix
- AWS Organizations
	- member accounts' billing info is disregarded for Consolidating Billing
	- Organization Root is container for all accounts in the org
	- some orgs have dedicated identity accounts
		- identity federation can be used to access these identities with on-premise IdP
		- use "role switch" to gain access to other accounts in the organization

## 08-28-2025 - Learn Cantrill (AWS Orgs)

- each IAM user can have two access keys
- access keys can be..
	- created
	- deleted
	- inactive
	- active
- management account is NEVER impacted by Service Control Policies (SCPs)
- SCPs are "account permissions boundaries"
	- you can never restrict the account root user from doing things in the account, but you can restrict the account itself
	- therefore, you restrict the root user indirectly
- SCPs can be attached to AWS Orgs root, Organizational Units (OUs), and directly to accounts
- FullAwsAccess SCP policy makes SCPs act like a deny list architecture
	- there's an implicit deny all if you don't have this FullAwsAccess policy
- all AWS accounts have a root user, but they have no credentials by default if created from AWS Orgs
	- AWS Orgs can enable central root user configuration and delete existing root user credentials
- Security Token Service creates temporary credentials similar to long-term access keys
	- they do not belong to the specific entity
	- you can limit the permissions to a subset of the assumed role's permissions
		- this is done using Session Policies
- EC2 Instance Profiles are containers for IAM Roles the EC2 instance's services can assume
	- can only have one role / one instance profile per EC2 instance
- you CANNOT invalid temporary STS credentials, you must use the deny all policy trick for role assumptions before a certain timestamp!!!
	- once you assume the role, your temporary credentials will exist until their expiration time
- only identity-based policies are impacted by Permission Boundaries
	- resource-based policies are not impacted
- permissions boundary is also known as identity boundary
- example use case for permissions boundaries:
	- give "IAM Administrator" privileges to an IAM User
		- do NOT let them escalate their own IAM permissions
	- as a fail safe for other identities getting too much access (cross-account, etc.)
- policy evaluation logic
	- SCPs of the account containing the identiy are the only ones that matter!!!
		- meaning if you access a cross-account resource, SCPs for that account are irrelevant!!!
	- an allow from a Resource Policy returns early with allow (before permission boundary, session, policies, or identity policies)
		- but remember that explicit denies are still checked before this

## 09-02-2025 - Learn Cantrill (Cross-Account S3, AWS RAM, Service Quota, Identities and Federation, Networking)

- S3 ACLs use a Canonical Account ID
- may want to setup S3 buckets so that owner owns all uploaded objects
- AWS RAM potentially changes how you'd architect things
	- originally, accounts were isolated and then connected via transit gateways or VPC peers
- Availability Zone IDs actually stay consistent between accounts
	- AWS rotates which physical facilities serve us-east-1a, for example
	- AZ ID would be "use1-az1"
- need to accept resource share invite
	- unless your AWS Org is setup to automatically accept shares
- "Shared Services VPC" is a class AWS RAM pattern
	- particpants still own their resources
	- particants have read-only visibility of owner's networking resource
- Naming of resources can be per-account for AWS RAM shared resources
- AWS services typically have a per-region service quota
	- some service are per-account
- starting quotas are relatively low for professional work and architectures
- some services have hard limits
	- they can impact architecture choices
	- e.g., 5000 IAM Users per account
- Quota Request Templates can be used across your AWS Org
- can create CW Alarms for when nearing service limits
- there are multiple ways to interact with service quotas
	- exam questions are typically based around all these different methods
- SAML 2.0 Identity Federation
	- you can only ever interact with AWS resources using AWS credentials
		- you just gain these AWS credentials through Identity Federation
	- main selection criteria for this is
		- Enterprise Identity Provider
		- SAML 2.0 compatible
	- you would NOT use SAML 2.0 Identity Federation for Google logins!!!
	- SAML 2.0 typically used by large organizations, and especially those with a Windows-based IdP
- IAM Identity Center (Successor to AWS Single Sign-On (SSO))
	- AWS SSO is almost always preferred over direct SAML 2.0 Identity Federation
	- requires AWS Organization to be configured
	- "enterprise" or "workplace" identities => AWS SSO
	- "web" or "user" identities => AWS Cognito
- Amazon Cognito
	- naming in this service is very poor
	- provided authn, authz, and user management
    - User Pools are for signing in, signing up, and obtaining JWT tokens 
		- JWTs can't be used by most AWS services	
	- Identity Pools allow you to offer access to temporary AWS credentials
		- this is for either unauthenticated or authenticated identities
		- social logins or SAML 2.0 identities can be swapped for temporary creds
		- a User Pool login could be swapped for temporary creds
	- login with social would happen within User Pools but outside of Identity Pools
		- can then combine this architecture to avoid dealing with many different types of external auth tokens
		- this architecture is called "web identity federation" (WEBIDF)
	- "federation" is the process of swapping external identity tokens for AWS credentials
- Public vs Private AWS Services 
	- there are three different network zones to consider
		- public internet zone
		- AWS Public zone
		- AWS Private zone
- Dynamic Host Configuration Protocol (DHCP)
- DHCP Option Sets are immutable and can be attached to zero or more VPCs
- DHCP is how a device gets an IP, subnet mask, and default gateway
	- these are all automatically generated by AWS in each AWS VPC
- in AWS VPC, your DHCP Option Set can only control the DNS server to use
	- R53 Resolver by default
		- private and (potential) public DNS hostnames are generated automatically
	- could configure your own DNS server
	- could also configure NTP servers
- VPC Routers are always at the "subnet+1" address
- VPC Routers are controlled using route tables
- every subnet has a VPC Router Interface
- subnets are associated with ONE ROUTE TABLE
	- there's a default Main Route Table (RT) for the entire VPC
	- main RT should be left completely blank for security posture reasons
		- it gets automatically associated with subnets if the subnet's custom RT is removed
	- the route tables network prefix number determine the specificity of the route
		- e.g., "10.16.0.0/16"
- ephemeral port rangers are a big downside of stateless firewalls

## 09-03-2025 - Learn Cantrill (Networking, Continued)

- all subnets have an associated Network Access Control List (NACL) 
	- it's a stateless firewall
	- lowest rule processed first!!!
	- implicit DENY if no rule matches
	- default rules of NACLs allow ALL traffic (NACL is ignored)
	- NACLs can use EXPLICIT denies, which is useful against bad actors
- Security Groups
	- stateful firewall
	- only IMPLICIT denies
	- higher up the networking stack, so can support logical resources
		- this includes itself and other AWS resources
	- security groups are NOT directly attached to subnets or instances
		- they are attached to Elastic Network Interfaces (ENIs)!!!
	- logical referencing scales very well
- AWS Local Zones
	- mostly for low latency benefits
	- can treat them like any other Availability Zone (AZ)
	- not all products support them
	- they still rely on parent region for some things (e.g., EBS Snapshots)
	- DX to local zones IS supported
- Border Gateway Protocl (BGP)
	- must manually configure any peering
	- eBGP is for routing between Autonomous Systems (AS)
	- eBGP is primarily what AWS architects would care about
	- prefix paths to avoid issues of slow connections (e.g., satellite)
- Global Accelerator
	- need to distinguish between CloudFront and Global Accelerator use cases
	- anycast IP addresses are the key technology
	- "get into the optimized AWS network faster"
	- Global Accelerator works for TCP or UDP!!!
	- it's a network product, it does NOT cache things
	- CloudFront is for HTTP/S only!!!
- AWS Site-to-Site VPN
	- a logical IPSec connection between a VPC and on-premise network over the public internet
		- could also be over Direct Connect (DX)
	- Virtual Private Gateway (VGW) is associated with a single VPC
	- Customer Gateway (CGW) is either..
		- the logical configuration within AWS
		- the physical router located on-premise
	- the VPN connection is between the VGW and the CGW
	- "partial high availability" if you only have a single on-premise router
		- resolve by adding more VGW endpoints and another router
	- Static vs Dynamic VPN
		- Dynamic VPN requires routers to support BGP
		- enable "route propogation" on the VPC to detect routes from the VGW whenever a VPN is active
	- exam considerations
		- VPN has a 1.25Gbps limit (not including your on-premise router and encryption overheads)
		- latency over public internet
		- charger per hour and per GB out
		- on-premise internet plan may have limits
		- speed of setup (takes a couple hours to configure)
		- use as backup for Direct Connect or with Direct Connect
- Transit Gateway (TGW) 
	- single network object to connect many VPCs to many on-premise networks
	- highly available and scalable (like other network gateways)
	- can connect to...
		- VPC
		- Site-to-Site VPN
		- Direct Connect Gateway
	- can peer Transit Gateways across regions and across accounts
	- supports transitive routing, so you do not need a mesh architecture
	- can share your TGW via AWS RAM

## 09-15-2025 - Learn Cantrill (Transit Gateway, VPC, Continued)

- Transite Gateway (Deep Dive)
	- can peer transit gateways (up to 50 peers)
		- across regions and accounts
		- data is encrypted just like with VPC peering
	- all attachments propogate routes to the TGW's one route table (RT)
		- NO ROUTE PROPOGATION OVER PEERING, THOUGH
		- must use STATIC ROUTES
	- should configure unique ASNs for future route propogation features
	- association vs propogation is key for more advanced architecures
		- can use this to isolate routing domains, which is critical in practice
- Advanced VPC Routing
	- subnets have one route table, typically the implicit one inherited from parent VPC
	- can have 50 static routes and 100 propgated routes
	- send traffic based on destination, target, and priority order
	- more specific routes (longest prefix) always win
	- static routes have higher priority than dynamic (propogated routes)
	- good example of how to use route tables to ameliorate overlapping VPC CIDR ranges
	- routing is typically about EGRESS not INGRESS
		- can use Gateway Route Tables for devices like IGW and VGW
		- e.g., forward all returning public internet traffic through a security appliance
- Accelerated Site-to-Site VPN
	- can use TGW to allow a pair of VPN tunnels to access multiple VPCs
	- acceleration gets your traffic onto the AWS network sooner, so less public network performance variance
	- you CANNOT use VGWs with the acceleration, ONLY TGW
	- fixed fee + transfer fees for acceleration
	- combines three services: S2S VPN, TGW, and the Global Accelerator
	- remember, TGW is almost always recommended now
- AWS Client VPN
	- managed implementation of OpenVPN
	- connect to a Client VPN endpoint
	- connect to single VPC
	- connect to 1+ Target Networks (subnets, high-availability)
		- can only pick one subnet per AZ
	- charged based on network association (an ENI device is created in each subnet)
	- integrates with identity providers and CloudWatch Logs
	- the client's existing route tables are completely replaced
		- couldn't even access their local network
		- this can be fixed using Split Tunnel Client VPN
		- Split Tunnel is NOT the default, needs to be enabled
- Direct Connect (DX)
	- physical connection (1, 10, 100 Gbps)
	- goes from on premsie --> DX Location --> AWS Region
	- really just a Port Allocation at a DX Location
		- need to have a 3rd-party telecom actually connect you to the port
	- pay for Port Hourly Cost and ONLY Outbound Data Transfer
	- NO INTERNET, just private and public AWS services
	- DX Locations are typically large regional data centers NOT owned by AWS
	- "Cages" for various customers in the data centers
	- Physical Connection Architecture
		- details about port configurations and fiber connections
		- seems like more detail than needed for the AWS Sol Arch Pro exam
	- MACsec (deals with lack of DX encryption)
		- adds encryption to layer 2 of networking stack
		- needed so that we do not need to trust the datacenter where port connection occurs
		- works hop-by-hop between switches / routers
		- can also be set up on a Link Aggregation Group (LAG)
		- does NOT replace IPSEC over DX
		- is capable of massive speeds (terrabit performance)
		- uses unidirectional channels
		- Secure Channel Identifier (SCI)
		- Secure Associations (sessions), exist one at a time
		- MACsec encapsulation (MACsec tag and Integrity Check VAlue (ICV))
		- MACSec Key Agreement
	- DX Connection Process
		- Letter of Authorization Customer Facility Access (LOA-CFA)
		- used at datacenter to allow your rented cage to connect to AWS' rented cage
		- the two routers are then connected (layer 1 physical connection networking is established)
		- there's now a continuous layer 2 data link connection between AWS and the on-premise network
			- DX Connections are a layer 2 connection!!!
	- DX Virtaul Interfaces
		- Virtual Interfaces (VIFs) allow multiple L3 networks to run on the DX Connection
			- these networks would be VPCs and the AWS public zone
		- concretely, VIFs are just BGP Peering Session
		- VLAN Tagging is used to isolate these networks
		- BGP exchanges routes and authenticates
		- VIF types
			- Public VIF - for public zone services (no VPC), or VPC services that have public IP addressing
			- Private VIF - anything connecting to a VPC from your on-premise network using private addresses
			- Transit VIF - allow communication between DX and TGW
		- each VIF is a VLAN/BGP Session
			- they can be extended into customer premises via Q-in-Q
	- Private VIFs
		- access 1* VPC using private IPs
		- attaches to VGWs
			- don't always need to terminate VIFs into VGWs
			- e.g., Direct Connect Gateway
		- IN THE SAME REGION as your terminating DX location
		- no encryption of VIFs (you must add HTTPS, for example)
		- if using VGW, Route Propogation IS enabled by default
		- when creating VIF, need to setup...
			- if in a multi-account setup, the destination account would be the interface owner (must accept)
			- VLAN ID (match customer side)
			- BGP ASN of on-premise network (public or private)
			- peer IP addresses (could auto generate)
			- you advertise either default network prefixes or specific corp prefixes
				- there is a HARD MAX of 100 prefixes before interface breaks
		- AWS then advertises the VPC CIDR and its BGP Peer IPs (/30's)
		- you can download the config file to speed up your customer configuration
		- Private VIFs can ONLY connect to VPCs in the SAME REGION as the DX Location
			- solved by DX Gateway
		- configure your ASN on the VIF, AWS ASN is configured on the VGW
			- your ASN is either a publically owned one, or 64512-65535
	- Public VIFs 
		- access Public Zone services
			- includes elastic IPs (EC2 instances) and public services (e.g., S3)
		- can access ALL public zone regions
		- AWS advertises all AWS public IP ranges to you
		- you advertise any public IPs you own over BGP
		- tangential - BGP Communities are used
			- filter routes you receive by geography
		- your prefixes don't leave AWS (not transitive)
			- this means you won't advertise your public IPs to other AWS customers
			- HOWEVER you could access ANY Elatsic IP address for, e.g., an EC2 instance???
		- configuration is much like Privat VIFs
		- there's some verification on AWS's end for the BGP prefixe advertisements

## 09-20-2025 - Learn Cantrill (Direct Connect, Route53, Continued)

- DX, VPN and Public VIF
	- can combine VPN with Public VIF for security, speed, consistency
	- note: uses PUBLIC vif, since connecting to VGW or TGW public endpoints
	- MACsec still used here for single hop in data center
	- typical to run VPN over public internet first, or for redundancy
	- you can benefit from the global AWS network and connect to remote regions
- DX Gateway (DXGW)
	- DX is a regional service
	- add multiple for high availablity
	- Public VIF can access all AWS Public Regions
	- Private VIF can only access VPCs in the same region via VGW
	- DX Gateway solves this by allowing On-Premise to talk to any VPC
	- DX Gateway is a global service
	- it DOES NOT allow the VPCs to talk to one another, though
	- limit:
		- 1 Private VIF can connect to 1 DX Gateway
		- 10 VGW per DX Gateway
		- 50 Private VIFs per DX Connection = 50 DX Gateways
		- 50 DX Gateways with 10 VPCs each = 500 VPCs connected
		- also: 1 DXGW can accept up to 30 Private or Transit VIFs
			- DXGW never uses Public VIFs
	- DX Gateway is free (pay for underlying traffic)
	- could get around inter-VPC talking issue by going through customer router back to DX Gateway
	- DX Gateway works in multi-account
		- create "Shared Services" account
		- other accounts create an "association proposal"
		- if accepted, other accounts can access on-prem via Private VIF
- DX, Transit VIFs and TGW
	- a DX Connection can have a single Transit VIF
		- this might be 4 now???
		- Public VIF and Private VIF limit might be 50 total???
	- Transit VIF is used to connect up to 3 TGWs to the DXGW
		- this means you cannot use the DXGW anymore for a Private VIF!!!
		- i.e., you CANNOT mix Private VIFs and Transit VIFs in a single DXGW
	- DXGW doesn't route between attachments, use TGW Peering
	- each TGW can be attached to up to 20 DXGWs
	- TGWs support 5,000 attachments, and can peer with 50 other TGWs (each with 5,000 attachments)
	- main benefit of TGWs is that you can route across DX Gateway attachments
		- this is for the case where you are within the same AWS Region
		- e.g., going through DXGW from one on-premise site to another
		- this would not be possible with just DXGWs
	- to route across DX Gateways in multiple regions...
		- simply peer the TGWs you have in separate AWS regions
		- the DXGWs automatically can send traffic between on-prem locations
- DX Resilience
	- DX is not a resilient product, it's physical and has many single points of failure (SPOFs)
	- potential fixes
		- provision two DX Connections at same location
			- these will be on separate AWS DX Routers
		- have two customer routers
		- two physical cable paths from DX location to customer premises
		- two completely separate customer premises
		- two completely separate DX locations
		- most exteme, two DX locations each with...
			- two DX Connections (separate cross-connect cables)
			- two AWS DX Routers
			- two customer routers
	- note that a S2S VPN backup is another alternative for achieving high-availability
- DX Link Aggregation Groups (LAGs)
	- multiple physical connections configured to act as one
		- this means multiple DX Connections being viewed as one
	- up to 200 Gbps total speed per LAG
	- although they provide some level of resiliency (switch port), AWS does NOT market them this way
	- complete hardware (switch) failure is still SPOF, so focus on speed benefit during exam!!!
	- active / active architecture
	- max of 4 connections per LAG
	- all connections must be same speed
	- all connections must terminate at same location (same DX Location)
	- "minimumLinks" used to define if LAG is active or inactive (failed state)
	- ports get allocated on the same AWS DX Router chassis
		- allocate early before physical ports are taken by other people
	- remember, this is NOT a resiliency product!!!
- Route53 Fundamentals
	- can register domains
	- can host Zones that are on managed Nameservers
	- global service (resilient)
	- a Zone file is just a database for a particular domain
		- has records or recordsets within it (in AWS terminology)
	- a Hosted Zone is just AWS terminology for them managing your domain's Zone file
- DNS Record Types
	- Nameserver (NS)
	- A and AAAA (same thing, host to IP, IPv4 or IPv6)
	- CNAME (host to host, cannot point to raw IPs)
	- MX (how a server can find the mail server for a specific domain)
		- has priority recoreds (lowest highest) 
	- TXT Records (provide arbitrary text to your records)
		- used to extend DNS functionality
		- e.g., validate that you own a domain by setting specific requested text value
		- e.g., fight spam by whitelisting who can send emails on your behalf
	- Time To Live (TTL), your DNS Resolver will cache (authoritative) query responses for this amount of time
		- good to lower this days or weeks in advance of any work you're performing
- AWS X-Ray
	- a distributed tracing application
	- Tracing Header (trace ID) - created by first service to track entire processing
	- Segments - data blocks produced by services and added to trace
	- Subsegments - more granular data (e.g., calls to other services)
	- Service Graphs - JSON Document detailing services and resources in the application
	- Service Map - visual version of the service graph showing traces
	- various agents needed to produce X-Ray segments
		- EC2 X-Ray agent
		- ECS agent in tasks
		- Lambda (enable option)
		- Beanstalk preinstalled agent
		- API Gateway per stage option
		- SNS configuration options
		- SQS configuration options
	- need to provide IAM PERMISSIONS for writing data into AWS X-Ray!!!

## 09-27-2025 - Learn Cantrill (AWS Private Link, VPC Endpoints, IPv6, Advanced Network Design)

- AWS Private Link
	- provides private connectivity between VPCs, AWS services, and on-premises applications, securely on the Amazon network
	- primarily used to securely provide a service to another AWS account (or vice versa)
	- remember AZ vs AZ IDs
	- VPC Service Provider and (many) VPC Service Consumers
	- Network Load Balancers (NLBs) and another cross-zone LB ensure HA
		- multiple endpoints also provide HA
	- secured using Security Groups and NACLs
	- secured using typical IAM Users and Roles
	- private DNS is supported
	- works with DX, S2S VPN, and VPC Peering 
	- you just need to know theory for the exam
- VPC Endpoints - Gateway
	- provide private access to public AWS services
	- e.g., access S3 from a private VPC without an IGW or NGW
	- created per service and per region
		- HA by default
		- this is different than VPC Endpoint Interfaces
	- created in a VPC, then assigned to subnets
	- it essentially manages the route table in the VPC subnets to point to the VPC Router, then the AWS services
		- "works using prefix lists and route tables"
		- no changes to your existing applications
	- resource policy (Endpoint Policy) used to control access
	- CANNOT access resources cross-region!!!
		- the VPC Endpoints are NOT accessible outside the VPC
		- even with VPC Peering or Transit Gateways
	- good for preventing leaky S3 buckets, only allow access from the VPC Endpoint Gateway
- VPC Endpoints - Interfaces
	- similar functionality to VPC Endpoint Gateways, BUT KEY ARCHITECTURAL DIFFERENCES
		- provide private access to AWS Public Services
	- key difference is they are NOT highly-available by default
	- they are an ENI added to specific subnets
	- remember one subnet means one Available Zone (AZ)!!!	
	- key difference is they are controlled via Security Groups
		- VPC Endpoint Gateways do NOT use SGs, they use IAM permissions
	- resource policies (Endpoint Policies) supported
	- uses AWS PrivateLink under the hood
	- they create new service endpoint DNS your service could use
		- e.g., vpce-123-xyz.sns.us-east-1.vpce.amazonaws.com
	- by default now, PrivateDNS overrides the default DNS for services!!!
		- so, sns.us-east-1.amazonaws.com will magically go to private DNS endpoint
		- "works by using DNS"
		- you do not need to make application changes, because PrivateDNS is the default
- Advanced VPC DNS and DNS Endpoints
	- in all VPCs and subnets, a DNS address (.2) is reserved
		- called the Route53 Resolver (used by default)
		- gives access to both Public and Associated Private Zones
	- this DNS is only accessible from within the VPC, so difficult for hybrid networking
	- before Route53 Endpoints, the solution was a "DNS Forwarder" EC2 instance in the VPC
	- Route53 Endpoints
		- VPC interfaces (ENI) accessible over VPN or DX
		- "inbound" is considered on-premises into AWS
		- "outbound" is handled with Rules for request forwarding
		- can use DX or VPN connections
		- can handle about 10,000 queries per second per endpoint
		- deployed per region (per VPC)
- IPv6 Capabilities in VPCs
	- private and public IPv4 addresses are NOT compatible
		- requires NAT Gateway to translate public IPv4 address
	- you will NEVER see an EC2 instance's operating system configured with a public IP
		- this is handled by gateway appliances outside of EC2
	- every IPv6 addresses is considered public, so NAT is not used
	- each VPC gets an IPv6 CIDR block
		- can BYOIP or have AWS provision you some
		- very large number, again, IPs are no longer scarce resources
		- can have 256 subnets per VPC
	- routing handled the same, but separate route table entries for IPv4 and IPv6
		- this means IPv4 and IPv6 devices can route to one another
	- you can limit IPv6 inbound traffic with an "Egress Only IGW"
		- this gives you the equivalent functionality of IPv4 private address behind a NAT
		- you would need to change the default IPv6 route to point at the Egress Only IGW instead of the standard IGW
		- you can have multiple gateways in a single VPC
	- very common exam question is how to limit IPv6 ingress traffic!!!
	- you can retroactively add IPv6 addressing to existing VPCs and subnets
		- you then configure services (like EC2) to use IPv6 addressing
- Advanced VPC Structure - How Many AZs for High Availability?
	- adding more AZs does not necessarily increase availability (consider application minimums)
	- Buffer AZ, Nomincal AZs, Nominal Instances -> Optimal Apps per AZ
	- Subnets and Tiers
		- separate subnets = separate tiers
		- no longer necessary to use legacy application tier design for infrastructure
		- one big benefit of using more subnets is NACLs that have EXPLICIT DENY
		- you can keep DBs in a public application subnet and just NOT provision it a public IP
			- SGs also limit DB connections from just your application
		- a primary reason to split subnets is for separate route tables
			- e.g., directing different resources to different gateways / on-premise / etc.
				- NAT Gateway can't be in same subnet as the instances that use it (both need different default routes)
			- general rule is you MUST assume routing is shared by ALL resources within a subnet
				- even specific routing rules aren't bulletproof
		- considerations for subnets and tiers
			- public vs private addressing is irrelevant (security can be handled fine)
			- different routing needs -> multiple subnets
			- a public ALB (in a public subnet) can communicate with private instances (in private subnets)
			- multiply your final number of subnetst by your needed number of AZs

## IAM Access Analyzer

- access advisor - uses data analysis to help you set permission guardrails confidently
  - provides service-last-accessed information for accounts in your organization.
  - determine the services not used by IAM users and roles.
  - can later implement permissions guardrails using SCPs that restrict access to those services
- access analyzer - lets you know if you've shared resources to outside accounts (Zone of Trust)
  - also lints your IAM policies' grammar, suggestions, etc.
  - generate policies based on real activity (via CloudTrail logs)
- assuming a role drops all of your existing permissions

## AWS STS (Security Token Service)

- Security Token Service (STS) assume role within...
  - your account
  - another account
  - identity federation (3rd party authenticated users)
  - AWS services (Lambda, for example)
- Again, STS will drop all your current permissions
- Least privelege + auditing using CloudTrail (require MFA, CLI, etc.)
- External ID (secret between you and 3rd party, chosen by 3rd party)
- Confused Deputy (exam question)
- GetFederationToken API call probably NOT on the exam

## AWS Identity Federation & Cognito

- Identity Federation (users outside AWS get access to your account)
  - e.g., your company already uses Active Directoy
  - need a "trust relationship" between identity provider and AWS
  - STS AssumeRoleWithSAML
- Customer Identity Broker Application pushes the burden of appropriate IAM Role determination to the Custom Identity Broker
- For some reason, the flow is slightly different (extra step) to go to the Management Console?
- Use special Policy Variables to actually restricted the authenticated users to certain resources

## AWS Directory Services

- Domain Controllers in Microsoft AD???
- Connecting to on-premise AD is an IMPORTANT exam topic
- This is NOT replication, just talking to each other
  - via Direct Connection (DX) or VPN

## AWS Organizations

- OrganizationAccountAccessRole (gives management account admin rights in member account)
- Create manually if inviting an existing account into organizational
- Multi Account Strategies (practical examples??)
- Volume discounts when aggregating cost within Organization
- **Accounts cannot leave Organization once they've accepted membership!**
- Reserved Instance discounts and Saving Plans caveats

## Service Control Policies (SCP)

- "Management account can do anything, no matter what!"
- Explicit allows (FullAWSAccess) needed at every OU and account (even root)
  - Management Account would still have full access, but nested OUs would not
- Cannot restrict access for Service-linked roles
- IAM Policy Evaluation Logic (shouldn't memorize, but should make sense)
- Restricting specific Tags on AWS resources
  - exam question: ForAllValues or ForAnyValue
- Can deny entire regions via SCP
- Are tag-based IAM conditions only available in SCPs???
- AI training and backup policies

## IAM Identity Center

- Use single credentials to login to multiple different AWS accounts
- Any SAML2.0 IdP integration
- IAM Identity Center Group -> users > permission set -> organizational unit
  - multi-account permissions
- attribute based access control (ABAC)

## AWS Control Tower

- on top of AWS Organizations
- Why does AWS Service Catalog need to be used as well???
- Guardrail Levels - mandatory, strongly recommended, elective

## AWS Resource Access Manager (RAM)

- avoids resource duplication (e.g., VPC subnets PRIMARILY)
  - there are a lot of VPC-specific considerations
  - e.g., cannot share security groups and default VPC
- should just briefly review the capabilities for the main services
- avoids "VPC peering"
- cannot view / modify / delete other resources, just talk to them ("view" as in through the management console???)
- "Security Groups from other accounts can be reference for maximum security"
  - need to get a concrete example of this???
- Route 53 Outbound Resolver and forwarding rules to your DNS
  - need to get a concrete example of this???

## Summary

- the exam is always going to push you towards the more modern solutions
  - e.g., use SSO instead of SAML federation

# Section 04 - Security

## AWS CloudTrail

- By default, Management logs are always enabled
- Data logs are high volume, not enabled by default
- CloudTrail Insights is for anamoly detection and service limits, etc.
- S3 + Athena for querying logs >90 days old

## CloudTrail - EventBridge Integration

- Send notifications via EventBridge when a specific API call is made.

## CloudTrail - SA Pro

- Solutions Architecture: Delivery to S3
- Solutions Archtecture: Multi Account, Multi Region Logging
  - Use S3 bucket resource policy for cross-account access.
  - "Security account for audit"
-
- Solutions Archtecture: Alert for API Calls
  - Can trigger on aggregates of API calls
  - e.g., a lot of denied calls, a lot of resource deletions, etc.
- Solutions Archtecture: Organizational Trail
  - Must be created in the Management account!!
  - S3 bucket with account numbers as object key suffix
- 15 mins delivery of CloudTrail events
  - EventBridge is the fastest reactive way

## KMS

- Anytime you hear encryption, think Key Management Service
- You'd use an asymetric key if you have users who need to perform encryptions, but do not have the ability to make KMS service API calls.
- envelope encryption - data keys and wrapping keys
- keyrings - generate, encrypt, and decrypt data keys
- master key provider (alternative) - returns the wrapping keys you specify
- best practice to specify wrapping keys during decryption
- CloudHSM (Hardsare Security Module) for custom key stores
- External = BYOK
  - automatic rotation is NOT supported
  - four step process for importing an external key to KMS
- multi region keys are NOT global keys

## SSM Parameter Store

- integration with CloudFormation
- heirarchy of parameter folders
- trick: you can access Secrets Manager secrets through fancy Parameter Store paths.
- there are publical parameters for some AWS services that are also available at fancy paths.
- Parameter Policies (expiration dates) only avialable for _advanced_ parameters.

## Secrets Manager

- Sharing Across Accounts - view example solution in slides
  - RAM service CANNOT handle this

## RDS Security

- TDE = oracle, SQL Server
- IAM auth = MySQL, PostgresSQL, MariaDB
- authentication through IAM, but authorization through RDS still
- CloudTrail doesn't track queries made within RDS

## SSL Encryption, SNI & MITM

- SSL == TLS
- Possible that the client provides a second cert (two-way certificate)
- good diagram for understanding the handshake
- Server Name Indication (SNI) - multiple websites on a single server (ALB)
- avoid MITM attacks, DNSSEC for your domain is important

## AWS Certificate Manager (ACM)

- hosts public SSL certificates in AWS
- free and very convinient
- good to knows are important
- ACM is a **regional** service, deploy multiple certs across all your regions
  - CloudFront solves this issue

## CloudHSM (KMS adjacent)

- No API calls available, need the CloudHSM Client Software
- Redshift integration
- Good for SSE-C encryption (for S3)
- AWS just manages the hardware, not responsible for keys or users
- No free tier

## Solutions Architecture - SSL on ELB

- Using NLB, user data scripts on your EC2 instances to install SSL certs (via SSM Parameter Store, IAM permissions)
  - Alternative is to offload SSL coompute to CloudHSM (SSL Acceleration)
  - more secure because private key never leaves HSM device

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

## S3 Access Points

- fights unmanageable policies
  - control access within the bucket (object keys / paths)
- access point has its own DNS name
- can configure as public or private endpoint

## S3 Multi-Region Access Points (Global)

- Dynamically routes request to lowest latency buckets
  - Different S3 buckets, but with regional replication enabled (Bi-directional Cross-Region Replication)
  - must have bucket versioning enabled
- Failover control active/passive or active/active
  - active, in this case, means you can write to multiple regions/buckets and have it synced
- S3 is NOT A GLOBAL SERVICE BY AWS DEFINITION

## S3 Object Lambda

- relies upon S3 Access Point and S3 Object Lambda Access Point
- for, as an example, redacting or enriching data from the object, resizing an image, converting to another format, etc.

## DDoS and AWS Shield

- overview of types of attacks
- AWS Shield Standard to protect yourself at no cost
- AWS Shield Advanced is premium service for 24/7 DDoS protection
- AWS WAF - filter requests with rules
- CloudFront and Route52 have Shield enabled by default, a lot of work to attack
  - good because stops attack at the edge before your services
- be ready to auto scale (more $$$)
- serve static resources via S3 / CloudFront

## AWS WAF - Web Application Firewall (Layer 7 HTTP)

- is NOT for DDoS protection
- it is for layer 7 protection (e.g., IP addresses, SQL injection, size constraints, CAPTCHA)
- managed rules for convenience and speed
- Web ACL (WACL) logging can be sent to several sources, with limitations on throughput / delay
- good architecture example

## AWS Firewall Manager

- manage firwall rules across all AWS acocunts within an AWS Organization
  - AWS WAF
  - AWS Shield Advanced
  - Security Groups
  - AWS Network Firewall
  - and more!

## Blocking an IP Address

- NACL would be first line of defence within your public subnet
- ALB adds another line of defense (EC2 can be in private subnet with private IP)
  - can use Connection Termination at ALB, so ALB uses its own Security Group setup and makes separate connection to the EC2 instance.
  - this is the same for ALB or NLB.
- WAF then pairs with the ALB to filter IP addresses, and do much more defensive things
- NACL filtering is not helpful if clients are going through CloudFront first
  - in that case, put WAF on the CloudFront
  - could additionally use CloudFront Geo Restriction

## Amazon Inspector

- automated security assessements
- AWS System Manager (SSM) agent on EC2
- Inspector ONLY works for:
  - EC2
  - Amazon ECR container images
  - Lambda Functions
- Uses a database of CVE for package vulnerabilities
- Network reachability for EC2
- Results sent to AWS Security Hub
- Send findings to EventBridge as well
- there is a risk score associated with all findings

## AWS Config

- compliance (changes to resource config)
- it does not stop actions from happening
  - an AWS Organizations SCP would be good for this
- custom config rules must be defined in AWS Lambda
- SSM Automations can be used to remediate AWS Config Rules

## AWS Managed Logs

- logs generated by AWS services themselves
- mostly sent to S3 or CloudWatch logs
  - e.g., CloudFront

## Amazon GuardDuty

- machine learning findings can be sent to EventBridge
- good for CryptoCurrency attacks specifically
- Delegated Administrator = one account that can manage all the accounts in the org
- only the Organization Management Account can name the Delegated Administrator
  - not that it itself is NOT the Delegated Administrator

## IAM Conditions

- restrict API calls by IP address (aws:SourceIp)
- restrict by region (aws:RequestedRegion)
- restrict by the EC2 instance tags (ec2:ResourceTag)
  - related: aws:PrincipalTag/Department
- require user to have MFA (aws:MultiFactorAuthPresent)
- bucket vs object level S3 permissions
- aws:PrincipalOrgID
  - e.g., bucket resource policy allowing access for an entire AWS Organization

## EC2 Instance Connect

- SendSSHPublicKey API
- could use it yourself, but EC2 Instance Connect service uses it under the hood
- would be good to get a practical diagram / explanation of this???

## AWS Security Hub

- gives a security evaluation across SEVERAL AWS accounts
- aggregates several services' results in a digestible way
- Amazon Detective service will tell where the security issues come from

## Amazon Detective

- help you find the root cause of security issues and findings
  - uses ML and graphs
  - leverages GuardDuty, Macie, Security Hub, etc.

# Section 05 - Compute and Load Balancing

## Solution Architecture on AWS

- everything looks similar at a high level
- Glacier does NOT work automatically with CloudFront???
- CloudFront could serve your Web Layer, sometimes
- always tradeoffs as the solution architect
  - exam will ask you for the optimal choices

## EC2

- instance types
- nice website for choosing AWS resource instance types
  - https://instances.vantage.sh/
  - EC2, RDS, ElastiCache, OpenSearch, etc.
- Placement Group strategies
  - stop, use CLI, start again to move
- EC2 Graviton for best performance (no Windows instances)
- RAM IS NOT INCLUDED IN AWS EC2 METRICS
  - need to push custom CloudWatch Metrics
- Disk metrics are for Instance Stores only
- recovery options for Instance vs System status checks???

## High Performance Computing (HPC)

- cloud is well positioned for this
  - because it scales rapidly 0-->100-->0
- services for moving data around
- services for compute and networking
  - Spot Instances and Spot Fleets
- SR-IOV (EC2 Enhanced Networking)
  - ENA (Elastic Network Adapter)
  - Intel 82599 VF (Legacy ENA from Intel)
- Elastic Fabric Adapter (EFA)
  - only works for Linux
  - bypasses OS for direct node connections
- AWS Batch
- AWS ParallelCluster

## Auto Scaling

- Should look around the EC2 UI and try in sandbox
- Instance Refresh for updating EC2 Launch Templates
- can suspend unhealthy processes for debugging
- ELB health checks must be HTTP???

## Auto Scaling Update Strategies

- many different ways to update an Auto Scaling Group (ASG)
  - should be aware of them all
- Target Groups are a way you could split traffic between separate ASGs
- further separation achieved by Weighted Route 53 CNAME records
  - requires a second Application Load Balancer (ALB)
  - allows separate, manual testing
  - reliant on clients being well-behaved with DNS queries

## Spot Instances and Spot Fleet

- you choose your "bid" price for spot instances
- prices vary by AZ (not even just by region)
- Spot Fleet allocation strategy for Spot Instances from Spot Pools
  - lowestPrice
  - diversified
  - capacityOptimized
  - priceCapacityOptimized (recommended)
- spot fleet's main benefit is that it will choose cheapest spot instances for you

## Amazon ECS - Elastic Container Service

- container management platforms
  - Amazon ECS
  - Amazon EKS (managed Kubernetes)
  - AWS Fargate
    - serverless
    - works with both ECS and EKS
- useful for running batch processing / scheduled tasks on EC2 instances
- migrate legacy on-premise applications by containerizing them
- ECS IAM Roles
  - EC2 Instance Profile (talk to ECS, etc)
  - ECS Task IAM Role (talk to S3, Dynamo, etc.)
- Dynamic Port Mapping (ALB integration)
- inject secrets / configuration as env vars to running containers
- ECS Tasks Networking
  - none
  - bridge
  - host
  - awsvpc (default)
- Amazon ECS leverages AWS Application Auto Scaling
  - this services is used for scaling various other AWS resources
  - scaling strategies
    - Target Tracking
    - Step Scaling
    - Scheduled Scaling
- CPU and RAM tracked in CloudWatch at ECS Service level
  - Note the previous comment that "RAM IS NOT INCLUDED IN AWS EC2 METRICS"
- Fargate Auto Scaling is easier, because you don't need your ECS Service Auto Scaling to be in lockstep with your EC2 Auto Scaling
- FARGATE_SPOT for cost-savings
- ECR public and private repositories
  - IAM policies needed to give EC2 instance role access to images

## Amazon ECR - Elastic Container Registry

- cross region replications rather than rebuilding images
- image scanning
  - findings can trigger EventBridge
  - Enhanced Scanning (leverages Amazon Inspector)

## Amazon EKS - Elastic Kubernetes Service

- cloud agnostic
- supports EC2 or Fargate for containers
- any mention of "pods" = Amazon EKS
- should review how these would be exposed to public subnets???
- Managed vs Self-Managed vs No (Fargate) Nodes
- StorageClass manfiest on your EKS cluster
  - leverages Container Storate Interface (CSI)
  - multiple options, reference slides
- Amazon EFS is only option that works with Fargate!

## AWS App Runner

- deploy web applications without knowing anything about running the applications at scale
- just start with app code or container image
- VPC access support

## ECS Anywhere and EKS Anywhere

- ECS Anywhere
  - deploy native ECS tasks in any environment
    - ECS Container Agent
    - SSM Agent
  - "EXTERNAL" launch type
- EKS Anywhere
  - create and operate K8 clusters created outside AWS
  - via the Amazon EKS Distro
  - EKS Connector (optional)
    - Fully Connected
    - Partially Disconnected
    - Fully Disconnected

## AWS Lambda - Part 1

- a lot of integrations
- a lot of languages
  - Customer Runtime API (Rust, Golang, etc.)
- lambda supports custom images, but for exam prefer ECS / Fargate
- limits
  - up to 10 GB RAM
  - CPU linked to RAM, not configurable
  - 15 minute timeout
  - /tmp storage limit 10 GB
  - etc. (look at slides)
- sync vs async payload limits???
- AWS Service Quotas service for requesting more concurrency
- Reserved Concurrency to avoid throttling
- CodeDeploy for automated traffic shifts
  - Linear
  - Canary
  - AllAtOnce
- Pre and Post Traffic hooks
- monitoring
  - need to ensure Lambda has execution role with an IAM policy that authorizes CloudWatch Logs
  - AWS X-Ray also available (configure, then use AWS SDK in code)
  - again, needs correct IAM policies

## AWS Lambda - Part 2

- lambda in public AWS cloud by default
  - this is different than a public subnet
  - VPC managed by AWS that you have no control over
    - allows public (stateful) egress, blocks ingress
  - can't access VPCs and private subnets
- lambda in a VPC
  - assign Security Group
    - can access private resources as expected
  - should review all networking concepts???
  - access public internet via
    - Network Address Translator (NAT) gateway in public subnet
    - then, Internet Gateway (IGW)
    - alternatively, use VPC Endpoint for private connection to public API like DynamoDB???
  - lambda in public subnet can NEVER access the public internet
  - lambda ALWAYS has access to CloudWatch Logs
- use ENI, NATGW, Fixed Elastic IP, and IGW to maintain static IP on public internet??
- synchronous invocations for CLI, API Gateway, etc.
  - client handles all error handling
- asynchronous invocations for S3, SNS, EventBridge, etc.
  - should be idempotent
  - can send to SNS or SQS DLQ after 3 failed tries
- architecture example where SNS invokes rapidly without DLQ opportunity
  - delay vs batching and retry tradeoffs

## Elastic Load Balancers - Part 1

- types of load balancers and which protocols they support
- Classic Load Balancer (v1)
  - need distinct SSL certificates for each
  - Subject Alternate Name (SAN) vs Server Name Indication (SNI) for Application Load Balancer (ALB)
  - SSL authentication happens on EC2 instance
- Application Load Balancer (v2)
  - load balance multiple applications on same machine (containers)
  - great for ECS integration
  - can do more complex things, like route to Target Groups based on query params
  - Target Groups
    - EC2 instances (managed by an Auto Scaling Group??? Alternatives???)
    - ECS tasks
    - Lambda functions
    - IP Addresses (must be private IPs)
- Network Load Balancer (Layer 4)
  - forwards TCP and UDP traffic to instances
  - high performance
  - one static IP per AZ
    - use Elastic IP for whitelisting???
  - NOT available in AWS free tier
  - Target Groups
    - EC2 instances
    - IP Addresses
    - Application Load Balancer??? (very common pattern)
      - keep static IP but use Layer 7 features of ALB
  - Regional NLB DNS returns IP for each enabled AZ of the NLB
  - Zonal DNS Name (prefixed AZ name) gives single NLB node IP
    - avoids data transfer costs and reduces latency
    - would need to implement app-specific logic
- Gateway Load Balancer (Layer 3, works on packets)
  - virtual appliance (VA) are preconfigured software solution, often packaged as a Virtual Machine Image (VMI) (AMI), that provides specific functionalities similar to a physical appliance
  - functions
    - Transparent Network Gateway (single entry/exit)
    - Load Balancer (to virtual appliances)
  - GENEVE protocol on port 6081
    - UDP port all traffic is sent to
    - adds headers to network packets to create virtual networks over existing infra
    - headers then get stripped off and packet is routed to destination within the virtual network
  - Target Groups
    - EC2 instances
    - IP addresses (must be private IPs)

## Elastic Load Balancers - Part 2

- cross-zone load balancing
  - cross-zone load balancing (availability zone)
    - evenly across all EC2 instances
  - without cross-zone load balancing
    - distributed between instances of each AZ
  - CLB (disabled by default, no charges if enabled)
  - ALB (always on, no charges)
  - NLB (disabled by default, charges if enabled)
  - GLB (disabled by default, charges if enabled)
- sticky sessions (session affinity)
  - same instance always serves client by using cookies
  - request routing algorithms
    - least outstanding requests (CLB and ALB)
    - round robin (CLB and ALB)
    - flow hash (NLB)

## API Gateway - Part 1

- 29 second timeout (think about lambda timeout >29 seconds)
- 10 MB max payload size
- Deployment Stages
- how does API Gateway interact with an ALB???
- expose...
  - HTTP (ALB integration???)
  - Lambda
  - AWS Service API
- pre-signed URL to get around API Gateway payload size limits
- endpoint types
- caching (300 second TTL by default)
  - defined per stage
  - override cache settings per method
- error codes (502, 503, 504 specifically)
  - out of order invocations???
- security
  - SSL certificates
  - resource policies
  - IAM Execution Roles (to access services like Lambda)
  - CORS (cross-origin resource sharing)
- authentication
  - IAM credentials via Sig V4
  - Lambda Authorizer
  - Cognito User Pools
- CloudWatch Logs
  - enabled at stage level (ERROR, INFO)
  - can send logs to Kinesis Data Firehose, alternatively
- CloudWatch Metrics
- X-Ray for tracing full architecture picture

## API Gateway - Part 2

- Usage Plans and API Keys
- WebSocket functionality
  - DynamoDB example
  - @connections for replies to clients
  - uses HTTP POST with IAM Sig V4
- private API Gateway APIs
  - only accessible from VPC with a VPC Interface Endpoint
  - VPC Interface Endpoint can be used for multiple private APIs
  - can use aws:SourceVpc and aws:SourceVpce in API Gateway resource policies
    - this includes across AWS accounts

## AWS AppSync

- if you hear GraphQL, think AWS AppSync
- real-time with WebSocket or MQTT on WebSocket???
- mobile apps: local data access and data sync???
- Cognito auth that uses Groups for fine-grain access

## Route 53 - Part 1

- Hosted Zone = management system for DNS records of a domain and its subdomains
- record types
  - A, AAAA, CNAME, and NS are only relevant ones
  - can't create CNAME record for the top node of a DNS namespace (example.com)
- AWS resources expose an AWS hostname
- ALIAS records work for both ROOT and NON ROOT DOMAINS
  - free of charge
  - native health checks
  - targets include ELB, CloudFront Distribution, and others???
  - you CANNOT set an ALIAS record for an EC2 DNS name???
- TTL cost / outdated record tradeoff
- TTL required for all DNS records other than ALIAS
- Routing Policies
  - simple (no health checks)
  - weighted (health checks)
  - latency-based (health checks)
  - failover (Active-Passive) (health check mandatory)
  - geolocation (health checks)
    - based on user location (e.g., United States), not traffic to AWS regions
  - geoproximity (does this have health checks???)
    - based on user location (e.g., latitude / longitude), not traffic to AWS regions
    - must have Route 53 Traffic Flow enabled
    - uses Bias to manipulate weighting
    - Traffic Flow for maintaining large and complex record configurations
      - configurations can be saved as Traffic Flow Policy
      - Traffic Flow Policy supports versioning
  - multi-value (health checks)
    - limit 8 healthy records returned per query
    - is NOT a subsititute for an ELB
  - IP-based (does this have health checks???)
    - provide list of CIDRs for your clients

## Route 53 - Part 2

- private vs public Hosted Zones
- must enable VPC settings for internal private DNS / Private Hosted Zone
  - enableDnsHostnames
  - enableDnsSupport
- how does DNS Security Extensions (DNSSEC) work exactly???
  - only for Public Hosted Zones
- third-party registrar by updating registrar's NS record
- health checks are only for public resources (not the same as Public Hosted Zone???)
  - they can publish CloudWatch Metrics
- health check types
  - an endpoint
  - other health checks (Calculated Health Checks)
  - CloudWatch Alarms (full control)
- about 15 global health checkers will check endpoint health
- first 5120 bytes of the response can be used to pass or fail the check
- for private endpoints, health checkers don't have access to the VPC or on-premise resource
  - solution is CloudWatch Metric, CloudWatch Alarm, health check looks at Alarm

## Route 53 - Resolvers and Hybrid DNS

- Route 53 Resolver is what typically answers DNS queries
  - what is a local domain name for an EC2 instance???
  - is an VPC EC2 domain name visible to a public Hosted Zone???
  - are EC2 domain names separate from things you put in a private or public Hosted Zone??? somewhat built-in feature of Route 53???
- Hybrid DNS = resolving DNS queries between VPC and your network (other DNS resolvers)
- Inbound Endpoint (your network resolves AWS resources)
- Outbound Endpoint (Route 53 Resolver resolvers your network resources)
  - Resolver Rules are used to implement this (most specific match)
    - Conditional Forwarding Rules (Forwarding Rules)
    - System Rules
    - Auto-defined System Rules
  - Resolver Rules can be shared across accounts using AWS RAM
    - managed centrally in one account
    - multiple VPCs send DNS queries to the target IP defined in the rule
- endpoints are associated with one or more VPCs in the same AWS region
- create in two AZs for high availability
- need to link on-premise network via AWS VPN or Direct Connect

## AWS Global Accelerator

- use AWS internal network to route traffic to your applications faster
- 2 "Anycast IPs" created for your application
- these IPs send traffic directly to Edge Locations
- targets are EIP endpoints, EC2 instances, ALB, NLB, public or private
  - public or private what though???
- client IP address is NOT preserved for EIP endpoints
- has health checks, failovers, disaster recovery
- security
  - only need to whitelist 2 IPs
  - DDoS protection with AWS Shield
- superior to CloudFront when dong non-HTTP things
  - proxies packets at edge to applications running in one or more AWS regions
  - ex: UDP, TCP, MQTT, VOIP
- also superior for HTTP things that require static IP addresses
- OR deterministic, fast regional failover (intelligent routing, no client cache issue because static IP)

## Comparison of Solutions Architecture

- good target CPU utilization for ASG is between 40-70%
- ALB and Lambda is something like 10-20x cheaper than API Gateway and Lambda
  - can use AWS WAF with the ALB and Lambda solution
- soft limits of 10,000 requests per second and 1000 concurrent Lambda for API Gateway

## AWS Outposts

- Hybrid Cloud = businesses keep on-premise infra alongside cloud infra
- an "Outposts Racks" is installed on-premise with pre-loaded AWS services
- same APIs as usual, but you are responsible for physical security of hardware
- AWS DataSync could be used to sync S3 on Outposts bucket to standard Amazon S3 bucket

## AWS WaveLength

- infra deployments to telecomms companies' 5G datacenters / networks
  - deployed to the 5G edge
  - traffic may never leave the Communication Service Provider's (CSP's) network
  - if needed, high-bandwidth and secure connection to the parent AWS Region
- if 5G is mentioned, it probably related to AWS WaveLength

## AWS Local Zones

- for latency-sensitive applications
  - puts select resources / services in "extended" AWS region
  - e.g., "Boston" in us-east-1

## Quiz

- dedicated host vs reserved instance vs host affinity
- IAM task role vs EC2 instance role
- EC2 Lifecycle Hooks for troubleshooting
- AWS App Runner for simple container deployments
- DNS does NOT have anything to do with protocols like HTTP vs HTTPS
- Gateway Load Balancer for individual packets
- Edge-Optimized API Gateway must have ACM certificate in us-east-1???

## Study Group Questions

- you can suspend and resume Amazon EC2 Auto Scaling processes (e.g., Terminate)
- "awsvpc" networking mode gives ECS Tasks same networking properties as EC2 instances
- use API Gateway if there is mention of API keys
- EC2 instance termination protection does not stop auto-scaling events / termination
- Elastic IP Addresses must be public??? Not in private subnets???
- enableDnsHostnames vs enableDnsSupport
  - enableDnsHostnames allows instances with assigned public IPs to have corresponding DNS hostnames in the <region>.compute.amazonaws.com domain.
  - enableDnsSupport enables DNS resolution within the VPC, meaning your instances can resolve the DNS names of other instances.
- how does ECS Anywhere work (more implementation details)???
- AWS AppSync is not for session data, it's a GraphQL service
  - ElastiCache (Redis) would be more appropriate for session data

# Section 06 - Storage

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

## Amazon EFS (Elastic File System)

- mounting???
- can be mounted on many EC2 instances
- bill by GB used, not provisioned (unlike EBS)
- doesn't work for Windows AMIs
- Security Groups for configuring access
- limit to one VPC, then one ENI (mount target) per AZ
- Performance Mode vs Throughput Mode???
- Storage Classes or Storage Tiers???
- EFS One Zone-IA???
- on-premise server must use the IPv4 of the ENI (not DNS)
  - EC2 instance can use VPC peering and DNS
- AWS Site-to-Site VPN???
- combine IAM permissions with EFS Access Points
  - POSIX users and groups
- can use resource-based policies too, like with S3
- Cross-Region Replication
  - provides RPO and RTO
  - does NOT affect provisioned throughput

## Amazon S3

- Storage Classes (e.g., Intelligent-Tiering)???
  - Lifecycle Policies to move data between these (or delete)
- Replication Time Control (RTC), 15 minute SLA with CW Alarms
- S3 events and Amazon EventBridge integration
- Bucket Prefixes affect read/write request throughput???

## Amazon S3 - Storage Class Analysis (Analytics)

- does NOT work for One-Zone IA or Glacier
- visualize with Amazon QuickSight
- useful to put create / improve Lifecycle Rules
- Storage Classes are per object, many different ones per bucket

## Amazon S3 - Storage Lens

- metrics can be exported daily into another S3 bucket (CSV, parquet)
- default dashboard
  - data from across multiple accounts and multiple regions
- free and paid metrics
  - available for 14 days and 15 months, respectively
- various metric names to memorize???

## S3 Solution Architecture

- exposing static objects
- indexing objects in DynamoDB
- dynamic vs static content
  - AWS DAX (DynamoDB Accelerator)
  - CloudFront / S3 auth via either...
    - OAC (Origin Access Control)???
    - OAI (Origin Access Identity)???

## Amazon FSx

- run managed versions of Lustre, Windows File Server, NetApp ONTAP, OpenZFS, etc.
  - all different file systems
- FSx in general
  - Scratch File System vs Persistent File System
  - replace files within minutes
- FSx for Windows can still be mounted on Linux EC2 instances
- supports Microsoft Distributed File System (DFS) Namespaces
  - for grouping files across multiple FS
- Amazon FSx for Lustre
  - "Linux" plus "Cluster"
  - if you hear High Performance Computing (HPC), think Lustre
  - seemless integration with S3???
    - read as a file system???
    - S3 optional data repository???
  - can be used with VPN or DX
- Amazon FSx for NetApp ONTAP
  - for moving workloads already using ONTAP or NAS to AWS
  - very broad compatibility
  - storage shrinks / grows automatically
  - snapshots, replication, low-cost, compressions, AND dedup
  - PIT instantaneous backups
- Amazon FSx for OpenZFS
  - for moving workloads already using ZFS to AWS
  - very broad compatibility
  - high IOPS (1 million) and low latency (<0.5ms)
  - snapshots, replication, low-cost, compressions
  - NO DATA DEDUP
  - PIT instantaneous backups

## Amazon FSx - Solution Architecture

- AWS DataSync to migrate Single AZ FSx to Multi-AZ FSx
- can also do backup and restore (has some downtime)
- decrease FSx Volume size with AWS DataSync and separate, smaller FSx instance
- FSx for Lustre can lazy load S3 files

## AWS DataSync

- synchronize data (large data to and from places)
  - includes on-premise and other cloud providers
    - need appropriate protocol, e.g., NFS
    - these would need an appropriate client
- replication tasks are NOT continuous, are scheduled
- file permissions and file metadata are PRESERVED
- can setup bandwidth limits
- works for all S3 Storage Classes
- can work in the reverse direction
- AWS Snowcone if you have limited bandwidth

## AWS DataSync - Solution Architecture

- Move large amount of data to and from AWS, on-prem, other clouds
- Direct Connect Public VIF (Virtual Interface)???
- public vs private VIF options

## AWS Data Exchange

- third-party data available in the cloud
- AWS Data Exchange for Redshift works both directions
- AWS Data Exchange for APIs integrates with AWS auth

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

## AWS Storage Services Price Comparison

- should understand the cost rankings of things intuitively

## Quiz

- RAID (Rundant Array of Independant Disks)???
- EFS cross-region replication
- TODO continue, haven't finished all questions

## Study Group Practice Questions

- TODO

# Section 07 - Caching

## CloudFront - Part 1

- a Content Deliver Network (CDN)
- 225+ Point of Presence
- 13 Regional Edge Caches
- Origins include S3 and uses Origin Access Control (OAC)
- VPC Origin for to deliver traffic to private networks
- Custom Origin (HTTP)
  - API Gateway for greatest control
  - or just API Gateway Edge
  - S3 Bucket configure as a website
  - Why not HTTP-S though???
- S3 Cross Region Replication better for servicing only a few specific regions
- use customer header with secret between CloudFront and Custom Origin
- SGs for only whitelisting the CloudFront Edge IPs

## CloudFront - Part 2

- Lambda@Edge has access to headers like CloudFront-Viewer-Country
- Price Classes to cost control
- Signed URL to protect your content

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

## Lambda@Edge Reduce Latency

- architecture to route to a different origin and reduce latency

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

## Handling Extreme Rates

- architecture discussion
- ALB throughput limits only 10,000 RPS???
- SQS and SNS have unlimited throughput, essentially
- SQS FIFO has 3,000 RPS (with batching)
  - 300 RPS without batching???
- Kinesis is 1 MB/s in, 2 MB/s out PER SHARD
- S3 prefix throughputs limited by KMS if data is encrypted
- caching is a key cost reduction strategy!!!
- this is one of the best architecture slides in the course!!!

## Section Quiz

- how would removing the host header break SSL???
  - clearly would help cache hits
- why need signed URLs in addition to VPC Origin???
  - wouldn't AOC control access?
- CloudFront has cache invalidation functionality
- Origin Groups are just for failover, not meant for latency or load balancing

## Study Group Practice Questions

- TODO this entire section should be moved into the service communication section
- common pattern is to use queues to make a service async and therefore reduce load on DBs
  - you read the queue as fast or slow as you'd like

# Section 08 - Databases

## DynamoDB

- NoSQL and fully managed
- Similar to Apache Cassandra
- max object size is 400KB
- provisioned vs on-demand capacity
- eventual or strong consistency for READS
- transactions across multiple tables (ACID)
- PITR for backups
- standard and Infrequent Access (IA) tables classes
- primary key and attributes
- data types include
	- scalar
	- document
	- set
- sort key == range key
- object = parition key + optional sort key + attributes
- Local Secondary Index (LSI)
	- alternative sort key
	- must be defined at table creation time
- Global Secondary Index (GSI)
	- change the primary key and optional sort key
	- can be defined after table creation time
- TTL on rows
- DynamoDB Streams can be read by many services
	- 24 hour retention of data
- Global Tables
	- active-active replicaiton, many regions
	- requires having DynamoDB Streams enabled
	- good for low latency and disaster recovery
- send DynamoDB Streams to Kinesis Data Streams
	- if you want longer retention
	- you want to use other tools like Kinesis Data Firehouse
	- or Kinesis Data Analytics
	- etc.
- common pattern is to index S3 objects using DynamoDB and S3 Events
- DynamoDB Accelerator (DAX)
	- cache for DynamoDB
	- 5 minute TTL by default
	- up to 10 nodes in cluster
	- Multi AZ (at least 3 nodes recommended for production)
	- has encryption at rest
- DAX vs ElastiCache
	- if you're directly accessing DynamoDB, use DAX
	- if you do any computation with the DynamoDB results, use ElastiCache 

## Amazon OpenSearch (ElasticSearch)

- Kibana is now OpenSearch Dashboards
- two modes
	- managed cluster
	- serverless cluster
- OpenSearch Dashboards is more advanced than CloudWatch dashboards
	- Logstash Agent instead of CloudWatch Logs agent
	- you decide on retention and granularity of logs
- note for architectures you can often replace Lambda with Kinesis Streams or Kinesis Firehose

## Amazon Relational Database Service (RDS)

- managed provisioning, backups, patching, and monitoring or various database engines
- run within a VPC, control with Security Groups
- can expand the EBS storage with auto-scaling
- automated PITR, but backups expire
- manual snapshots, set retention time
	- can also move across regions
- management or outage notifications via SNS
- Multi-AZ standby instances for failover
	- application never accesses the standby instance (one DNS name)
- Read Replicas for throughput, eventual consistency, and cross-region
- use Route53 for distributing reads across replicas
	- can leverage health checks
- in-flight and at rest encryption (SSL for in-flight)
- authentication via IAM
	- for MariaDB, MySQL, and PostgreSQL
	- what about for other database engines???
	- obtain token via RDS API calls
	- network in/out is therefore always encrypted using SSL
	- EC2 Instance Profiles make this integration easy???
- authorization still is within RDS
- can copy un-encrypted snapshot into encrypted one
- CloudTrail CANNOT track queries made within RDS
- Oracle
	- RDS Backups for backup and restore of Amazon RDS for Oracle
	- Oracle Recover Manager (RMAN) for backup, but restore only NON- Amazon RDS for Oracle
	- Real Application Clusters (RAC) NOT SUPPORTED by RDS
		- must use EC2 for full control
	- use Transparent Data Encryption (TDE) for encryption at rest
	- Database Migration Service (DMS) works on Oracle RDS
- RDS for MySQL
	- use "mysqldump" to migrate from RDS to non-RDS instance
- RDS Proxy for AWS Lambda
	- avoid "TooManyConnections" exceptions
	- manages connection pools and cleaning up connections
	- requires either
		- public proxy and public lambda
		- private proxy and lambda in VPC

## Aurora - Part 1

- PostgreSQL and MySQL are compatible
- storage grows by 10GB increments all the way to 128TB
- 6 copies of data, across three AZs
- up to 15 read replicas available via endpoints
- replication across regions is ENTIRE database
	- NOT just certain tables like DynamoDB
- load or offload data directly from / to S3
	- this saves network and resource costs
- self-healing with peer-to-peer replication
- backup, smapshots, and restore features
- storage striped across 100s of volumes
- failover of master in less than 30 seconds
- support for cross-region replication
- Aurora DB Cluster
	- Writer Endpoint
	- Reader Endpoint (load balancing)
- Aurora Endpoints (host address + port)
	- Cluster Endpoint (Writer Endpoint)
	- Reader Endpoint (load balancing)
	- Custom Endpoint (a set of particular DB instances you configure)
		- different DB parameter group???
	- Instance Endpoint (a particular DB instance)
- Aurora Logs (just for MySQL???)
	- can either download them or publish them to CloudWatch Logs
- Performance Insights tool to troubleshoot
- CloudWatch Metrics for basic hardware usage statistics
- Enhanced Monitoring Metrics for host level, process view, per-second metric
- Slow Query logs also available

## Aurora - Part 2

- Aurora Serverless
	- as usual, good for infrequent, intermittent or unpredictable workloads
	- pay per second, can be more cost-effective
	- Data API for HTTPS endpoints to run SQL statements
		- leverages Secrets Manager for database credentials
		- need access to both the Data API and the underlying secret
	- are the following points still only related to Aurora Serverless???
	- RDS Proxy can be used in front of Aurora primary instance for R+W
	- RDS Proxy can be used in front of Read Replica instances for reading
	- Aurora Global Aurora
		- Cross-Region Read Replicas
		- Aurora Global Database (recommended)
			- 1 primary region for r+w
			- up to 5 read-only replication regions (less than 1 second replication lag)
			- up to 16 read replicas within each secondary region
			- RTO less than 1 minute for disaster recovery to secondary region
			- can manage RPO of Aurora for PostgreSQL
			- Write Forwarding lets secondary regions forward SQL commands to the primary
				- mostly helps with having to manage a bunch of different endpoints
		- convert RDS to Aurora via snapshot and restore
		- convert RDS to Aurora via Aurora Read Replica on an RDS DB instance 
			- promote to Aurora when replication lag is very low

## Database Section Quiz 

- Kinesis Data Firehose cannot be a subscriber of DynamoDB Streams
- Aurora has a 128TB limit
- Route53 CANNOT check the health of an RDS database

# Section 09 - Service Communication

## Step Functions

- don't need to know in depth, just the capabilities and where it fits in your architecture
- flow represented by JSON sate machine
- features
    - sequence
    - parrallel
    - conditions
    - timeouts
    - error handling
- maximum execution time of one year!!!
- human approval feature
- note the extra latency between step function and lambda communication
- optimized integrations
    - Lambda
    - AWS Batch
    - DynamoDB
    - EMR
    - other Step Functions
    - many others
- AWS SDK Integrations
    - pretty standard, 200+ AWS services available
- many example workflows available in the AWS docs
    - e.g., coordinate all the steps of training a ML model with SageMaker, S3, etc.
- Step Functions Tasks
    - Lambda Tasks
    - Activitiy Tasks (must use polling, is not serverless)
    - Service Tasks (connect to supported AWS service)
    - Wait Tasks (set duration or until timestamp)
- Step Functions do NOT integrate natively with AWS Mechanical Turk!!!
    - SWF is preferred over Step Functions for this???
- Standard Workflows vs Express Workflows
    - Express can kickoff many more executions per second
    - Express has shorter maximum duration
    - Express is at-least-once execution (instead of exactly-once)
    - Express priced similar to Lambdas (instead of per state transition)
- Express Workflow Synchronous vs Asynchronous
- can use error handling, retries, and alerting with State Machines
    - integrates with EventBridge, SNS, etc. for notifying about failures
- remember, steps like reading a DDB table can be done natively without a Lambda function

## SQS

- serverless, managed queue with IAM integration
- decouples services so they can scale independently
- max message size of 256KB!!! use S3 pointer!!!
- common to use SQS as a write buffer for DynamoDB
- SQS FIFO has 300 messages per second standard or 3000 mps with batching
- Dead Letter Queue (DLQ)
    - fail to process in Visibility Timeout, message goes back to queue
    - if MaximumReceives threshold exceeded, send message to DLQ
    - DLQ must be same FIFO or Non-FIFO type as source queue
    - can debug, then redrive the DLQ without any custom code
- consumers need to be idempotent since events can be delivered multiple times
- Event Source Mapping to connect a Lambda to SQS queue
    - specify batch size 1-10
    - queue visibility timeout should be 6x the timeout of your Lambda Function
    - DLQ should be attached to SQS Queue, not the Lambda
        - Lambdas can have DLQs for their async invocations
    - could also use Lambda destination for failures
- request / response queue solution architecture (just an example)
    - gives decoupled scaling
    - fault tolerance
    - load balancing

## Amazon MQ

- SQS / SNS are cloud-native services
- traditional on premise applications use open protocols like MQTT, AMQP, Openwire, etc.
- Amazon MQ is a managed message broker service for Rabbit MQ and ActiveMQ
    - doesn't scale as much as SQS / SNS
    - runs on servers, which you can run in Multi-AZ with failover
    - has both queue (SQS) and topic (SNS) features on each server
- can migrate these current services to Amazon MQ
    - IBM MQ
    - TIBCO EMS
    - Rabbit MQ
    - ActiveMQ

## SNS

- send one message to many receivers (pub / sub)
- "event producer" sends messages to SNS topic
- "event receivers" subscribe to SNS topic
- each subscriber will get all of topic's messages
    - there is now functionality to filter these messages
- up to 12,500,000 million subscription per topic
- up to 100,000 topics
- can integrate with many kinds of subscribers
    - emails
    - SMS
    - HTTP(S) endpoints
    - AWS services (e.g., SQS, Lambda, Kinesis Data Firehose)
- can integrate with many kinds of publishers
    - from a ton of AWS services and features (e.g., Auto Scaling Groups)
- how to publish
    - Topic Publish (via SDK)
    - Direct Publish (mobile apps SDK???)
        - platform applications and endpoints???
        - Google GCM, Apple APNS, Amazon ADM???
- encryption in flight with HTTPS API
- encrytion at rest using KMS keys
- client-side encryption also possible
- access control via IAM policies and SNS API
- SNS Access Policies (similar to S3 Bucket Policies)
    - useful for cross-account access to SNS topics
    - useful for other servies (e.g., S3) to write to an SNS topic

## Amazon SNS and Amazon SQS Fan Out Pattern

- pattern to send messages to multiple SQS queues
- push once to SNS topic, and subscibe many queues to that SNS topic
- benefits
    - fully decoupled
    - SQS gives
        - data persistence
        - delayed processing
        - retries
    - add more subscribers over time
- SQS queue access policy must allow SNS to write
- can deliver messages to cross-region queues
- SNS can also publish to Kinesis Data Firehose (KDF)
    - therefore, can send to any KDF supported destinations (e.g., S3)
- can also use SNS FIFO topics
    - same throughput limit as SQS FIFO
    - subscribers can be SQS Standard or SQS FIFO queues!!!
    - deduplication via Diduplication ID or Content Based Deduplication
- SNS Message Filter
    - JSON policy to filter messages sent to SNS topic's subscriptions
    - if omitted, all messages recieved by subscriber

## SNS Message Delivery Retries

- when SNS tries to send a message, and the destination has a server error
- delivery protocols and total attempts are key metrics
- backoff phases
    - immediate retry phase
    - pre-backoff phase
    - backoff phase
    - post-backoff phase
- AWS managed endpoints 
    - try 100,015 times over 23 days
- customer managed endpoints
    - SMTP protocol
    - try 50 times in 6 hours
- HTTP/S endpoints support custom retry policies
    - e.g., your backend does not like heavy load from retries
    - backoffFunction
    - sicklyRetryPolicy
- SNS Dead Letter Queues (DLQ)
    - after delivery policy is exhausted, discard message unless DLQ is configured
    - DLQ is configured on a per subscription basis, NOT a per topic basis
    - must use SQS FIFO for SNS FIFO???

## Service Communication Section Quiz

- Amazon Simple Workflow Service (SWF) Activity Workers are direct targets for Step Functions???
    - likely need to check the AWS Console UI
- Kinesis Data Streams is a better choice than SQS FIFO for high TPS
    - how does it preserve ordering???
- what are the alternatives to lift-and-shift migrations???

# Section 10 - Data Engineering

## Amazon Kinesis Data Streams

- keyword "real-time" data
- RT data --> producers --> amazon kinesis data streams --> consumers
  - Apache Flink???
- data must expire, cannot be deleted
- provisioned and on-demand mode
  - on-demand scales based on 30-day peak???

## Amazon Kinesis Data Firehouse

- store data into target destinations
- batch writes for efficiency
  - "near real-time"
- need to remember specifically
  - Redshift
  - S3
  - OpenSearch
  - Splunk
- automatic scaling (unlike Kinesis Data Streams)
- Lambda can be used for arbitrary transformations
- ORC data conversion is only for S3
  - possibly parquet as well???
- compression support to S3 and Redshift (GZIP)
- Spark and Kinesis Client Library (KCL) do NOT read from Kinesis Data Firehose (KDF)
  - only from Kinesis Data Streams (KDS)
- "blueprint" transformation lambdas
- S3 + copy command used to go to Amazon Redshift
- source records and transformation failures, and delivery failures can be written to an S3 bucket
  - no data loss is the key
- 1 minute minimum for buffer timeout
- KDF vs KDS
  - enhanced fan-out for stream latency???

## Amazon Managed Service for Apache Flink

- formerly Kinesis Data Analytics for Apache Flink
- Flink is a framework for processing data streams
- does NOT read from KDF, only KDS

## Streaming Architectures

- can go from KDS to Amazon Kinesis Data Streams back to KDS???
- Kinesis Producer Library (KPL) and Kinesis Agent can produce directly to KDF
- cost analysis of KDS vs Dynamo for streaming data
- good comparison chart for streaming applications

## Amazon MSK

- Managed Streaming for Apache Kafka (MSK)
- alternative to Amazon Kinesis
- manages the Kafka broker nodes and Zookeeper nodes for you
- MSK can have higher message sizes
- can only add partitions to topic (no scale down)???
- can keep MSK data for as long as you want to pay for EBS volumes

## AWS Batch

- run batch jobs as Docker images
- AWS Fargate OR EC2 + Spot Instances
- direct Amazon EventBridge integrations between S3 and AWS Batch
- managed compute environment - need NAT gateway / instance or VPC Endpoint for ECS
- unmanaged compute environment - deal with all instance configuriation, provisioning, scaling
- Multi Node Mode - good for HPC
  - should launch EC2 instances with placement group "cluster"
    - same server rack in same AZ
  - does NOT work with EC2 Spot Instances

## Amazon EMR

- Elastic MapReduce
- helps create Hadoop clusters to analyze and process big data
- used to migrate away from on-premise Hadoop clusters
- can use hundreds of EC2 instances
- EC2 + EBS with HDFS (temporary storage)
- EMRFS has native integration with S3 (permanent storage)
  - is EMRFS set at EC2 level or EBS level???
- everything launched in single AZ for performance (but you'll lose data)
- Apache Hive for reading from DynamoDB table???
  - Apache Hive is a data warehouse built on top of Hadoop for SQL-like analyzing
- node types and purchasing options
  - master and core nodes good candidates for reserved instances
- instance configurations, know the various options
  - Uniform Instance Groups
  - Instance Fleet (like Spot Fleets)
    - still no autoscaling???

## Running Jobs on AWS

- probably never vouch for EC2 + cron for batch jobs
- understand the differences in each choice discussed

## AWS Glue

- managed extract, transform, and load (ETL) service
- Glue Data Catalog
  - collects metadata about data sources
  - done using AWS Glue Data Crawler
  - other AWS sources rely on this catalog
    - Athena, Redshift Spectrum, EMR

## Redshift

- analytics data warehousing
- based on Postgres, but not for Online Transaction Processing (OLTP)
- Online Analytical Processing (OLAP)
- Massively Parallel Query execution (MPP)
- integrates with tools like AWS Quicksight and Tableau
- Database Migration Service (DMS) and other data loading options
- only certain clusters have multi-AZ options
- leader vs compute node
- Redshift Enhanced VPC Routing for reduced costs???
- Athena is better if queries are sporadic and you don't want to provision resources
- snapshots are incremental
- CANNOT restore snapshots into an old cluster
- snapshots work similarly to RDS
- can automate copy of snapshots to different regions
- "Redshift snapshot copy grant" for different KMS keys in different regions
- Redshift Spectrum - query S3 data that is not loaded into Redshift
  - must have Redshift cluster available to start the query
  - does Redshift Spectrum manage all of its own nodes???
- Redshift Workload Management (WLM) - queues for managing query priorities
  - automatic WLM vs manual WLM
- Concurrency Scaling Cluster for increased requests
  - WLM can control which queries go to this cluster

## Amazon DocumentDB

- the MongoDB (NoSQL) version of AWS Aurora
- pay for what you use, no upfront cost
- you pay for...
  - on-demand instances per second
  - database I/O per million I/Os
  - database storage per GB/month
  - backup storage per GB/month
- DocumentDB is all provisioned???
  - there is no on-demand tier, but uses on-demand instances???
  - this is very similar to Aurora???

## Amazon Timestream

- managed, serverless time series database
- IoT, operational apps, real-time analytics, etc.
- integrates with AWS IoT and other services
  - Prometheus for system monitoring and alerting
  - Telegraf agent for collecting metrics, logs, aggregations, data, etc.
- goes into Amazon SageMaker, Grafana, any JDBC connection

## Amazon Athena

- serverless query service for S3 data
  - built on Presto and standard SQL language
- Presto = distributed SQL query engine designed for fast, interactive querying of large datasets from various sources
- can be good for VPC Flow Logs, ELB Logs, CloudTrail trails, etc.
- columnar data helps cost by reducing scans
  - parquet or ORC data formats
  - possibly use AWS Glue for transformations
- compress (reduce retrievals) and partition datasets (reduce scans)
- big files (>128 MB) to minimize overhead
- Federated Query can be run using Data Source Connectors
  - HBase in EMR???
  - results written back to S3

## Amazon Quicksight

- serverless machine learning business intelligence (BI) service
  - creates dashboards and visualizations
- per session pricing???
- integrates with many data stores
- use SPICE engine for in-memory computation
  - must import your data into Quicksight for this to work
  - e.g., CSV or JSON files
- column-level security (CLS) in enterprise version
- 3rd-party SaaS integrations like Jira or SalesForce
  - 3rd-party databases as well, or anything with JDBC
- has its own concepts of Users and Groups
  - use to share dashboards
  - dashboards are different than analyses???
  - dashboards are read-only snapshots???

## Big Data Architecture

- from real-time to reporting use cases
- out-of-the-box queries for many services (cost and billing)

## Quiz 9: Data Engineering Quiz

- KPL can write to KDF directly
- S3 events cannot be directly sent to AWS Batch
- think AWS Batch if you hear containers and coupled workloads
- EMR and Hive have a direct connection to DynamoDB
- EMR can be used to run frameworks such as Spark, Hive, or Presto
- AWS Neptune is a managed, serverless graph database

# Section 11 - Monitoring

## CloudWatch

- CloudWatch Metrics
  - EC2 Detailed Monitoring bumps CW Metrics from 5 mins to 1 min
  - EC2 RAM is NOT a built-in metric
- CloudWatch Alarms
  - can be intercepted by EventBridge (powerful)
  - can trigger actions like EC2 terminate, auto-scaling, or SNS
- CloudWatch Dashboards
  - can display both metrics and alarms
  - can display metrics of multiple regions
- CloudWatch Synthetics Canary
  - scripts that monitor your services by acting like users
  - screenshots of UIs, API calls, real workflows
  - checks more than just if a service is responsive
  - can trigger CloudWatch Alarms
  - written in NodeJS or Python
  - headless browser
  - "Blueprints"???
  - probably based on Selenium or Puppeteer???

## AWS CloudWatch Logs

- can publish data via SDK, CloudWatch Logs Agent and CloudWatch Unified Agent
- could also integrate with AWS services like...
  - Elastic Beanstalk
  - ECS
  - Lambda
  - VPC Flow Logs (VPC specific logs)???
  - API Gateway
  - CloudTrail based on filter???
  - CloudWatch log agents, e.g., on EC2 or on-premise servers
    - CloudWatch Logs agent (deprecated)
    - Unified CloudWatch Agent (recommended)
  - Route 53 DNS queries
- Log Groups and Log Streams relatively arbitrary
- Metric Filters to trigger Alarms
- Logs Insights used to query logs and add them to dashboards
- S3 Export is NOT real-time (CreateExportTask)
- CloudWatch Logs Subscriptions (Subscription Filters)
  - sends data in real-time if managed Lambda
  - sends data in near real-time if KDF
  - could also directly interact via KDS or custom Lambdas
  - destinations supported by Subscription Filter???
- central logging account is a very common architecture
- tight integration between CW Agent and System Manager
  - SSM State Manager???
  - SSM Run Command???
  - SSM Parameter Store???

## Amazon EventBridge (formerly CloudWatch Events)

- many sources
- can use cron scheduling
- CloudTrail could intercept ANY API call
- produces JSON and sends that to destinations
- many destinations
- Default Event Bus vs Partner Event Buses
  - mostly SaaS companies
  - you can listen to these buses
- can create your own Custom Event Buses
- Resource-based Policies for cross-account access
- can archive and replay events
- Schema Registry can infer your bus's data's schema and do code generation
- Resource-based Policy specifically for each Event Bus
  - could use to aggregate all events from your AWS Organization in a single AWS account

## AWS X-Ray

- visual analysis of your applications and tracing
  - primarily for microservices and distributed systems
- many integrations
- can use the X-Ray agent for EC2, ECS, and others???
- ECS could also use the Docker container???
- Beanstalk has agent automaticallly installed
- X-Ray agent, or services that use X-Ray, need IAM permissions to talk to X-Ray

## AWS Personal Health Dashboard (PHD)

- global service
- shows how AWS outages directly impact you
- key word is "maintenance" - shows all maintenance events from AWS
- accessible through the AWS Health API
- aggregate across multiple accounts with AWS Organizations
- can react to AWS Health events for your AWS account via EventBridge
  - CANNOT be used to intercept public events from AWS Service Health Dashboard
    - use the RSS feed???
- good (and rare) demo given

## Section Quiz

- pretty straight forward

## Study Group Practice Questions

- AWS Batch and AWS Step Function interactions (does Batch use Step Functions under the hood)???
- Hadoop vs Hive vs Spark vs Glue vs EMR???
- MongoDB Atlas on AWS??? Why not Aurora with MongoDB or DocumentDB???
  - is Aurora just for relational databases???
  - is Aurora a sub-feature of AWS RDS???
- FSx does NOT need a new instance created to increase capacity, but what from the storage section did???
- need to review very tough question about AWS Systems Manager Automation for CVE scans???
- what data sources can Quicksight connect to???
  - is S3 acceptable, or do you need combination with Athena???
- Quicksight is definitely not near-real time or real time speed

# Section 12 - Deployment and Instance Management

## Elastic Beanstalk

- good for re-platforming on premise to cloud
- developer-oriented view of deploying an application
- supports the main platforms (e.g., Java with Tomcat)
- single or multi-container docker configuration
- managed service
- three architecture models
  - single instance (development)
  - high-availability with load balancer
  - worker tier
- web server vs worker environment
  - decoupling application into two tiers
  - cron.yaml for periodic tasks
- blue / green deployments (zero downtime)
  - Route53 + entirely new "stage" environment for v2

## AWS CodeDeploy

- deploy applications to EC2 and other AWS Services
- native integration with AWS services is nice
  - main reason to choose CodeDeploy over open source tools
  - e.g., Terraform
- CodeDeploy to EC2
  - they run the CodeDeploy agent
  - appspec.yml + deployment strategy
  - hooks for verification
- CodeDeploy to ASG
  - in place updates
  - blue / green deployments
    - must be using ELB
- CodeDeploy to Lambda
  - traffic shifting feature
  - before and after traffic shifting hooks
    - they themselves are lambda functions
  - leverages Lambda Aliases
  - SAM framework natively uses CodeDeploy
  - easy + automated rollback using CW Alarms
- Codedeploy to ECS
  - setup done using ECS service definition
  - supports canary deployment (Canary10Percent5Minutes)

## CloudFormation

- Infrastructure as Code (IaC)
- backbone of Service Catalog service (and many others)
- DeletionPolicy to retain data
  - Retain, Snapshot, or Delete (Default, except for AWS::RDS::DBCluster)
- custom resources via Lambda
  - AWS resource not yet supported
  - on premise resource
  - emptying S3 bucket before being deleted
  - fetch an AMI id
  - anything you want!
- StackSets - updates stacks across multiple accounts and regions
  - Administator and Trusted accounts
  - Automatic Deployment for AWS Organization or OUs
- CloudFormation Drift for detecting manual configuration changes
- Secrets Manager integrations and automatic password rotation for RDS
- resource importing is possible via templates, deletion policies, and unique identifiers for each target
  - CANNOT IMPORT RESOURCE INTO MULTIPLE STACKS

## AWS Service Catalog

- create stacks that are compliant and inline with the rest of the organization
  - launch via pre-defined cloudformation templates
  - self-service
- admin tasks: product --> portfolio --> control
- user tasks: product list --> (launch) --> provisioned products
- create and manage IT services on AWS
- all the deployed services are centrally managed
- helps with governance, comppliance, and consistency
- user does NOT need deep knowledge of AWS to launch products
- integrates with self-service portals such as ServiceNow

## AWS SAM (Serverless Application Model)

- framework for developing and deploying serverless applications
- all configuration in YAML
- can help you run things LOCALLY
- can use CodeDeploy to deploy Lambdas
- uses CloudFormation to work
- CICD Architecture for SAM
  - CodePipeline
  - CodeCommit
  - CodeBuild
  - CloudFormation + SAM (different than pure CloudFormation)???
  - CodeDeploy

## AWS CDK (Cloud Development Kit)

- define cloud infrastructure in a familiar language
  - gets compiled into CloudFormation templates (JSON/YAML)
- infrastructure and application code can exist together

## AWS Systems Manager (SSM) Overview

- manage EC2 and on-premise systems at scale
- SSM agent talks to Systems Manager
  - installed by default into Linux (and some Ubuntu) AMI
  - need proper IAM roles for SSM actions
- resource groups -> execute a document -> rate control / error control
- no need for SSH (because of agent)
- integrate with ASG Lifecycle Hook (Terminating:Wait)
- steps for Patch Manager
  - Patch Baseline
  - Patch Groups (could be tag-based)
  - Maintenance Windows
  - AWS-RunPatchBaseline Run Command (cross-platform)
  - Rate Control (concurrency and error)
  - Patch Compliance using SSM Inventory
- Systems Manager Session Manager
  - start secure shell on EC2 or on-premise server without SSH keys
  - works through the SSM Agent
  - cross-platform
  - CloudWatch Logs and CloudTrail monitoring
    - intercept StartSession events
- Systems Manager OpsCenter
  - OpsItems
  - aggregates useful debugging / remediation info
  - ex: EventBridge or SSM Automation to create OpsItems

## AWS Cloud Map

- fully managed resource discovery service
  - decouples services by giving them a directory to find each other through
- integrates with health checks
- can integrate with DNS
- make version changes through UI rather than via code changes

## Section Quiz

- Route53 cannot create records for Lambda functions (they're not accessible directly through HTTP)
- Pre and Post Traffic hooks for CodeDeploy???
- should review a demo of Systems Manager and all its features???

# Section 13 - Cost Control

## Cost Allocation Tags

- Tags can track related resources
  - Cost Allocation Tags are similar, but appear in Reports
- AWS Generated Cost Allocation Tags (prefix aws:)
  - they are NOT applied to resources retroactively once you've enabled tagging???
- User tags (prefix user:)
  - you need a tagging strategy

## AWS Tag Editor

- manage tags of multiple resources at once
- search tagged or untagged resources across all AWS regions

## Trusted Advisor

- analyze your AWS accounts and provide recommendations
  - cost optimization
  - service limits
  - operational excellence
  - and others
- Core Checks and recommendations for all customers
- can enable weekly emails
- Full Trusted Adivsor for Business and Enterprise support plans
- AWS Support Plans
  - Basic Support
  - Developer
  - Business
  - Enterprise
- Business and Enterprise get full checks and AWS Support API access
- can check if S3 bucket itself is public, but NOT public objects within
  - EventBridge / S3 Events / AWS Config Rules alternative
- service limits are READ ONLY in Trusted Advisor
  - AWS Support Centre or AWS Service Quotas alternative

## AWS Service Quotas

- notify if you're close to a service quota value threshold
  - e.g., concurrent lambda executions

## EC2 Launch Types & Savings Plan

- breakdown of best use cases for each EC2 Instance Launch Type
- AWS Savings Plan is a new pricing model for long-term usage discounts
  - e.g., $10 / hour for 3 years
- savings plans
  - EC2 Instance Savings (same as Standard Reserved Instances)
  - Compute Savings (same as Convertible Reserved Instances)
  - SageMaker Savings
- should better understand how the legacy / modern approaches differ???

## S3 Cost Savings

- another summary of S3 Storage Classes and their best use cases
- can move objects manually or through S3 Lifecycle configurations
- other savings options
  - S3 Lifecycle Rules
  - compress objects to save space
  - S3 Requester Pays (typically, the owner of the bucket pays for everything)
    - owner STILL PAYS for storage, but not the request or the data transfer
    - e.g., share dataset across a lot of accounts
    - do not create an IAM role to assume, or you will end up paying still!!!

## S3 Storage Classes - Reminder

- yet another summary of the S3 Storage Classes
- durability and availability
  - durability same for all classes
  - availability is different for all classes
- S3 Intelligent-Tiering
  - no retrieval charges for this
  - monthly monitoring and auto-tiering fee
  - tiers are slightly different than the S3 Storage Classes???
- should understand the tables that break down features and costs

## AWS Budgets & Cost Explorer

- AWS Budgets
  - create budgets and send alarms when cost exceed budget
  - budget types
    - Usage
    - Cost
    - Reservation
    - Savings Plans
  - up to 5 SNS notifications per budget
  - can filter by Linked Account and Purchase Option???
    - filter options are the same as AWS Cost Explorer
  - 2 budgets are free
  - Budget Actions
    - three types
      - apply IAM Policy
      - apply Service Control Policy to an OU
      - stop EC2 or RDS instances
    - can require a workflow approval process
  - Centalized Budget Management
    - Central Account uses budget with account as a filter
    - move the Member Account into a more restrictive OU
  - OR Decentralized Budget Management
    - budget in each Member Account
    - deploy the budgets to accounts using CloudFormation StackSet
      - could be deployed from the Management Account
- AWS Cost Explorer
  - visualize, understand, and manage AWS costs and usage over time
  - usage across all accounts
  - choose optimal Savings Plan
  - forecast up to 12 months usage in advance

## AWS Compute Optimizer

- reduce cost and improve performance with better AWS resources for your workloads
- uses machine learning to rightsize things based on configurations and CloudWatch Metrics (utilization)
- export results to S3
- use the CloudWatch Agent for Memory Utilization agents
  - not needed for other metrics like CPU or network traffic

## EC2 Reserved Instance

- can be shared in an AWS Organization
- can turn off sharing, but this needs to be done by the Management Account
- you can queue your Reserved Instances purchase for the datetime that the current one expires

## Quiz 12 Cost Control

- AWS Support API cannot be used to increase service limits (must make manual request)

# Section 14 - Migration

## Cloud Migration Strategies - The 7 R's

- blog post on AWS about the 7 R's
- concepts and diagram are important to read and understand!!!
- Retire (turn things off)
- Retain (no migration)
- Relocate (move from on-prem to cloud, or EC2 to a new account)
- Rehost (lift and shift, no change to application setups)
  - example: using AWS Application Migration Service
- Replatform (lift and reshape, get some Cloud optimizations)
  - example: RDS doesn't change application, but gives you automated backups
- Repurchase (drop and shop, quick to move to SaaS)
  - example: CRM to Salesforce
- Refactor / Re-architect (re-design application, most effort, most payoff)
  - example: move to a serverless architecture, use S3

## Storage Gateway

- hybrid cloud is useful or required for various reasons
- AWS Storage Gateway gives on-premise infra access to cloud native storage
  - example: block, file, and object storage
- bidirectional (access your on-premise data as well)
- types of Storage Gateways
  - S3 File Gateway
  - FSx File Gateway
  - Volume Gateway
  - Tape Gateway
- S3 File Gateway
  - no glacier tiering
  - interact with S3 like a normal file share
  - NFS and SMB protocols
  - caching for most recently used file in the gateway
  - SMB protocol is more for Windows, so has Active Directory (AD) integration
- FSx File Gateway
  - already accessible for your on-premise machines
  - only benefit is the local cache in the gateway in your data center
  - Windows native compatibility
  - useful for group file shares and home directories
- Volume Gateway
  - block storage using iSCSI protocol backed by S3???
  - can help restore on-premise volumes???
  - Cached and Stored volumes
  - need to understand better!!!
- Tape Gateway
  - Virtual Tape Library (VTL) backed by S3
  - iSCSI protocol
  - the company is responsible for using the physical tapes / media changers
  - works with leading backup vendors
- company would typical run these gateways on one of its servers
  - alternative is the Storage Gateway Hardware Appliance
  - has all the needed resources to function correctly as any of the gateway types
- good architecture diagram to conclude section

## Storage Gateway - Advanced Concepts

- File Gateway: Extensions
  - could use File Gateway for an EC2 instance in a VPC to facilitate cloud migration
  - combine with S3 Events to get benefits of the cloud and serverless architectures
- File Gateway: Read Only Replicas
  - different on-premise data centers can quickly read data with low latency
- File Gateway: Backup and Lifecycle Policies
  - get benefits of moving S3 objects to infrequent access tiers to get file system cost savings
- File Architecture: Other possibilities
  - S3 object versioning to restore a file or entire file systems to specific version
    - use the "RefreshCache" API on the Gateway to be notified of restore
  - S3 Object Lock for Write Once Read Many (WORM) data
    - clients' new versions do not affect previous versions

## Snow Family

- AWS Snowball is a highly-secure, portable device to collect and process data at the edge and migrate data into and out of AWS
  - Snowball Edge Storage Optimized
  - Snowball Edge Compute Optimized
- helpful for migrating petabytes of data
- receive the machine, load it, ship it back to AWS for import
- edge computing case is for when there's limited internet or no access to computing power
  - run EC2 instances or Lambda functions at the edge

## Snow Family - Improving Performance

- multiple tips for improving the upload speed of data to the Snowball device
- Amazon S3 Adapter for Snowball???

## AWS Database Migration Service (DMS)

- resilient and self-healing database migration
- source database remains available during the migration
- hetergenous migrations
- Continuous Data Replication using CDC???
- an EC2 instance is required to perform the tasks
- many sources and targets
  - note that Redshift, Kinesis Data Streams, and OpenSearch are targets but NOT sources
- AWS Schema Conversion Tool (SCT)
  - for converting schemas between different database engines
  - works alongside DMS on the EC2 instance
  - not needed if source and target engine are the same
  - for OLTP and OLAP
- various useful and specific points on the "Good things to know" slide
- can combine Snowball and DMS for very large volumes of data
  - speed of Snowball and CDC of DMS

## AWS Cloud Adoption Readiness Tool (CARD)

- tool to help an organization to plan its cloud adoption and migrations
- answer questions across six perspectives
  - business
  - people
  - process
  - platform
  - operations
  - security
- generates custom report on your level of migration readiness

## Disaster Recovery

- whitepaper on disaster recovery that you should read
  - these slides cover the majority of the whitepaper content
- disaster = any event that has a negative impact on a company's business continuity or finances
- Recovery Point Objective (RPO)
  - "how often you run backups"
  - data loss you will accept
- Recovery Time Objective (RTO)
  - "amount of downtime your application will have"
- recovery strategies (faster RTO going down)
  - Backup and Restore
  - Pilot Light
  - Warm Standby
  - Hot Sight / Multi Site Approach
- Backup and Restore
  - high RPO
- Pilot Light
  - always a small version of the app running in the cloud
  - ex: an RDS database getting continious data replication
- Warm Standby
  - full system up and running, but at minimum size
  - scale upon disaster
- Multi Site / Hot Site Approach
  - very low RTO (minutes or seconds)
  - very expensive
  - active-active setup with hybrid cloud
- AWS Multi Region
  - running active-active systems in multiple regions
- disaster recovery tips
  - automated backups
  - use Route53 to migrate DNS over from Region to Region
  - Site ot Site VPN as recovery from Direct Connect???
  - replication from many services
  - CloudFormation and Elastic Beanstalk to recreate environments
  - CloudWatch Alarms and Lambda for customized automations
  - chaos testing (Netflix "simian-army" randomly terminating EC2 instances)

## AWS Fault Injection Simulator (FIS)

- run fault injection experiments on AWS workloads
- based on chaos engineering
- ex: sudden increase in CPU or memory
- find performance bottlenecks or bugs
- Experiment Template -> Stop Experiment -> view results

## VM Migrations Services

- AWS Application Discovery Services
  - Agentless discovery (Application Discovery Agentless Connector)
    - OS agnostic, Open Virtual Appliance (OVA) package for VMware host
  - Agent-based discovery
    - find mappings between services and more detailed info
  - Migration Hub Data Exploration
    - use Athena to analyze data collected from on-premise servers during discovery
    - add extra data sources like Configuration Management Database (CMDB) exports
- AWS Application Migration Service (MGN)
  - replaces "CloudEndure Migration" and AWS Server Migration Service (SMS)
  - for Lift-and-shift (rehost)
  - on-premise our other cloud providers' servers
  - AWS Replication Agent to achieve this
- AWS Elastic Disaster Recovery (DRS)
  - used to be called "CloudEndure Disaster Recovery"
  - recover your on-premise or cloud-based servers
  - also uses AWS Replication Agent
  - has failover and failback functionality
- can use Amazon Linux 2 AMI as a VM (.iso format)
- don't forget about AWS Database Migration Service (DMS)

## AWS Migration Evaluator

- build a data-driven business case for migration to AWS
- install Agentless Collector to conduct broad-based discovery
- analyze current state, define target state, develop migration plan

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

## Section 14 quiz

- replatforming means you maintain the same API
- Storage Gateway Tape Gateway requires you to recover entire tape if you need a file
- 200 Mbps is considered network limited (Snowball is faster)
- two-way forest trust is for AD, not for ElasticSearch???
  - ElasticSearch on-premise -> S3 -> Amazon OpenSearch
- AWS SCT is completely separate from AWS DMS???

# Section 15 - VPC

## VPC - Basics

- need to review VPC basics from the associate level solution architect exam???
- CIDR block of IP addresses
  - exact format / meaning of these???
- common (and only allowed) ranges of IPs in private networks
- VPC vs Subnet vs Route Table
- first four and last one IP in subnets is reserved by AWS
- Internet Gateway (IGW) acts as NAT for instances that have public IPv4 or public IPv6
- Public Subnet = has a route table that sends everything (0.0.0.0/0) to an IGW
- NAT instances (EC2 deployed in public subnet)
  - needs Elastic IP
  - must disable Source/Destination Check (EC2 setting)!!!
- NAT Gateway - managed NAT solution, scales bandwidth automatically
  - deploy multiple NAT gateways across AZs for HA
  - would you ever deploy NAT Gateways across regions???
- Network ACL (NACL) - stateless firewall for all instances within a subnet
  - support allow and deny rules
  - stateless, so need to create inbound and outbound allow rules!!!
- Security Groups - stateful firewall applied at instance level
  - can reference other SGs in the same region
    - even with peered VPCs or cross-account (what would that look like)???
  - no deny rules!!!
- VPC Flow Logs
  - VPC, Subnet, or ENI-level
  - Elastic Network Interface (ENI) = virtual networking card attached to an EC2 instance
  - helpful to debug why internet traffic was denied
- Bastion Hosts = two-step SSH into private EC2 instances via public EC2 instance
  - no managed version of this
  - alternative is SSM Session Manager to avoid SSH entirely (better option)!!!
- can use IPv6 for VPC (pair with IGW, which also supports IPv6)
  - public subnet can route all IPv6 to IGW
  - private subnet needs Egress-Only Internet Gateway
  - cannot be reached via IPv6, but can reach out to IPv6
-

## VPC Peering

- connect two VPC privately using AWS' network
  - make them behave as if they're a single network
  - must not have overlapping CIDRs (IPv4)!!!
- NOT transitive
- you must update route tables for VPCs to properly work together
- across regions and AWS accounts
- longest prefix match for resolving routes
- where do route tables live??? in each VPC??? between them???
- no edge to edge routing possible
  - this includes NAT Gateway + IGW setup
  - why are both NAT Gateway and IGW needed together usually???
  - a solution will be explained in a later lecture

## Transit Gateway

- a way to understand your network topology as it gets complicated
- controls transitive peering between thousands of...
  - VPC
  - on-premise
- regional resource, but can work cross-region
  - via Transit Gateway peering
- share them across accounts with Resource Access Manager (RAM)
  - major use case for RAM!!!
- supports IP Multicast between your AWS services (only service that offers this)
  - access NAT Gateway, NLB, PrivateLink, and EFS of other VPCs
- need to understand the architecture diagram discussed???
- route tables can restrict transitive peering
  - comprehensive peering is the default??? seems off???
- integration with Direct Connect Gateway
- inter and intra region peering to create meshes
  - billed hourly for each peering attachment
  - only billed for data processing between regions

## VPC Endpoints

- allow you to connect to AWS Services using a private endpoint instead of www network
- VPC Endpoint Gateway (for S3 and DynamoDB)
  - VPC Endpoint Interface for all other AWS services
  - check DNS Setting Resolution in VPC or route tables!!!
  - cannot be extended out of the VPC to VPN, DX, TGW, or peeering!!!
- VPC Endpoint Interface (an Elastic Network Interface)
  - get a private endpoint interface hostname
  - public hostname of the AWS service then resolves to private endpoint interface hostname
  - CAN be accessed from DX and Site-to-Site VPN!!!
  - difference between VPC peering and Site-to-Site VPN???

## VPC Endpoint Policies

- JSON policies to control access to services
  - works in combination with IAM user policies or service-specific policies
  - can force their application by restricting traffic that does NOT come from the VPC
    - e.g., "aws:sourceVpce" condition (single VPC Endpoint)
    - e.g., "aws:sourceVpc" condition (NOT the VPC, but all VPC Endpoints within the VPC)!!!
- S3 bucket policies can only affect PUBLIC IP addresses
  - so, aws:SourceIp condition doesn't work on VPC Endpoints
- note all of the potential things blocking a private EC2 instance from accessing S3

## AWS PrivateLink (VPC Endpoint Services)

- most secure and scalable way to expose a service to 1000's of VPCs
  - no VPC peering, internet gateway, NAT, route tables, etc.
- NLBs for the service application and ENIs for the consumer application
- understand the PrivateLink for S3 with Direct Connect diagram???
- Direct Connect Public VIF vs Private VIF???
- last slide architecture doesn't require PrivateLink, just VPC Peering???

## AWS Site-to-Site (S2S) VPN

- AWS managed VPN
- needs...
  - VPN appliance with public IP for corporate data center
  - Virtual Private Gateway (VGW) setup in each VPC
  - setup Customer Gateway (CGW) to point to on-prem VPN appliance
- two VPN connections / tunnels created and encrypted with IPSec
- can pair with AWS Global Accelerator
- route propagation
  - still need to make sure there are no overlapping CIDRs???
  - Static vs Dynamic (BGP) Routing
  - BGP (eBGP when over internet)
  - Autonomous System Number (ASN) of CGW and VGW must be specified
- NAT Gateway DOES NOT allow traffic from S2S VPN to IGW / public internet
  - NAT Instance (self-managed) CAN access public internet
  - if going AWS -> corporate data center, NAT Gateway WOULD work
- AWS VPN CloudHub = connect up to 10 Customer Gateway from each Virtual Private Gateway (VGW)
  - remember: still going over public internet, just encrypted
- recommended to use DX Gateway to avoid creating separate VGWs for each VPC to the Customer Gateway
  - Shared Services VPC can use VPC peering to avoid need for multiple VGWs
  - another alternative to this approach is Transit Gateway

## AWS Client VPN

- connect from your computer to private network in AWS or on-premise
- uses OpenVPN
- uses private IP (of, e.g., an EC2 instance)
- single Client VPN ENI can be used with VPC peering or S2S VPN
  - note that this might mean your traffic goes through AWS to get to your on-premise network
- integrates with Internet Gateway or NAT Gateway so clients can access internet
  - don't client's use public internet for the initial Client VPN connection???
- also integrates with Transit Gateway

## Direct Connect

- provides dedicated PRIVATE connection from remote network to your VPC
- more expensive than VPN
- must use Direct Connect locations
- private access to AWS via Private VIF
- bypasses your ISP, reduces network costs, increases bandwidth and stability
- NOT redundant (would need a second DX created)
- VIF = Virtual Interface
  - Public VIF for anything AWS (e.g., EC2 service)
  - Private VIF connect to resources in VPC (e.g., EC2 instance)
- Transit Virtual Interface connects to resource in VPC via Transit Gateway
- VPC Interface Endpoints can be accessed through Private VIF
- should understand the Direct Connect Diagram slide architecture
- Dedicated Connections or Hosted Connections
  - can add or remove capacity for Hosted Connections
  - > 1 month lead time for new connections
- NOT encrypted by default (use VPN over DX Public VIF)
  - architecture diagram shows Private VIF though???
- Link Aggregation Groups (LAG) logically groups DX connections
  - active-active for increased speed and failover
  - requires Dedicated Connections
  - requires identical bandwidths
  - must terminate at same AWS Connect Endpoint
- Direct Connect Gateway to connect to VPC across regions and / or across accounts
  - allows you to integrates the DX with Transit Gateway

## On-Premise redundant Connections

- active-active VPN Connection
  - also works for DX
  - your corporate data centers need to be connected outside of AWS
  - could also mix VPN connections and DX connections
- Direct Connect Gateway SiteLink
  - create private network connection from on-premise to on-premise
  - this bypasses any AWS Regions

## VPC Flow Logs

- capture IP traffic going into your interfaces
  - VPC Flow Logs
  - Subnet Flow Logs
  - Elastic Network Interface (ENI) Flow Logs
- can send to various data sources (e.g., Kinesis Data Firehose)
- capture network information from AWS managed interfaces too
  - ELB
  - RDS
  - WorkSpaces
  - Transit Gateway
  - etc.
- has specific format
- query the logs using Athena on S3 or (for streaming analysis) CloudWatch Logs Insights
  - are all CloudWatch Logs Insights for streaming data???
- CloudWatch Contributor Insights for highest traffic
- inbound public IP traffic can make it to NAT Gateways, but is then dropped!!!

## AWS Network Firewall

- ways to control your networks
  - NACLs
  - Amazon VPC security groups
  - AWS WAF
  - AWS Shield and AWS Shield Advanced
  - AWS Firewall Manager
- to protect the your entire VPC, use AWS Network Firewall
  - from Layer 3 to Layer 7
  - need to review network layers???
  - can inspect any traffic / connections to the VPC
- under the hood, uses AWS Gateway Load Balancer
- can manage rules cross-account with AWS Firewall Manager
- allow, drop, or alert on traffic rules
- Active flow inspection for intrusion-prevention
- send logs of rule matches to various destinations (e.g., S3)
- "north-south" traffic enters / leaves your network
- "east-west" traffic stays within your network

## Quiz 15 - VPC Quiz

- PrivateLink is good for SaaS services that need to give access to many other VPCs
- Transit Gateway can scale up AWS Site-to-Site VPN connection throughput

## Study Group Practice Questions

- TODO

# Section 16 - Machine Learning

## Rekognition Overview

- service to find objects, people, text, and scenes in images or videos
- facial analysis and facial search for user verification or people counting
- create a database of "familiar faces" or compare against celebrities
- content moderation
	- used in various business models to create a safe user experience
	- use Minimum Confidence Threshold for items that will be flagged
	- can use Amazon Augmented AI (A2I) for optional manual review
- helpful to comply with regulations (exam tip)

## Transcribe Overview

- automatically transcribe speech to text
- Automatic Speech Recognition (ASR) via deep learning
- remove Personally Identifiable Information (PII) using Redaction
- supports Automatic Language Identification for muli-lingual audio
	- e.g., English and French
- use cases
	- transcribe customer calls
	- automate closed captioning and subtitling
	- create metadata for media assets to create searchable archive

## Amazon Polly

- opposite of Transcribe service
- turn text into lifelike speech via deep learning
- Lexicon
	- customize pronunciation with Pronunciation Lexicons
	- upload the lexicon file then use it with the "SynthesizeSpeech" operation
	- for stylized words or acronym expansion
	- this is just one-to-one mappings of words???
- Speech Synthesis Markup Language (SSML)
	- put emphasis on certain words
	- use whispering
	- include breathing

## Amazon Translate

- service for language translation
- useful for localizing content (e.g., on a website)
- this service is only for text translation???

## Amazon Lex and Amazon Connect

- Amazon Lex
	- powers Alexa devices
	- Automatic Speech Recognition (ASR)
	- Natural Language Understanding to recognize intent of text or callers
	- helps build call center bots or chatbots
- Amazon Connect
	- virtual contact center
	- receives calls, create contact flows
	- integrates with Customer Relationship Management (CRM) systems
	- integrates with other AWS services
	- cheaper than traditional contact center solutions

## Amazon Comprehend

- fully managed, serverless service for Natural Language Processing (NLP)
- uses ML to find insights and relationships in text
- features 
	- sentitment analysis
	- tokenization
	- extract key phrases
	- etc.
- use case: analyze customer emails for positive / negative experiences

## Amazon Comprehend Medical

- detects and returns useful information in unstructured clinical text
- detect Protected Health Information (PHI) using NLP
- integrates with S3, Kinesis Firehouse, Transpose, etc.

## Amazon SageMaker

- fully managed service for developers / data scientists to build ML models
- example of predicting students' scores on the AWS exam

## Amazon Kendra

- fully managed document search service powered by ML
- natural language search capabilities to answer questions based on PDF, HTML, etc.
- Incremental Learning via feedback from user interactions
- can manually fine-tine search results (e.g., by freshness or importance)

## Amazon Personalize

- fully managed ML service to build apps with real-time personalized recommendations
- e.g., product recommendations based on previous purchases and user interests
- the Amazon Personalize APIs are for separate goals such as...
	- control plane
	- data plane
		- ingesting data
		- getting recommendations
- you don't have to build any of the ML models or data pipelines

## Amazon Textract

- uses AI and ML to extract text from any scanned document
- for example...
	- handwriting
	- driver license
	- PDF
	- etc.

## AWS Machine Learning Summary

- good summarizing slide of all the services' purposes

## Machine Learning Section Quiz

- got all the questions correct!

# Section 17 - Other Services

## Other Services

- very short lectures on misc service offerings by AWS

## Code Commit (Deprecated!!!)

- July 25th, 2024 it as discontinued
- GitHub or GitLab as alternatives

## Continuous Integration Continuous Delivery (CICD)

- Continuous Integration (CI)
	- deliver code faster with less bugs
	- build server worries about checks
- Continuous Delivery (CD)
	- ensure software can be deployed reliably
	- usually CodeDeploy, Jenkins CD, Spinnaker, etc.
	- builder servers and deployment servers
- tech stack stages for CICD (in order)
	- Code (AWS CodeCommit vs GitHub) (no other AWS alternative)
	- Build (AWS CodeBuild vs Jenkins CI) (no other AWS alternative)
	- Test (AWS CodeBuild vs Jenkins CI) (no other AWS alternative)
	- Deploy (AWS CodeDeploy or AWS Elastic Beanstalk)
	- Provision (AWS Elastic Beanstalk or User Managed EC2 Instances Fleet / CloudFormation)
- this can all be orchestrated using AWS CodePipeline
- good CICD architecture diagram (this is typical exam question!!!)
	- pretty standard dev practices
- can trigger AWS Lambda on every AWS CodeCommit commit
	- scan for leaked secrets, lock repo, send SNS, etc.
- manual approval stage is possible
- CodeBuild and ECR for Docker images
- CodePipeline for automated flows
- webhooks can be used to trigger CodePipeline from GitHub
	- GitHub App "CodeStar Source Connection" is more modern approach
- AWS CodeStar - "a cloud service designed to make it easier to develop, build, and deploy applications on AWS by simplifying the setup of your entire development project"
	- including project management dashboards, etc.

## Amazon CodeGuru

- ML-powered code reviews and performance recommendations
	- CodeGuru Reviewer (static code analysis)
		- currently supports Python and Java languages
	- CodeGuru Profiler (production runtime)
		- e.g., determine that logging is using a lot of CPU

## Alexa for Business, Lex and Connect

- Alexa for Business
	- make employees productive in meeting rooms and at their desks???
- Amazon Lex
	- Automatic Speech Recognition (ASR)
	- Natural Language Understanding to recognize intent of text, callers
	- build chatbots or call center bots
- Amazon Connect
	- act like a call center
	- receive calls, create contact flows, integrate with CRMs

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

## Amazon WorkSpaces

- managed, secure cloud desktops
- Virtual Desktop Infrastructure (VDI)
- on-demand or monthly subscriptions
- integrates with Microsoft Active Directory
- Windows or Linux machines
- WorkSpaces Application Manager (WAM)
	- deploy managed applications as virutalized application containers
- Windows updates handled automatically
	- uses Maintenance Windows (you can define)
	- Always On WorkSpaces default to Sunday morning
	- AutoStop WorkSpaces perform updates once a month
- Cross Region Redirection
	- create AD Connector in failover region
		- can't use multi-region AWS Managed Microsoft AD (per documentation)
	- Route53 TXT record for connection aliases to each region
	- user data can be persisted across regions with Amazon WorkDocs
	- user data is region specific!!!
- IP Access Control Groups
	- like Security Groups, but for addresses ranges users can be from

## Amazon AppStream 2.0

- desktop application streaming service
- web browser used to deliver desktop application to users
- e.g., Blender can be compute intensive
- WorkSpaces is a fully managed VDI
- AppStream is just a stream and works on any device with a web browser

## AWS Device Farm

- useful for testing an app across many real browsers and devices
- fully automated testing using framework
- generate videos and logs for debugging
- remotely login to devices for even more debugging

## Amazon Macie

- ML and pattern matching service to discover and protect sensitive data
- alerts about sensitive data, such as personally identifiable information (PII)

## Amazon SES (Simple Email Service)

- managed service to send emails securely, globally and at scale
- inbound and outbound emails
- reputation dashboard, performance insights, anti-spam feedback
- supports DomainKeys Identified Mail (DKIM) and Sender Policy Framework (SPF)
	- are these meaningful???
- shared, dedicated, or customer-owned IPs
- Configuration Sets
	- customize and analyze your email send events
	- event destinations
		- Kinesis Data Firehose (for email metrics)
		- SNS (for immediate bounce and complaint feedback)
	- IP pool management
		- separate email reputations based on IP you send with

## Amazon Pinpoint

- two-way inbound / outbound marketing communications
- supports... messaging
	- email
	- SMS
	- push
	- voice
	- in-app
- scales to billions of messages per day
- can handle stream events with SNS, KDF, CloudWatch Logs
- Amazon Pinpoint manages delivery schedule, highly-targeted segments, full campaigns
	- this is how it differs from SES or SNS

## EC2 Image Builder

- automate the creation of Virtual Machiens or container images
- free and only pay for underlying resources
- publish AMI to multiple regions and multiple accounts
- steps
	- spawn Builder EC2 Instance
	- create AMI from the instance
	- spawn new test instance with the new AMI
	- run tests to validate the AMI's functionality / security
- can integrate with CICD pipeline via AWS CodePipeline

## AWS IoT Core

- Internet of Things (IoT)
- service allows you to easily connect IoT devices to the cloud
- scales to billions of devices and trillions of messages
- IoT Topics are similar to SNS Topics
	- set up IoT Rules and Actions 
- for example, you can...
	- can send into KDF for example
	- then, persist in S3, Redshift, or OpenSearch

## Other Services Summary

- CodeCommit: store code in version-controlled repositories. Code can live on multiple branches
- CodeBuild: build & test code on-demand in your CICD pipelines.
- CodeDeploy: deploy code on EC2, ASG, Lambda or ECS
- CodePipeline: orchestrate CICD pipelines. If using CodeCommit as a source, matches to only one branch
- CodeGuru: automated code reviews and application performance recommendations using ML
- CloudSearch: managed search solution to perform a full-text search, auto-completion in your applications
- Alexa for Business: use Alexa to help employees be more productive in meeting rooms and their desk
- Lex: Automatic Speech Recognition (ASR) to convert speech to text. Helpful to build chatbots
- Connect: receive calls, create contact flows, cloud-based virtual contact center
- Rekognition: find objects, people, text, scenes in images and videos using Machine Learning
- Kinesis Video Stream: one stream per video device, analyze using EC2 instances or Rekognition
- WorkSpaces: on-demand Windows workstations. WAM is used to manage applications
- AppStream 2.0: stream desktop applications into web browsers
- Device Farm: Application testing service for your mobile and web applications across real devices

## Section Quiz

- no issues, just had to identify which service the question described

