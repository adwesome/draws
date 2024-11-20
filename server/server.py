import re
import json
import sqlite3
import secrets
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = 'adte.db'


def get_today_start_of_the_day_epoch():  # incorrect, but fine to go
  return int(datetime.datetime.combine(get_today_datetime(), datetime.time.min).timestamp())


def get_yesterday_start_of_the_day_epoch():  # incorrect, but fine to go
  return int(datetime.datetime.combine(get_today_datetime() - datetime.timedelta(days = 1), datetime.time.min).timestamp())


def get_today_epoch():
  # return int(get_today_datetime().timestamp())
  return int(get_today_datetime().timestamp())


def get_today_epoch2():
  # return int(get_today_datetime().timestamp())
  return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


def get_today_datetime():
  now = datetime.datetime.now(datetime.timezone.utc)
  return now - datetime.timedelta(hours = 1) - datetime.timedelta(minutes = 30)


def get_today_date():
  today = get_today_datetime()
  return str(today.date())


def get_yesterday_date():
  now = datetime.datetime.now(datetime.timezone.utc)
  yesterday = now - datetime.timedelta(hours = 1 + 24) - datetime.timedelta(minutes = 30)
  return str(yesterday.date())


def db_write(command):
  con = sqlite3.connect(DB_NAME)
  cur = con.cursor()
  print(command)
  res = cur.execute(command)
  con.commit()
  con.close()


def db_read(command):
  con = sqlite3.connect(DB_NAME)
  cur = con.cursor()
  print(command)
  res = cur.execute(command)
  result = res.fetchall()
  con.close()
  return result


def send_response(result):
  response = jsonify(result)
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  # response.headers.remove('Content-Type')
  # response.headers.add('Content-Type', 'text/css; charset=utf-8')  # to no-cors
  return response


def read_player(data):
  uid = int(data['uid'])
  query = "SELECT rowid, * FROM players WHERE uid = {uid}".format(uid = uid)
  return db_read(query)


def read_pid(data):
  player = read_player(data)
  if not player:
    return
  if not player[0]:
    return

  return player[0][0]


def convert_to_dict(data):
  data = json.loads(data)
  if not isinstance(data, dict):
    data = json.loads(data)
  return data

###
# REGISTER PLAYER AND SELECT BRANDS
###
def create_or_update_player(data):
  uid = int(data['uid'])
  player_exists = read_player(data)
  command = ""
  if not player_exists:
    date_created = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    command = "INSERT INTO players VALUES ({uid}, {date_created}, {region}, {city}, {sex}, {age}, {tguid})".format(
      uid = uid,
      date_created = date_created,
      region = int(data['demography']['region']),
      city = int(data['demography']['city']),
      sex = int(data['demography']['sex']),
      age = int(data['demography']['age']),
      tguid = int(data.get('tguid', 0)),
    )
  else:
    command = "UPDATE players SET region = {region}, city = {city}, sex = {sex}, age = {age} WHERE uid = {uid}".format(
      uid = uid,
      region = int(data['demography']['region']),
      city = int(data['demography']['city']),
      sex = int(data['demography']['sex']),
      age = int(data['demography']['age']),
    )
  db_write(command)


def create_or_update_player_brands(data):
  pid = read_pid(data)
  new_brands = data['brands']
  if not re.match(r'[\d+\,]+', new_brands):
    return

  query = "SELECT rowid FROM brands WHERE rowid IN ({new_brands})".format(new_brands = new_brands)
  allowed_brands = db_read(query)
  
  new_brands = ''
  for each_brand in allowed_brands:
    new_brands += each_brand[0]

  command = "UPDATE players SET bids = '{new_brands}' WHERE rowid = {pid}".format(
    pid = pid,
    new_brands = new_brands,
  )
  db_write(command)


@app.route('/register/player/demography', methods=['POST'])
def register_player_demography():
  data = convert_to_dict(request.data)
  create_or_update_player(data)
  result = {"code": 200}
  return send_response(result)


@app.route('/register/player/brands', methods=['POST'])
def register_player_brands():
  data = convert_to_dict(request.data)
  create_or_update_player_brands(data)
  result = {"code": 200}
  return send_response(result)


###
# REGISTER PLAYER PARTICIPATION
##
def get_status_by_chance(chance):
  coin = secrets.choice(range(1, 101))
  if coin <= int(chance):
    return 1  # win
  return 0  # not win


def get_chance_from_cam_by_cid(cid):
  query = "SELECT chance FROM cam WHERE rowid = {cid}".format(cid = cid)
  return db_read(query)[0][0]


def create_player_participation(data):
  pid = read_pid(data)
  cid = int(data['cid'])
  if check_if_pid_participates_in_cid(pid, cid):  # do not duplicate records
    return
  if not pid or not cid:
    return
  chance = get_chance_from_cam_by_cid(cid)
  status = get_status_by_chance(chance)
  gift = ''
  if status == 1:
    gift = 'https://card.digift.ru/card/show/code/bb898d955afe898e5596abd0311e5b49'
  date_now = get_today_epoch()
  command = "INSERT INTO par VALUES ({cid}, {pid}, {status}, {date_now}, '{gift}')".format(cid = cid, pid = pid, date_now = date_now, status = status, gift = gift)
  db_write(command)


def check_if_pid_participates_in_cid(pid, cid):
  if not pid or not cid:
    return False

  command = "SELECT * FROM par WHERE pid = {pid} AND cid = {cid}".format(pid = pid, cid = cid)
  participants = db_read(command)
  if not participants:
    return False
  return True


def check_if_pid_participates_today(pid):
  if not pid:
    return False

  date_now = get_today_datetime().date()
  date_start = int(datetime.datetime(date_now.year, date_now.month, date_now.day).timestamp())
  date_finish = int(datetime.datetime(date_now.year, date_now.month, date_now.day + 1).timestamp() - 1)
  # print(111)
  command = "SELECT c.rowid, c.ad, c.chance, o.name FROM par p JOIN cam c on p.cid = c.rowid JOIN orgs o ON o.rowid = c.oid WHERE p.pid = {pid} AND p.date >= {date_start} AND p.date < {date_finish}".format(pid = pid, date_start = date_start, date_finish = date_finish)
  return db_read(command)


def check_if_uid_participates_today(uid):
  pid = read_pid({'uid': uid})
  return check_if_pid_participates_today(pid)


@app.route('/register/player/participation', methods=['POST'])
def register_player_participation():
  data = convert_to_dict(request.data)
  create_player_participation(data)
  result = {"code": 200}
  return send_response(result)


@app.route('/get/player/participation', methods=['GET'])
def get_player_participation():
  uid = request.args.get('uid')
  # cid = request.args.get('cid')
  if uid:
    result = {"code": 200, "result": check_if_uid_participates_today(uid)}
  else:
    result = {"code": 400, "description": "UID and CID are required"}
  return send_response(result)

##
# CAMPAIGNS
##
def get_brands_for_me_for_today(pid):
  date_now = get_today_epoch2()
  query = "SELECT bids FROM players WHERE rowid = {pid}".format(pid = pid)
  bids = db_read(query)[0][0]
  if not bids:
    return

  query = "SELECT DISTINCT b.rowid, b.name FROM cam c \
          JOIN orgs o ON o.rowid = c.oid \
          JOIN brands b ON b.rowid = o.bid \
          WHERE 1=1 \
          AND c.rowid NOT IN (SELECT cid FROM par WHERE pid = {pid}) \
          AND b.rowid IN ({bids}) \
          and c.date_start <= {date_now} \
          and c.date_end > {date_now}".format(pid = pid, date_now = date_now, bids = bids)
  return db_read(query)


def get_campaigns_for_brand_and_pid_for_today(pid, bid):
  date_now = get_today_epoch2()
  query = "SELECT c.rowid, c.ad, c.chance, o.name FROM cam c \
          JOIN orgs o ON c.oid = o.rowid \
          WHERE 1=1 \
          and c.date_start <= {date_now} \
          and c.date_end > {date_now} \
          AND o.bid = {bid} \
          AND c.rowid NOT IN (SELECT cid FROM par WHERE pid = {pid})".format(pid = pid, bid = bid, date_now = date_now)
  return db_read(query)


@app.route('/get/campaign', methods=['GET'])
def get_campaigns_for_player():
  uid = request.args.get('uid')
  pid = read_pid({'uid': uid})
  
  brands = get_brands_for_me_for_today(pid)
  if not brands:
    result = {"code": 404, "description": "No ongoing campaign"}
    return send_response(result)

  # add brands weights here
  brand = secrets.choice(brands)
  bid = brand[0]
  campaigns = get_campaigns_for_brand_and_pid_for_today(pid, bid)
  print(pid, bid, campaigns)
  if not campaigns:
    result = {"code": 404, "description": "No ongoing campaign"}
    return send_response(result)
  campaign = secrets.choice(campaigns)
  if campaign:
    print(campaign)
    result = {"code": 200, "result": campaign}
  else:
    result = {"code": 404, "description": "No ongoing campaign"}
  return send_response(result)

##
# PARTICIPATION HISTORY
##
def get_campaigns_history_for_pid(pid):
  query = "SELECT c.rowid, c.ad, c.chance, b.name, p.status, p.date, p.gift FROM par p \
           JOIN cam c on p.cid = c.rowid \
           JOIN orgs o ON o.rowid = c.oid \
           JOIN brands b ON b.rowid = o.bid \
           WHERE p.pid = {pid} \
           ORDER BY p.date DESC".format(pid = pid)
  return db_read(query)


@app.route('/get/participation/history', methods=['GET'])
def get_participation_campaigns_for_player():
  uid = request.args.get('uid')
  pid = read_pid({'uid': uid})
  
  campaigns = get_campaigns_history_for_pid(pid)
  if campaigns:
    # CLEANUP ONGOING CAMPAIGN STATUS AND GIFT !
    result = {"code": 200, "result": campaigns}
  else:
    result = {"code": 404, "description": "No campaigns"}
  return send_response(result)

##
# Orgs poll again
##
@app.route('/orgs', methods=['POST'])
def submit_vote():
  data = json.loads(json.loads(request.data))
  # print(request.data, data)
  exists = db_read("SELECT * FROM voters WHERE uid = " + str(data['uid']))
  now = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000)
  orgs = ','.join(str(x) for x in data['orgs'])
  uid = data['uid']
  city = 0  # data['demography'][0]
  sex = 0  # data['demography'][1]
  age = 0  # data['demography'][2]
  comment = ''  # data['comment']
  if exists:
    command = "UPDATE voters SET date_last = {}, orgs = '{}' WHERE uid = {}".format(now, orgs, uid)
  else:
    command = "INSERT INTO voters VALUES ({}, {}, {}, {}, {}, {}, '{}', '{}')".format(uid, now, now, city, sex, age, comment, orgs)
  db_write(command)

  brands = []
  if (55 in data['orgs']):
    brands.append('lenta')
  if (107 in data['orgs']):
    brands.append('mk')
  data['brands'] = brands
  create_or_update_player_brands(data)
  result = {"code": 200}
  return send_response(result)

@app.route('/orgs/all', methods=['GET'])
def get_orgs():
  orgs = db_read("SELECT rowid, * FROM orgs ORDER BY address")
  result = {"code": 200, "orgs": orgs}
  return send_response(result)

##
# USER STATS
##
@app.route('/get/stats/players', methods=['GET'])
def get_stats_players():
  p_total = db_read("SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par)")
  today = get_today_start_of_the_day_epoch()
  query = "SELECT COUNT(*) FROM par WHERE status > 0 AND date < {today}".format(today = today)
  w_total = db_read(query)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par WHERE date >= {today})".format(today = today)
  p_today = db_read(query)
  yesterday = get_yesterday_start_of_the_day_epoch()
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par WHERE date >= {yesterday} AND date < {today})".format(today = today, yesterday = yesterday)
  p_yesterday = db_read(query)
  query = "SELECT COUNT(*) FROM par WHERE status > 0 AND date < {today} AND date > {yesterday}".format(today = today, yesterday = yesterday)
  w_yesterday = db_read(query)
  result = {"code": 200, "result": {"total": p_total, "total_winners": w_total, "today": p_today, "yesterday": p_yesterday, "yesterday_winners": w_yesterday}}
  return send_response(result)
