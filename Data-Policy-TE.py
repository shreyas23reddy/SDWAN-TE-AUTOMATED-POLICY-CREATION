from ipaddress import ip_address
import requests
import sys
import json
import os
import ipaddress
import re
import logging
from pprint import pprint
import yaml
import random
from vmanage.api.authentication import Authentication
from vmanage.api.central_policy import CentralPolicy
from vmanage.api.policy_lists import PolicyLists
from vmanage.api.policy_definitions import PolicyDefinitions
from vmanage.api.http_methods import HttpMethods
from vmanage.api.utilities import Utilities
from logging.handlers import TimedRotatingFileHandler
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(filename='script_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

 
def create_prefix_list(session, vmanage_host, vmanage_port, payload):
    
    """This function creates data prefix list 
    return List ID if successful"""
    
    list_ID = None
    
    vmanage_policy_list = PolicyLists(session, vmanage_host, vmanage_port)
    
    try:
        response = vmanage_policy_list.post_data_prefix_list(name = payload['name'] , entries = payload["entries"])
    except Exception as e:
        logging.exception("failed to create data prefix list" + str(e))
        return (e.args)
    
    
    if response == 200:
        policy_list = vmanage_policy_list.get_data_prefix_list()
        for iter_policy_list in policy_list['json']['data']:
            if iter_policy_list["name"] == payload['name']:
                list_ID = iter_policy_list["listId"]
                break
        
        logging.info(f"**** Data prefix list created successfully :: {payload['name']} - {list_ID}******")
        return list_ID
                      
def create_data_policy(session, vmanage_host, vmanage_port, data_payload_seq_list):
    
    """This function creates a copy of existing centralized data policy returns None if successful
    extract the current centralized data policy and Add ThousandEye policy prior to existing sequences"""
    
    with open("config_details.yaml") as f:
        config = yaml.safe_load(f.read())
    
    data_policy_name = config["data_policy_name"]
    
    vManageDataPolicy = PolicyDefinitions(session, vmanage_host, vmanage_port)
    
    dataPolicy_List = vManageDataPolicy.get_policy_definition_list(definition_type='data')
    
    logging.info("***** Extracting current Centralized data policy******")
    
    
    dict = {'name': None, 'type': 'data', 'description': None, 'sequences':None, "defaultAction": None}
    
    seq_num = data_payload_seq_list[-1]["sequenceId"]
    logging.info(f"***** Trying to find {data_policy_name} from the list of centralized data policy******")
    
    for dataPolicy_iter in dataPolicy_List:
        
        if dataPolicy_iter['name'] == data_policy_name:
            
            logging.info(f"***** found {data_policy_name} from the list of centralized data policy ******")
            
            dict["name"] = dataPolicy_iter["name"] +"-TE-"+ str(random.randint(10000, 99999))
            dict["description"] = dataPolicy_iter["description"] + "with ThousandEyes"
            dict["defaultAction"] = dataPolicy_iter["defaultAction"]
            
            for seq_iter in dataPolicy_iter["sequences"]:
                seq_num += 10
                seq_iter["sequenceId"] = seq_num
                data_payload_seq_list.append(seq_iter)
            dict["sequences"] = data_payload_seq_list
            break
    
    logging.info(f"***** creating a new policy centrlized policy  {dict["name"]} ******")
    
    return (vManageDataPolicy.add_policy_definition(dict))
                
def get_tests(agentId=None):
    
    logging.info(f"***** Authenticating to TE dashboard ******")
    
    headers = {'Authorization': 'Bearer ' + os.environ['OAUTH_TOKEN'], "Accept": "application/hal+json" }
    
    if agentId == None:
        
        
        with open("config_details.yaml") as f:
            config = yaml.safe_load(f.read())
            
        agentName = config["agentName"]
        
        
        
        try:
            logging.info(f"***** Extracting info for all Enterprise Agents ******")     
            url = "https://api.thousandeyes.com/v7/agents?agentTypes=enterprise"
            payload = None
            headers = headers
            response = requests.request('GET', url, headers=headers)
            
        except Exception as e:
            logging.exception("Expcetion while getting jsession id without port \n" + str(e))
            
        try:
            response_dict = json.loads(response.content)
        
        except Exception as e:
            logging.exception("Expcetion while getting jsession id without port \n" + str(e))
            
            
        
        for agent in response_dict['agents']:
            logging.info(f"***** Extracting info for {agentName} ******") 
            if agent["agentName"] == agentName:
                agentId = agent["agentId"]
                break
    
    
    try:
        url = f"https://api.thousandeyes.com/v6/agents/{agentId}"
        response = requests.request('GET', url, headers=headers)
        agentDetailsResponse = json.loads(response.content)
    
    except Exception as e:
        logging.exception(str(e))
    
    return agentDetailsResponse

def validateIP(IP): 
    
    logging.info(f"***** validating {IP}******")
    
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\/(3[0-2]|2[0-9]|1[0-9]|[0-9])$"
    if(re.search(regex, IP)):
        logging.info(f"***** {IP} is valid  ******")
        return True 
    else: 
        logging.error(f"***** {IP} is invalid  ******")
        return False 
	                
def create_data_payload(agentDetailsResponse, session, vmanage_host, vmanage_port):
    
    count = 0
    
    color_List = [None,"default", "3g", "biz-internet", "blue",
                  "bronze", "custom1", "custom2", "custom3", "gold", "green", 
                  "lte", "metro-ethernet", "mpls", "private1", "private2", "private3",  
                  "private4", "private5", "private6", "public-internet", "red" , "silver"]
    
    
    print("\nDo we have a subnet reserved for ThousandEyes Agent in the SDWAN fabric?")
    
    val = True
    
    while val:
        
        if count !=0:
            print("\nInvalid entry try again \n")
        
        agentTESubnet = input(f"""
1. If yes, please enter the subnet. [Example: 10.0.0.0/12 seperated by commas]
2. if no, please just hit enter/return 
Your Input : """)
        logging.info(f"******** subnet reserved for ThousandEyes Agent in the SDWAN fabric {agentTESubnet} ********")
        
        count += 1
        
        if agentTESubnet:
            for i in re.split(',',agentTESubnet):
                if not validateIP((i.lstrip()).rstrip()):
                    logging.info(f"******** subnet reserved for ThousandEyes Agent is valid IPs {i} ********")
                    val = True
                    break
                else:
                    logging.error(f"******** subnet reserved for ThousandEyes Agent is invalid IPs {i} ********")
                    val = False
        else:
            if agentDetailsResponse['agents'][0]['agentType'] == 'Enterprise':
                agentTESubnet = f"{agentDetailsResponse['agents'][0]['ipAddresses'][0]}/32"
                logging.info(f"******** ThousandEyes Agent IP {agentTESubnet} ********")
                val = False
            

    agentTESubnetList = re.split(',',agentTESubnet)
    srcPrefixListName = "srcTE_AgentEntSubnet_"+str(random.randint(10000, 99999))
    
    payload = {"name": None,
              "type": "dataPrefix",
              "entries": []}
    
    payload["name"] = srcPrefixListName
    
    for i in agentTESubnetList:
        i = (i.lstrip()).rstrip()
        payload['entries'].append({"ipPrefix":i})
        
    SrcDataPrefixListID = create_prefix_list(session, vmanage_host, vmanage_port, payload)
    
    
    if SrcDataPrefixListID:
        logging.info(f"******** TE_agent Prefix list created Successfully with name {srcPrefixListName} list ID {SrcDataPrefixListID}********")
    
    sourceDataPrefix = {"field": "sourceDataPrefixList","ref":SrcDataPrefixListID}
    
    data_payload_seq_list = []
    
    count = 0
    
    for iterTest in (agentDetailsResponse['agents'][0]['tests']):
        logging.info(f"************************************************************************************")
        logging.info(f"******** Agent Test INFO  {iterTest} ********")
        data_payload_seq = {
      "sequenceId": None,
      "sequenceName": "ThousandEyesDataPolicy",
      "baseAction": "accept",
      "sequenceType": "data",
      "sequenceIpType": "ipv4",
      "match": {
        "entries": [sourceDataPrefix]
      },
      "actions": []
    }
        
        payload = {"name": None,"type": "dataPrefix","entries": []}
        dscp =  {"field": "dscp", "value": None}
        protocol = {"field": "protocol","value": None}
        destinationDataPrefixList = {"field": "destinationDataPrefixList","ref": None}
        destinationPort = {"field": "destinationPort","value": None}
        underlayNAT = {"type": "nat","parameter": [{"field": "useVpn", "value": "0"}]}
        setLocalTLOC = {"type": "set", "parameter": [{"field": "localTlocList","value": {"color": None,"restrict": ""}}]}
    
        
            
        if iterTest['type'] == 'agent-to-agent':
            logging.info(f"******** AgentTest type is 'agent-to-agent' ********")
            
            targetResponse = get_tests(agentId=iterTest['targetAgentId'])
            logging.info(f"******** Extract info about Target AgentTest ID {iterTest['targetAgentId']} ********")
            
            if targetResponse['agents'][0]['agentType'] == 'Enterprise':
                logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} is Enterprise Agent ********")
                
                for iterSubnet in agentTESubnetList:
                    iterSubnet = (iterSubnet.lstrip()).rstrip()
                    
                    if ipaddress.ip_address(targetResponse['agents'][0]['ipAddresses'][0]) in ipaddress.ip_network(iterSubnet):
                        logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} -  Enterprise Agent - IP belongs to TEagent subnet ********")
                        flag = True
                        break
                    else:
                        flag = False
                
                if flag == False:
                    
                    dstAgentIP = f"{targetResponse['agents'][0]['ipAddresses'][0]}/32"
                    dstPrefixListName = "destTE_agentEntIP_"+str(random.randint(10000, 99999))
                    logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} -  Enterprise Agent - creating data prefix list{dstPrefixListName} with {dstAgentIP} ********")
                    
                    payload["name"] = dstPrefixListName
                    payload['entries'] = {"ipPrefix":dstAgentIP}
                    
                    print(payload)
                    
                    DestDataPrefixListID = create_prefix_list(session, vmanage_host, vmanage_port, payload)
                    destinationDataPrefixList["ref"] = DestDataPrefixListID
                    data_payload_seq["match"]["entries"].append(destinationDataPrefixList)
                    logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} -  Enterprise Agent - created data prefix list{dstPrefixListName} with {dstAgentIP} ********")
                else:
                    
                    destinationDataPrefixList["ref"] = SrcDataPrefixListID
                    data_payload_seq["match"]["entries"].append(destinationDataPrefixList)
            
            
            if targetResponse['agents'][0]['agentType'] ==  'Cloud':
                
                logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} is Cloud Agent ********")
                
                for i in targetResponse['agents'][0]['ipAddresses']:
                    i = i+"/32"
                    payload['entries'].append({"ipPrefix":i})
                    
                
                dstPrefixListName = "destTE_agentCloudIPs_"+str(random.randint(10000, 99999))
                payload["name"] = dstPrefixListName
                logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} -  Cloud Agent - creating data prefix list{dstPrefixListName} with list od IP's {targetResponse['agents'][0]['ipAddresses']} ********")
                DestDataPrefixListID = create_prefix_list(session, vmanage_host, vmanage_port, payload)
                destinationDataPrefixList["ref"] = DestDataPrefixListID
                data_payload_seq["match"]["entries"].append(destinationDataPrefixList)
                logging.info(f"********Target AgentTest ID {iterTest['targetAgentId']} -  Cloud Agent - created data prefix list{dstPrefixListName} with list od IP's {targetResponse['agents'][0]['ipAddresses']} ********")
                    
                            
            
            data_payload_seq["sequenceId"] = (count*10) + 1
            count += 1
    
            dscp["value"] = str(iterTest['dscpId'])
            data_payload_seq["match"]["entries"].append(dscp)
            
            protocolValue = {"TCP":6,"ICMP":1,"UDP":17}
            
            if iterTest["protocol"].upper() in protocolValue.keys():
                protocol["value"] = str(protocolValue[iterTest["protocol"].upper()])
                data_payload_seq["match"]["entries"].append(protocol)
            
            
            
            
            while True:
                
                uo = input(f"""
-------------------------------------------------------------------------------------------                           
Test Name - {iterTest['testName']} - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay """).lower()
            
                if uo == "o":
                    break
            
                elif uo == "u":
                    data_payload_seq["actions"].append(underlayNAT)
                    break
            
                else:
                    print("Incorrect, please re-enter 'U' for underlay, 'O' for overlay ")
                    
            while True:
                try:
                    mapLocalTLOC = int(input(f"""
Test Name - {iterTest['testName']}, DSCP - {iterTest['dscp']} probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
"""))
                    break
                
                except:
                    print("Invalid, please re-enter ")
            if mapLocalTLOC != 0:    
                setLocalTLOC["parameter"][0]["value"]["color"] = color_List[mapLocalTLOC]
                data_payload_seq["actions"].append(setLocalTLOC)
            logging.info(f"********{data_payload_seq}********")
            data_payload_seq_list.append(data_payload_seq)
            
       
        if iterTest['type'] == 'agent-to-server':
            
            logging.info(f"******** AgentTest type is 'agent-to-server' ********")
            
            ipPort = re.split(":", iterTest['server'])
            
            logging.info(f"******** Extract info - Sever IP {ipPort} ********")
            
            if validateIP(ipPort[0]+"/32"):
                
                dstAgentIP = ipPort[0]+"/32"
                dstPrefixListName = "dest_ServerIP_"+str(random.randint(10000, 99999))
                
                payload["name"] = dstPrefixListName
                payload['entries'].append({"ipPrefix":dstAgentIP})
                
                logging.info(f"******** Creating  a data prefix list name {dstPrefixListName} ID {DestDataPrefixListID}  ********")
                
                DestDataPrefixListID = create_prefix_list(session, vmanage_host, vmanage_port, payload)
                destinationDataPrefixList["ref"] = DestDataPrefixListID
                data_payload_seq["match"]["entries"].append(destinationDataPrefixList)
            
            else:
                
                logging.error(f"""******** %% WARNING : Since the target server is configured using Domain name, script is capable of creating Destination match based of IP only. 
Please review the policy Sequence number - {(count*10) + 1} once its created ********""")
                
                print(f"""
%% WARNING : Since the target server is configured using Domain name, script is capable of creating Destination match based of IP only. 
Please review the policy Sequence number - {(count*10) + 1} once its created""")
                 
            data_payload_seq["sequenceId"] = (count*10) + 1
            count += 1
    
            dscp["value"] = str(iterTest['dscpId'])
            data_payload_seq["match"]["entries"].append(dscp)
            
            protocolValue = {"TCP":6,"ICMP":1,"UDP":17}
            
            if iterTest["protocol"].upper() in protocolValue.keys():
                protocol["value"] = str(protocolValue[iterTest["protocol"].upper()])
                data_payload_seq["match"]["entries"].append(protocol)
                
                if iterTest["protocol"].upper() == "TCP":
                    destinationPort["value"] = ipPort[1]
                    data_payload_seq["match"]["entries"].append(destinationPort) 
                    
            
            while True:
                
                uo = input(f"""
------------------------------------------------------------------------------------------- 
Test Name - {iterTest['testName']} - probes needs to be routed via underlay or overlay ? 
please enter 'U' for underlay, 'O' for overlay """).lower()
            
                if uo == "o":
                    
                    
                    break
            
                elif uo == "u":
                    data_payload_seq["actions"].append(underlayNAT)
                    break
            
                else:
                    print("Incorrect, please re-enter 'U' for underlay, 'O' for overlay ")
                    
            while True:
                try:
                    mapLocalTLOC = int(input(f"""
Test Name - {iterTest['testName']}, DSCP - {iterTest['dscp']} probes does this need to be routed via specific Local TLOC color?

0 - None           |    6 - custom1    |   12 - metro-ethernet  |    18 - private5
1 - default        |    7 - custom2    |   13 - mpls            |    19 - private6
2 - 3g             |    8 - custom3    |   14 - private1        |    20 - public-internet
3 - biz-internet   |    9 - gold       |   15 - private2        |    21 - red
4 - blue           |    10 - green     |   16 - private3        |    22 - silver
5 - bronze         |    11 - lte       |   17 - private4

please enter associated number :
"""))
                    break
                
                except:
                    print("Invalid, please re-enter ")
            if mapLocalTLOC != 0:       
                setLocalTLOC["parameter"][0]["value"]["color"] = color_List[mapLocalTLOC]
                data_payload_seq["actions"].append(setLocalTLOC)
            
            data_payload_seq_list.append(data_payload_seq)
            logging.info(f"********{data_payload_seq}********")
      
        
    
    
    while True:
        
        data_payload_seq = {
      "sequenceId": None,
      "sequenceName": "ThousandEyesDataPolicy",
      "baseAction": "accept",
      "sequenceType": "data",
      "sequenceIpType": "ipv4",
      "match": {
        "entries": [sourceDataPrefix]
      },
      "actions": []
    }
                
        uo = input(f"""
------------------------------------------------------------------------------------------- 
How does TE Agent communicate to TE dashboard?
Please enter 'U' for underlay, 'O' for overlay """).lower()
            
        if uo == "o":
            data_payload_seq["sequenceId"] = count*10 + 1
            count += 1
            data_payload_seq_list.append(data_payload_seq) 
            logging.info(f"******** TE Agent communicate to TE dashboard via overlay********")
            break
            
        elif uo == "u":
            
            data_payload_seq["sequenceId"] = count*10 + 1
            count += 1
            logging.info(f"******** TE Agent communicate to TE dashboard via underlay********")
            with open("Whitelist_TE.json") as jf:
                whitelistData = json.load(jf)
            
            
            
            payload = whitelistData["TE_IPV4_data_prefix"]
            payload["name"] = payload["name"]+str(random.randint(10000, 99999))
            logging.info(f"********creating a data prefix lixt name {payload["name"]} ********")
            DestDataPrefixListID = create_prefix_list(session, vmanage_host, vmanage_port, payload)
            logging.info(f"********created a data prefix lixt name {payload["name"]} ********")
            destinationDataPrefixList["ref"] = DestDataPrefixListID
            data_payload_seq["match"]["entries"].append(destinationDataPrefixList)
            data_payload_seq["actions"].append(underlayNAT)
            data_payload_seq_list.append(data_payload_seq)
            logging.info(f"********{data_payload_seq}********") 
            
            data_payload_seq = {
      "sequenceId": None,
      "sequenceName": "ThousandEyesDataPolicy",
      "baseAction": "accept",
      "sequenceType": "data",
      "sequenceIpType": "ipv4",
      "match": {
        "entries": [sourceDataPrefix]
      },
      "actions": []
    }
            data_payload_seq["sequenceId"] = count*10 + 1
            count += 1
            logging.info(f"********Default action accept any thing sourced from TE agent IP address********")
            data_payload_seq_list.append(data_payload_seq)
            logging.info(f"********{data_payload_seq}********") 
            break
            
        else:
            print("Incorrect, please re-enter 'U' for underlay, 'O' for overlay ")
            
    
    return data_payload_seq_list
    
                    


if __name__ == "__main__":
    
    with open("config_details.yaml") as f:
        config = yaml.safe_load(f.read())
    

    vmanage_host = config["vmanage_host"]
    vmanage_port = config["vmanage_port"]
    username = config["vmanage_username"]
    password = os.environ["vmanage_password"]
    
    logging.info(f"***** Auth to vManage generating token ******")
    session = Authentication(host=vmanage_host, port=vmanage_port, user=username, password=password).login()
    
    logging.info(f"***** Calling TE Agent ******")
    agentTestDetails = get_tests(agentId=None)
    
    logging.info(f"***** creating data payload to create a centralized data policy ******")
    dataPolicyPayload = create_data_payload(agentTestDetails, session, vmanage_host, vmanage_port)
    
    logging.info(f"***** Trying to create a Centrlized data policy ******")
    response = create_data_policy(session, vmanage_host, vmanage_port, dataPolicyPayload)
    
    if response == None:
        logging.info(f"***** new centrlized data policy created ******")
        print("\nSuccessfully created the Data Policy\n")
        
    else:
        logging.error(f"***** Error while creating a entrlized data policy {response}******")
        print(response)
    
    
    




