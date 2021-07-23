# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
# import two packages to help us with dates and date formatting
from time import gmtime, strftime
import sys
import logging
import pymysql
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
# use the DynamoDB object to select our table
table_details = dynamodb.Table('participant-details')
table_interests = dynamodb.Table('participant-interests')
# store the current time in a human readable format in a variable

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
# extract values from the event object we got from the Lambda service and store in a variable
    kerberosID = event['kerberosID']
    try:
        response = table_details.delete_item(
            Key={
                'kerberosID': kerberosID,
            }
        )
        response = table_interests.delete_item(
            Key={
                'kerberosID': kerberosID,
            }
        )
        
        done = False
        start_key = None
        response = table_details.scan()
        data = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        
        for row in data:
            if kerberosID in row.keys():
                table_interests.update_item(
                    Key={
                            'kerberosID': row['kerberosID'],
                        },
                    UpdateExpression=f"REMOVE {kerberosID}",
                    ReturnValues="ALL_NEW"
                )
        
    # Update feedback RDS
        # Read mysql connection variables
        rds_host = os.environ['RDS_HOST']
        rds_user = os.environ['RDS_USER']
        rds_password = os.environ['RDS_PASSWORD']
        rds_db_name = os.environ['RDS_DB_NAME']
        rds_table_name = os.environ['RDS_TABLE_NAME']

    # Connect to RDS
        try:
            print("attempting to connect to db")
            conn = pymysql.connect(host=rds_host, user=rds_user, passwd=rds_password, db=rds_db_name, connect_timeout=5)
        except pymysql.MySQLError as e:
            logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
            logger.error(e)
            sys.exit()

        logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
        cur = conn.cursor()
        
        # Check if user exists in db
        select_query = "Select * from {} where id = \"{}\"".format(rds_table_name, kerberosID)
        cur.execute(select_query)
        existing_user = cur.fetchone()
        print(existing_user)
        
        if existing_user is not None:
            insert_query = "delete from {} where id = \"{}\"".format(rds_table_name, kerberosID)
            print(insert_query)
            cur.execute(insert_query)
        else:
            print("User does not exist")

        conn.commit()
            
        return {
            'statusCode': 200,
            'body': json.dumps('Unsubscribe successful for ' + kerberosID + ', thank you!')
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'body': json.dumps(e)
        }