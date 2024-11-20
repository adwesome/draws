import sqlite3
DB_NAME = 'adte.db'

import datetime

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

def db_write(command):
  # print(command)
  res = cur.execute(command)
  con.commit()
  # con.close()


def db_read(command):
  # print(command)
  res = cur.execute(command)
  result = res.fetchall()
  return result


query = "SELECT p.rowid, v.orgs FROM voters v JOIN players p ON v.uid = p.uid"
voters = db_read(query)

query = "SELECT * FROM playersbrands"
existing_pb = db_read(query)

for each_voter in voters:
  orgs = each_voter[1]
  if orgs:
    orgs = orgs.split(',')
  else:
    continue
  pid = each_voter[0]
  
  for each_org in orgs:
    skip = False
    for each_pb in existing_pb:
      pb_pid = each_pb[0]
      pb_bid = each_pb[1]
      if pb_pid == pid and pb_bid == each_org:
        skip = True
        break

    if not skip:
      command = "INSERT INTO playersbrands VALUES ({pid}, {bid})".format(
        pid = pid,
        bid = each_org,
      )
      db_write(command)

con.close()
