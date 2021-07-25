import boto3
from matching_participants import matching
import pandas as pd
import json

dynamodb = boto3.resource('dynamodb')
table_interests = dynamodb.Table('participant-interests')

def lambda_handler(event, context):
    response = table_interests.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table_interests.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    
    data_df = pd.DataFrame(data)
    return {
        'statusCode': 200,
        'body': json.dumps(matching(data))
    }

