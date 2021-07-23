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
now = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

# define the handler function that the Lambda service will use as an entry point
def lambda_handler(event, context):
# extract values from the event object we got from the Lambda service and store in a variable
    kerberosID = event['kerberosID']
    firstName = event['firstName']
    lastName = event['lastName']
    email = event['email']
    gender = event['gender']
    division = event['division']
    team = event['team']
    location = event['location']
    position = event['position']
    year = event['year']
    outdoors = 1 if event['outdoors'] else 0
    sports = 1 if event['sports'] else 0
    music = 1 if event['music'] else 0
    food = 1 if event['food'] else 0
    gaming = 1 if event['gaming'] else 0
    cafe = 1 if event['cafe'] else 0
    movies = 1 if event['movies'] else 0
    reading = 1 if event['reading'] else 0
    photography = 1 if event['photography'] else 0

# write name and time to the DynamoDB table using the object we instantiated and save response in a variable
    response1 = table_details.put_item(
        Item={  "kerberosID" : kerberosID,
                "firstName" : firstName,
                "lastName" : lastName,
                "email" : email,
                "gender" : gender,
                "division" : division,
                "team" : team,
                "country" : location,
                "position" : position,
                "startYear" : year})
    response2 = table_interests.put_item(
        Item={  "kerberosID" : kerberosID,
                "outdoors" : outdoors,
                "sports" : sports,
                "music" : music,
                "food" : food,
                "gaming" : gaming,
                "cafe" : cafe,
                "movies" : movies,
                "reading" : reading,
                "photography" : photography,
                kerberosID : '0.1'
        })
# return a properly formatted JSON object
    return {
        'statusCode': 200,
        'body': json.dumps('Sign up successful for ' + kerberosID + ', thank you!')
    }
