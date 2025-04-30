# Setup EC2 downtime to save cost

## ✅ Step 1: Create IAM Role for Lambda

Go to IAM > Roles and create a new role:

- Trusted entity: AWS Service → Lambda
- Permissions: Attach a custom Inline Policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

Name it something like: LambdaEC2ControlRole

## ✅ Step 2: Create Lambda Function to Start and Stop EC2

### 🔹 Stop EC2

```python
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='ap-southeast-1')  # Change region as needed
    instance_ids = ['i-xxxxxxxxxxxxxxxxx']  # Replace with your EC2 instance ID(s)
    
    ec2.stop_instances(InstanceIds=instance_ids)
    return f'Stopped instances: {instance_ids}'
```

### 🔹 Start EC2

```python
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='ap-southeast-1')  # Change region as needed
    instance_ids = ['i-xxxxxxxxxxxxxxxxx']  # Replace with your EC2 instance ID(s)
    
    ec2.start_instances(InstanceIds=instance_ids)
    return f'Started instances: {instance_ids}'
```

### 🔹 For better version see [ec2-scheduler-lambda.py](ec2-scheduler-lambda.py)

## ✅ Step 3: Create CloudWatch Scheduled Events

Go to CloudWatch > Rules (EventBridge > Scheduler)

### 🔹 Create Rule to Stop Instance

- Name: stop-ec2-daily
- Schedule pattern: cron(0 13 ? *MON-FRI*) → runs at 8 PM Bangkok time (13:00 UTC)
- Target: Lambda function → stop-ec2-instance

### 🔹 Create Rule to Start Instance

- Name: start-ec2-daily
- Schedule pattern: cron(0 1 ? *MON-FRI*) → runs at 8 AM Bangkok time (01:00 UTC)
- Target: Lambda function → start-ec2-instance

#### ⏱ Cron Format Reference (UTC-based)

```sh
cron(Min Hour Day-of-Month Month Day-of-Week Year)
```

> So cron(0 1 ? *MON-FRI*) means 01:00 UTC Mon–Fri

## ✅ How to Schedule a Lambda with EventBridge (CloudWatch Events)

### 🔹 Example

- Start instance every day at 08:00
- Stop instance every day at 20:00

## 🛠 Step-by-Step Setup

### 1. Go to Amazon EventBridge Console

- <https://console.aws.amazon.com/events/>
- Click "Rules" on the left
- Click "Create rule"

### 2. Define Rule Details

- Name: start-ec2-lambda-schedule
- Description (optional): Run Lambda to start EC2 instance daily at 8AM
- Event bus: Default
- Rule type: Schedule

### 3. Define Schedule Pattern

- Choose "Recurring schedule"
- Use Cron expression:

    ```sh
    cron(0 8 * * ? *)
    ```

    > This runs at 08:00 UTC every day (adjust for your timezone, e.g., 1 AM UTC = 8 AM Thailand)

### 4. Add Target

- Target type: AWS service
- Service: Lambda function
- Function: Choose your Lambda
- Execution role: Leave default (or create if asked)
- Input:
  - Select Constant (JSON text)
  - Paste:

    ```sh
    {
        "action": "start",
        "instance_ids": [
            "i-xxxxxxxxxxxxxxxxx"
        ]
    }
    ```

### 5. Click Create Rule

- Repeat for Stop Rule
- Create another rule:
  - Name: stop-ec2-lambda-schedule
  - Schedule:

    ```sh
    cron(0 20 * * ? *)
    ```

  - Input:

    ```sh
    {
        "action": "stop",
        "instance_ids": [
            "i-xxxxxxxxxxxxxxxxx"
        ]
    }
    ```
