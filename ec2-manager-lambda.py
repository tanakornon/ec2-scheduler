import boto3
from typing import List, Dict

class EC2Manager:
    def __init__(self, region: str = "ap-southeast-1"):
        self.client = boto3.client("ec2", region_name=region)

    def start_instances(self, instance_ids: List[str]) -> Dict:
        return self.client.start_instances(InstanceIds=instance_ids)

    def stop_instances(self, instance_ids: List[str]) -> Dict:
        return self.client.stop_instances(InstanceIds=instance_ids)

class EC2ActionHandler:
    def __init__(self, manager: EC2Manager):
        self.manager = manager
        self.actions = {
            "start": self.manager.start_instances,
            "stop": self.manager.stop_instances
        }

    def handle(self, action: str, instance_ids: List[str]) -> str:
        if not instance_ids:
            raise ValueError("No instance IDs provided.")
        if action not in self.actions:
            raise ValueError(f"Invalid action: {action}")

        self.actions[action](instance_ids)
        return f"{action.capitalize()}ed instances: {', '.join(instance_ids)}"

def lambda_handler(event, context):
    action = event.get("action", "").lower()
    instance_ids = event.get("instance_ids", [])

    try:
        handler = EC2ActionHandler(EC2Manager())
        return {
            "statusCode": 200,
            "body": handler.handle(action, instance_ids)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
