import subprocess
from decimal import Decimal
import boto3
import os
import simplejson as json
import argparse
from datetime import datetime

def get_aws_credentials():
    """Retrieve AWS credentials from environment variables."""
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('REGION')
    table_name = os.getenv('TABLE_NAME')

    if not aws_access_key_id or not aws_secret_access_key:
        raise Exception("AWS credentials not found in environment variables")

    return aws_access_key_id, aws_secret_access_key, region, table_name

def get_dynamodb_client(aws_access_key_id, aws_secret_access_key, region):
    """Create and return a DynamoDB resource client."""
    try:
        dynamodb = boto3.resource('dynamodb',
                                  region_name=region,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key)
        return dynamodb
    except Exception as e:
        raise Exception(f"Error creating DynamoDB client: {e}")

def get_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description='Internet Speed Test with Optional DynamoDB Saving')
    parser.add_argument('--no-save', action='store_true', help='Disable saving results to DynamoDB')
    parser.add_argument('--no-print', action='store_true', help='Disable print of results')
    return parser.parse_args()

def run_command(command):
    """Run a shell command and return its output."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed ({result.returncode}) with error: {result.stderr or result.stdout}")
    return result.stdout.strip()

def measure_speed(args):
    """Use speedtest-cli to measure internet speed."""
    result = run_command("speedtest --format=json")
    try:
        return json.loads(result, parse_float=Decimal)
    except json.JSONDecodeError:
        if not args.no_print:
            print("Error decoding JSON")
        return None

def save_to_dynamodb(table, data, args):
    """Save the measured data to DynamoDB in its entirety."""
    try:
        response = table.put_item(Item=data)
        return response
    except Exception as e:
        if not args.no_print:
            print(f"Error saving data to DynamoDB: {e}")
        return None

def main():
    args = get_arguments()
    aws_access_key_id, aws_secret_access_key, region, table_name = get_aws_credentials()
    dynamodb = get_dynamodb_client(aws_access_key_id, aws_secret_access_key, region)
    table = dynamodb.Table(table_name)

    speed_data = measure_speed(args)
    timestamp = datetime.now().isoformat()

    if not args.no_print:
        print("Speed Test Results:")
        print(json.dumps(speed_data, indent=4))

     # Calculate speeds for Mb/s => bytes*8/(elapsed_ms*1000)
    speed_data['upload']['speed'] = Decimal(str(speed_data['upload']['bytes']*8/(speed_data['upload']['elapsed']*1e3)))
    speed_data['download']['speed'] = Decimal(str(speed_data['download']['bytes']*8/(speed_data['download']['elapsed']*1e3)))

    data = {
        "Index": str(timestamp),
        **speed_data
    }
   

    if not args.no_save:
        save_to_dynamodb(table, data, args)
        if not args.no_print:
            print(f"Data saved for {timestamp}")
    else:
        if not args.no_print:
            print(f"Data not saved for {timestamp}")

if __name__ == "__main__":
    main()
