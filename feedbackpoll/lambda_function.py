import sys
import logging
import pymysql
import os
import json
 
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
    id = event["kerberosID"]
    groupId = event["chatID"]
    conversation_score = event["ratingQ1"]
    suggestion_score = event["ratingQ2"]
    exclusion = event["restriction"]
    suggestion = event["suggestion"]

    cur = conn.cursor()

    # Check if user exists in db
    select_query = "Select * from {} where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, id, groupId)
    cur.execute(select_query)
    existing_user = cur.fetchone()
    print(existing_user)

    # If user exists in db, append suggestions and update scores
    if existing_user is not None:
        print("User {} exists".format(existing_user[0]))
        if existing_user[6] is not None and existing_user[6] not in ("no", "na", "nothing", "NO", "NA", "NOTHING", "No", "Na", "Nothing", "none", "NONE", "None"):
            previous_sugg = existing_user[6]
            print("Previous suggestion: ", previous_sugg)
            suggestion = previous_sugg + ", "+ suggestion

        update_query = "Update {} set conversation_score = \"{}\", suggestion_score = \"{}\", suggestion = \"{}\" where id = \"{}\" and groupId = \"{}\"".format(rds_table_name, conversation_score, suggestion_score, suggestion, id, groupId)
        count = cur.execute(update_query)
    # If user does not exist, insert new record
    else:
        print("User not found!")
        insert_query = "Insert into {} (id, conversation_score, suggestion_score, groupId, suggestion) values (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\")".format(rds_table_name, id, conversation_score, suggestion_score, groupId, suggestion)
        count = cur.execute(insert_query)
    
    # If exclusion has been entered, increment their exclusionCount
    if exclusion != "":
        excl = [x.strip() for x in exclusion.split(',')]
        print("Excluding", excl)
        cur_exclusion = conn.cursor()

        for exclId in excl:
            exclusion_select = "Select exclusionCount from {} where id = \"{}\"".format(rds_table_name, exclId)
            cur_exclusion.execute(exclusion_select)
            temp = cur_exclusion.fetchone()
            update_exclusion_query = "Update {} set exclusionCount = \"{}\" where id = \"{}\"".format(rds_table_name, temp[0]+1, exclId)
            cur.execute(update_exclusion_query)


    conn.commit()
    return {
        'statusCode': 200,
        'body': json.dumps('Feedback successful for ' + id + ', thank you!')
    }
    