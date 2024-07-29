# Cisco SD-WAN and ThousandEyes Integration

# Objective 

*   Data policy creation based of the tests that are created on the enterprise agent. 

# Requirements

To use this code you will need:

* Python 3.7+
* vManage user login details. (User should have privilege level to create centraliaed data policies)
* ThousandEyes API token 

# Install and Setup

- Clone the code to local machine.

```
git clone https://github.com/shreyas23reddy/SDWAN-TE-AUTOMATED-POLICY-CREATION
cd SDWAN-TE-AUTOMATED-POLICY-CREATION
```
- Setup Python Virtual Environment (requires Python 3.7+)

```
python3.7 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

- Create **config_details.yaml** using below sample format to provide the login details of vManage, agent name and data policy name.

## Example:

```
# vManage Connectivity Info

vmanage_host: 
vmanage_port: 
vmanage_username:

#ThousandEyes Enterprise Agent Name 
agentName: 

# Centralized Data Policy-name
data_policy_name: 

```
- Create **.env** using below sample format to provide the vManage password and TE API token.
export OAUTH_TOKEN = 4xxxxxxxxxxxxxxxxxx
export vmanage_password = xxxxxxxxxxxxxx

- Run the script using the command `python3 Data-Policy-TE.py`

Script will walk you through the already created tests to request for some input and based of the inputs we will able to  create a centralized data policy.  

## Example:

Do we have a subnet reserved for ThousandEyes Agent in the SDWAN fabric?

1. If yes, please enter the subnet. [Example: 10.0.0.0/12 seperated by commas]
2. if no, please just hit enter/return 
Your Input : 172.16.0.0/16

-------------------------------------------------------------------------------------------                           
Test Name - 120-105-mpls-overlay - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay o

Test Name - 120-105-mpls-overlay, DSCP - AF 22 (DSCP 20) probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
13

-------------------------------------------------------------------------------------------                           
Test Name - San Jose, CA (Webex) - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay u

Test Name - San Jose, CA (Webex), DSCP - Best Effort (DSCP 0) probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
0

%% WARNING : Since the target server is configured using Domain name, script is capable of creating Destination match based of IP only. 
Please review the policy Sequence number - 21 once its created

------------------------------------------------------------------------------------------- 
Test Name - 120-105-BIZ-Router-1_underlay_ICMP - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay u

Test Name - 120-105-BIZ-Router-1_underlay_ICMP, DSCP - AF 21 (DSCP 18) probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
3

------------------------------------------------------------------------------------------- 
Test Name - 120-105-Router-1-MPLS_underlay_ICMP - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay u

Test Name - 120-105-Router-1-MPLS_underlay_ICMP, DSCP - AF 22 (DSCP 20) probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
13

------------------------------------------------------------------------------------------- 
Test Name - SDGE_TE - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay o

Test Name - SDGE_TE, DSCP - AF 21 (DSCP 18) probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
0

------------------------------------------------------------------------------------------- 
How does TE Agent communicate to TE dashboard?
Please enter 'U' for underlay, 'O' for overlay u

*********Successfully created the Data Policy**************
