import boto3
import os

"""
You need to configure the environment variables:
    ACCESS_KEY_ID = "Your access key id"
    SECRET_ACCESS_KEY = "Your secret key id"
    AWS_KEY_NAME = "the name of the key you have"
"""


class MemcacheEC2(object):
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client
        self.maxMemcacheNumber = 8
        self.memcacheDict = {}
        self.amiID = "ami-080ff70d8f5b80ba5"  # Change it to my own AMI

    def grep_vpc_subnet_id(self):
        response = self.ec2_client.describe_vpcs()
        vpc_id = ""
        for vpc in response["Vpcs"]:
            if vpc["InstanceTenancy"].__contains__("default"):
                vpc_id = vpc["VpcId"]
                break
        response = self.ec2_client.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        subnet_id = response["Subnets"][0]["SubnetId"]
        return vpc_id, subnet_id

    def create_security_group(self):
        sg_name = "memcache_security_group"
        try:
            vpc_id, subnet_id = self.grep_vpc_subnet_id()
            response = self.ec2_client.create_security_group(
                GroupName=sg_name,
                Description="Memcache Security Group. This is created using python",
                VpcId=vpc_id,
            )
            sg_id = response["GroupId"]
            self.ec2_client.authorize_security_group_ingress(
                GroupId=sg_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 5001,
                        "ToPort": 5001,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                    },
                ],
            )
            return sg_id, sg_name
        except Exception as e:
            if str(e).__contains__("already exists"):
                response = self.ec2_client.describe_security_groups(
                    GroupNames=[sg_name]
                )
                sg_id = response["SecurityGroups"][0]["GroupId"]
                return sg_id, sg_name

    def create_ec2_instance(self):

        if not self.refresh_memcacheDict():
            print("Error")
            return

        if len(self.memcacheDict) >= self.maxMemcacheNumber:
            print("Cannot create new instance. dict already has 8. ")
            return
        try:
            number = 0
            for i in range(self.maxMemcacheNumber):
                if str(i) in self.memcacheDict.keys():
                    continue
                number = i
                break
            memcacheName = "Memcache_Node_" + str(number)
            sg_id, sg_name = self.create_security_group()
            vpc_id, subnet_id = self.grep_vpc_subnet_id()
            conn = self.ec2_client.run_instances(
                ImageId=self.amiID,
                MinCount=1,
                MaxCount=1,
                InstanceType="t2.micro",
                KeyName=os.environ["AWS_KEY_NAME"],
                SecurityGroupIds=[sg_id],
                SubnetId=subnet_id,
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": memcacheName},
                        ],
                    }
                ],
            )
            self.memcacheDict[str(number)] = {
                "Name": memcacheName,
                "Status": conn["Instances"][0]["State"]["Name"],
                "instanceID": conn["Instances"][0]["InstanceId"],
                "amiID": self.amiID,
                "Number": number,
                "PublicIP": "",
            }
        except Exception as e:
            print("Error, ", e)

    def describe_ec2_instance(self):
        print("Describing EC2 instance")
        print(self.ec2_client.describe_instances())
        return self.ec2_client.describe_instances()

    def start_ec2_instance(self, number):

        if not self.refresh_memcacheDict():
            print("Error")
            return

        try:
            print("Start EC2 instance:", number)
            if self.memcacheDict:
                if not str(number) in self.memcacheDict:
                    print("Memcache number:", number, "not exist")
                    return
                instanceID = self.memcacheDict[str(number)]["instanceID"]
                if self.memcacheDict[str(number)]["Status"] == "stopped":
                    conn = self.ec2_client.start_instances(InstanceIds=[instanceID])
                    print("Signal to start Memcache number", number, "sent.")
                    self.memcacheDict[str(number)]["Status"] = conn[
                        "StartingInstances"
                    ][0]["CurrentState"]["Name"]
                    if self.memcacheDict[str(number)]["Status"] == "pending":
                        print("Memcache number", number, "is pending...")

                elif self.memcacheDict[str(number)]["Status"] == "running":
                    print("Memcache number", number, "is already running.")
                elif self.memcacheDict[str(number)]["Status"] == "shutting-down":
                    print(
                        "Cannot start Memcache number",
                        number,
                        "because it is shutting down.",
                    )
                elif self.memcacheDict[str(number)]["Status"] == "pending":
                    print(
                        "Cannot start Memcache number", number, "because it is pending."
                    )
                elif self.memcacheDict[str(number)]["Status"] == "terminated":
                    print(
                        "Cannot start Memcache number",
                        number,
                        "because it is terminated.",
                    )
                elif self.memcacheDict[str(number)]["Status"] == "stopping":
                    print(
                        "Cannot start Memcache number",
                        number,
                        "because it is stopping.",
                    )

        except Exception as e:
            print("Error, ", e)

    def stop_ec2_instance(self, number):

        if not self.refresh_memcacheDict():
            print("Error")
            return
        try:
            print("Stop EC2 instance:", number)
            if self.memcacheDict:
                if not str(number) in self.memcacheDict:
                    print("Memcache:", number, "not exist")
                    return
                instanceID = self.memcacheDict[str(number)]["instanceID"]
                if self.memcacheDict[str(number)]["Status"] == "running":
                    conn = self.ec2_client.stop_instances(InstanceIds=[instanceID])
                    print("Signal to stop Memcache number", number, "sent.")
                    self.memcacheDict[str(number)]["Status"] = conn[
                        "StoppingInstances"
                    ][0]["CurrentState"]["Name"]
                    if self.memcacheDict[str(number)]["Status"] == "stopping":
                        print("Memcache number", number, "is stopping...")
                    # Delete public IP
                    self.memcacheDict[str(number)]["PublicIP"] = ""

                elif self.memcacheDict[str(number)]["Status"] == "stopped":
                    print("Memcache number", number, "is already stopped.")
                elif self.memcacheDict[str(number)]["Status"] == "shutting-down":
                    print(
                        "Cannot stop Memcache number",
                        number,
                        "because it is shutting down.",
                    )
                elif self.memcacheDict[str(number)]["Status"] == "terminated":
                    print(
                        "Cannot stop Memcache number",
                        number,
                        "because it is terminated.",
                    )
                elif self.memcacheDict[str(number)]["Status"] == "stopping":
                    print(
                        "Cannot stop Memcache number", number, "because it is stopping."
                    )
                elif self.memcacheDict[str(number)]["Status"] == "pending":
                    print(
                        "Cannot stop Memcache number", number, "because it is pending."
                    )

        except Exception as e:
            print("Error, ", e)

    def stop_largest_ec2_instance(self):
        if self.memcacheDict:
            number = 0
            for i in range(self.maxMemcacheNumber - 1, -1, -1):
                if str(i) not in self.memcacheDict.keys():
                    continue
                number = i
                break
            return self.stop_ec2_instance(number)
        print("MemcacheDict is empty")
        return False

    def terminate_ec2_instance(self, number):

        if not self.refresh_memcacheDict():
            print("Error")
            return False

        try:
            print("Terminate EC2 instance:", number)
            if self.memcacheDict:
                if not str(number) in self.memcacheDict:
                    print("Memcache:", number, "not exist")
                    return False
                instanceID = self.memcacheDict[str(number)]["instanceID"]
                if (
                        self.memcacheDict[str(number)]["Status"] != "shutting-down"
                        and self.memcacheDict[str(number)]["Status"] != "terminated"
                ):
                    conn = self.ec2_client.terminate_instances(InstanceIds=[instanceID])
                    print("Signal to terminate Memcache number", number, "sent.")
                    self.memcacheDict[str(number)]["Status"] = conn[
                        "TerminatingInstances"
                    ][0]["CurrentState"]["Name"]

                    if self.memcacheDict[str(number)]["Status"] == "shutting-down":
                        print("Memcache number", number, "is shutting down...")
                    self.memcacheDict.pop(str(number))
                else:
                    print(
                        "Cannot terminate Memcache number",
                        number,
                        "because it is already gone forever.",
                    )
                    return False
            return True
        except Exception as e:
            print("Error, ", e)
            return False

    def terminate_largest_ec2_instance(self):
        if self.memcacheDict:
            number = 0
            if not self.refresh_memcacheDict():
                print("Error")
                return
            for i in range(self.maxMemcacheNumber - 1, -1, -1):
                if str(i) not in self.memcacheDict.keys():
                    continue
                if self.memcacheDict[str(i)]["Status"] == "shutting-down":
                    self.memcacheDict.pop(str(i))
                    continue
                if self.memcacheDict[str(i)]["Status"] == "terminated":
                    self.memcacheDict.pop(str(i))
                    continue
                number = i
                break
            return self.terminate_ec2_instance(number)
        print("MemcacheDict is empty.")
        return False

    def get_instanceIDs(self):
        try:
            response = self.ec2_client.describe_instances()
            instanceIDs = []
            for i in response["Reservations"]:
                if (
                        self.amiID == i["Instances"][0]["ImageId"]
                        and "Tags" in i["Instances"][0]
                        and ("Memcache_Node") in i["Instances"][0]["Tags"][0]["Value"]
                        and i["Instances"][0]["State"]["Name"] != "terminated"
                ):
                    instanceIDs.append(i["Instances"][0]["InstanceId"])
            return instanceIDs
        except Exception as e:
            print("Error, ", e)

    def get_active_instanceIDs(self):
        try:
            response = self.ec2_client.describe_instances()
            activeInstanceIDs = []
            states = ["running", "pending"]
            for i in response["Reservations"]:
                if (
                        self.amiID == i["Instances"][0]["ImageId"]
                        and i["Instances"][0]["State"]["Name"] in states
                        and "Tags" in i["Instances"][0]
                        and i["Instances"][0]["Tags"][0]["Value"].__contains__(
                    "Memcache_Node"
                )
                        and i["Instances"][0]["State"]["Name"] != "terminated"
                ):
                    activeInstanceIDs.append(i["Instances"][0]["InstanceId"])
            return activeInstanceIDs
        except Exception as e:
            print("Error, ", e)

    def get_num_of_memcache(self):
        if not self.refresh_memcacheDict():
            print("Error")
            return
        return len(self.memcacheDict)

    def get_num_of_active_memcache(self):
        if not self.refresh_memcacheDict():
            print("Error")
            return
        if self.memcacheDict:
            runningNum = 0
            for i in self.memcacheDict.values():
                if i["Status"] == "running":
                    runningNum = runningNum + 1
            return runningNum
        else:
            return 0

    def get_active_memcaches(self):
        if not self.refresh_memcacheDict():
            print("Error")
            return
        if self.memcacheDict:
            runningList = []
            for i in self.memcacheDict.values():
                if i["Status"] == "running":
                    runningList.append(i["Number"])
            return runningList
        else:
            return []

    def get_memcache_node_details(self, number, verbose=False):
        if not self.refresh_memcacheDict():
            print("Error")
            return
        if self.memcacheDict:
            if not str(number) in self.memcacheDict:
                print("Memcache number:", number, "not exist")
                return {}
        if verbose:
            print("Memcache Number ", self.memcacheDict[str(number)]["Number"])
            print("Name:", self.memcacheDict[str(number)]["Name"])
            print("Status:", self.memcacheDict[str(number)]["Status"])
            print("instanceID:", self.memcacheDict[str(number)]["instanceID"])
            print("amiID:", self.memcacheDict[str(number)]["amiID"])
            print("PublicIP:", self.memcacheDict[str(number)]["PublicIP"])

        return self.memcacheDict[str(number)]

    def get_public_IP(self, number, verbose=False):
        if not self.refresh_memcacheDict():
            print("Error")
            return
        if self.memcacheDict:
            if not str(number) in self.memcacheDict:
                print("Memcache:", number, "does not exist.")
                return {}
        if verbose:
            print("PublicIP:", self.memcacheDict[str(number)]["PublicIP"])
        return self.memcacheDict[str(number)]["PublicIP"]

    def update_public_IP(self):
        try:
            response = self.ec2_client.describe_instances()
            states = ["running", "pending"]
            for i in response["Reservations"]:
                if (
                        self.amiID == i["Instances"][0]["ImageId"]
                        and "Tags" in i["Instances"][0]
                        and i["Instances"][0]["Tags"][0]["Value"].__contains__(
                    "Memcache_Node"
                )
                        and i["Instances"][0]["State"]["Name"] != "terminated"
                ):
                    memcacheName = i["Instances"][0]["Tags"][0]["Value"]
                    memcacheNum = int(memcacheName[-1])
                    if i["Instances"][0]["State"]["Name"] in states:
                        if (
                                "PublicIpAddress" in i["Instances"][0].keys()
                                and i["Instances"][0]["PublicIpAddress"]
                        ):
                            if str(memcacheNum) in self.memcacheDict:
                                self.memcacheDict[str(memcacheNum)]["PublicIP"] = i[
                                    "Instances"
                                ][0]["PublicIpAddress"]
                else:
                    continue
        except Exception as e:
            print("Error, ", e)

    def refresh_memcacheDict(self):
        try:
            response = self.ec2_client.describe_instances()
            self.memcacheDict.clear()
            for i in response["Reservations"]:
                if (
                        self.amiID == i["Instances"][0]["ImageId"]
                        and "Tags" in i["Instances"][0]
                        and i["Instances"][0]["Tags"][0]["Value"].__contains__(
                    "Memcache_Node"
                )
                        and i["Instances"][0]["State"]["Name"] != "terminated"
                        and i["Instances"][0]["State"]["Name"] != "shutting-down"
                ):
                    memcacheName = i["Instances"][0]["Tags"][0]["Value"]
                    memcacheNum = int(memcacheName[-1])

                    self.memcacheDict[str(memcacheNum)] = {
                        "Name": memcacheName,
                        "Status": i["Instances"][0]["State"]["Name"],
                        "instanceID": i["Instances"][0]["InstanceId"],
                        "amiID": self.amiID,
                        "Number": memcacheNum,
                        "PublicIP": "",
                    }

                    if (
                            "PublicIpAddress" in i["Instances"][0].keys()
                            and i["Instances"][0]["PublicIpAddress"]
                    ):
                        self.memcacheDict[str(memcacheNum)]["PublicIP"] = i[
                            "Instances"
                        ][0]["PublicIpAddress"]
            return True
        except Exception as e:
            print("Error, ", e)
            return False
