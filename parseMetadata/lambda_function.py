import sys
import logging
import pymysql
import os
import json
import datetime
import time
 
# Read mysql connection variables
rds_host = os.environ['RDS_HOST']
rds_user = os.environ['RDS_USER']
rds_password = os.environ['RDS_PASSWORD']
rds_db_name = os.environ['RDS_DB_NAME']
rds_table_name = os.environ['RDS_TABLE_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    print("attempting to connect to db")
    conn = pymysql.connect(host=rds_host, user=rds_user, passwd=rds_password, db=rds_db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def lambda_handler(event, context):
    
    # Read event payload
    id = event["id"]
    groupId = event["groupId"]
    messageCount = event["messageCount"]
    lastActiveTime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(event["lastActiveTime"]))

    cur = conn.cursor()

    # Check if user exists in db
    select_query = "Select * from {} where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, id, groupId)
    cur.execute(select_query)
    existing_user = cur.fetchone()

    # If user exists in db, append suggestions and update scores
    if existing_user is not None:
        print("User {} exists".format(existing_user[0]))
        update_query = "Update {} set messageCount = \"{}\", lastActiveTime = \"{}\" where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, messageCount, lastActiveTime, id, groupId)
        count = cur.execute(update_query)
    # If user does not exist, insert new record
    else:
        print("User not found!")
        insert_query = "Insert into {} (id, groupId, messageCount, lastActiveTime) values (\"{}\", \"{}\", \"{}\", \"{}\")".format(rds_table_name, id, groupId, messageCount, lastActiveTime)
        count = cur.execute(insert_query)
        
    conn.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Record update successful for ' + id + ', thank you!')
    }
    