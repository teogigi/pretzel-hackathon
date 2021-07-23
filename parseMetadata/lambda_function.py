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
    
    print(event)
    cur = conn.cursor()
    
    
    if event["action"] == "newmessage":
    
        # Read event payload
        id = event["id"]
        groupId = event["groupId"]
        messageCount = event["messageCount"]
        lastActiveTime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(event["lastActiveTime"]))
        
        # Check if user exists in db
        select_query = "Select * from {} where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, id, groupId)
        cur.execute(select_query)
        existing_user = cur.fetchone()
        
        # If user exists in db, append suggestions and update scores
        if existing_user is not None:
            print("User {} exists".format(existing_user[0]))
            update_query = "Update {} set messageCount = \"{}\", lastActiveTime = \"{}\" where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, messageCount, lastActiveTime, id, groupId)
            cur.execute(update_query)
        # If user does not exist, insert new record
        else:
            print("User not found!")
    
    elif event["action"] == "newgroup":
        # Read event payload
        ids = event["id"]
        groupId = event["groupId"]
        
        for id in ids:
            first_group = False
            select_query = "Select * from {} where id = \"{}\"".format(rds_table_name, id)
            cur.execute(select_query)
            
            existing_user = cur.fetchall()
            for row in existing_user:
                print(row)
                if row[3] == "No group":
                    print("updating" + id)
                    update_query = "update {} set groupId = \"{}\" where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, groupId, id, row[3])
                    print(update_query)
                    cur.execute(update_query)
                    first_group = True
                    break
            if not first_group:
                update_query = "Insert into {} (id, groupId) values(\"{}\",\"{}\")".format(rds_table_name, id, groupId)
                cur.execute(update_query)
        
    conn.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Record update successful, thank you!')
    }
    