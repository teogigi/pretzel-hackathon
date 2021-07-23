# import the json utility package since we will be working with a JSON object
import json
# import the AWS SDK (for Python the package name is boto3)
import boto3
# import two packages to help us with dates and date formatting
from time import gmtime, strftime

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

        return {
            'statusCode': 200,
            'body': json.dumps('Unsubscribe successful for ' + kerberosID + ', thank you!')
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'body': json.dumps(e)
        }
