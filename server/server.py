import re
import json
import sqlite3
import secrets
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = 'adte.db'
TIMESTAMP_BEGINNING = 1732843800


def get_start_of_the_day_epoch(days_offset):  # incorrect, but fine to go
  today = datetime.datetime.combine(get_today_datetime(), datetime.time.min, tzinfo=datetime.timezone.utc)
  today_shifted = today - datetime.timedelta(days = days_offset) + datetime.timedelta(hours = 1) + datetime.timedelta(minutes = 30)
  return int(today_shifted.timestamp())


def get_today_epoch():
  # return int(get_today_datetime().timestamp())
  return int(get_today_datetime().timestamp())


def get_today_epoch2():  #fix this
  # return int(get_today_datetime().timestamp())
  return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


def get_today_datetime():
  now = datetime.datetime.now(datetime.timezone.utc)
  return now - datetime.timedelta(hours = 1) - datetime.timedelta(minutes = 30)


def get_tomorrow_datetime():
  return get_today_datetime()  + datetime.timedelta(days = 1)


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
def create_player(tguid, mc = None):
  bids = '55,107'  # lenta and mc
  mc_sql = 'NULL'
  if mc == 'mcg':
    bids = '107'  # mc group
    mc_sql = "'" + mc + "'"

  uid = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)  # ms
  date_created = int(uid / 1000)
  command = "INSERT INTO players VALUES ({uid}, {date_created}, {region}, {city}, {sex}, {age}, {tguid}, '{bids}', NULL, {mc})".format(
    uid = uid,
    date_created = date_created,
    region = -1,
    city = -1,
    sex = -1,
    age = -1,
    tguid = tguid,
    bids = bids,
    # churned_since = None,
    mc = mc_sql,
  )
  db_write(command)
  return uid


def update_player(data):
  command = ""
  uid = int(data['uid'])
  bids = data.get('brands', '')
  command = "UPDATE players SET region = {region}, city = {city}, sex = {sex}, age = {age} ".format(
    region = int(data['demography']['region']),
    city = int(data['demography']['city']),
    sex = int(data['demography']['sex']),
    age = int(data['demography']['age']),
  )
  if bids:
    if not re.match(r'[\d+\,]+', bids) and bids != '':
      return
    command += ", bids = '{bids}' ".format(bids = bids)

  command += "WHERE uid = {uid}".format(uid = uid)
  db_write(command)


def create_or_update_player_brands(data):
  pid = read_pid(data)
  new_brands = json.dumps(data['brands'])[1:-1]
  if not re.match(r'[\d+\,]+', new_brands):
    return

  query = "SELECT rowid FROM brands WHERE rowid IN ({new_brands})".format(new_brands = new_brands)
  allowed_brands = db_read(query)
  
  bids = []
  for bid in allowed_brands:
    bids.append(str(bid[0]))
  bids = ','.join(bids)

  command = "UPDATE players SET bids = '{bids}' WHERE rowid = {pid}".format(
    pid = pid,
    bids = bids,
  )
  db_write(command)


@app.route('/register/player/demography', methods=['POST'])
def register_player_demography():
  data = convert_to_dict(request.data)
  update_player(data)
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


def create_player_participation(data):  # fix this get_today_epoch2
  pid = read_pid(data)
  cid = int(data['cid'])
  if not pid or not cid:
    return
  if check_if_pid_participates_in_non_repeatable_cid(pid, cid):
    return
  chance = get_chance_from_cam_by_cid(cid)
  status = get_status_by_chance(chance)
  gift = ''
  if status == 1:
    gift = 'https://card.digift.ru/card/show/code/bb898d955afe898e5596abd0311e5b49'
  # temporary manual
  status = 0
  gift = ''
  date_now = get_today_epoch2()
  command = "INSERT INTO par VALUES ({cid}, {pid}, {status}, {date_now}, '{gift}')".format(cid = cid, pid = pid, date_now = date_now, status = status, gift = gift)
  db_write(command)


def check_if_pid_participates_in_non_repeatable_cid(pid, cid):
  # type = 0 - non-repeatable, 1 - repeatable
  command = "SELECT * FROM par WHERE pid = {pid} AND cid IN (SELECT rowid FROM cam WHERE rowid = {cid} AND type = 0)".format(pid = pid, cid = cid)
  participants = db_read(command)
  if not participants:
    return False
  return True


def check_if_pid_participates_today(pid):
  date_now = get_today_datetime().date()
  date_start = int(datetime.datetime(date_now.year, date_now.month, date_now.day).timestamp()) + 1 * 3600 + 1800
  # date_finish = date_start + 86400 - 1  # UTC bug hidden by this comment: I register in UTC but check participation in UTC+1.5, need to fix participation time and then fix this code
  # print(get_today_datetime(), date_start, datetime.datetime.utcfromtimestamp(date_start).strftime('%Y-%m-%d %H:%M:%S'))
  # print(date_finish, datetime.datetime.utcfromtimestamp(date_finish).strftime('%Y-%m-%d %H:%M:%S'))
  command = "SELECT c.rowid, c.ad, c.chance, o.name FROM par p JOIN cam c on p.cid = c.rowid JOIN orgs o ON o.rowid = c.oid WHERE p.pid = {pid} AND p.date >= {date_start} ".format(pid = pid, date_start = date_start)
  # command += "AND p.date < {date_finish}".format(date_finish = date_finish)
  return db_read(command)


@app.route('/register/player/participation', methods=['POST'])
def register_player_participation():
  data = convert_to_dict(request.data)
  create_player_participation(data)
  result = {"code": 200}
  return send_response(result)


def get_uid_by_tguid(tguid):
  query = "SELECT uid FROM players WHERE tguid = {}".format(tguid)
  uid = db_read(query)
  if not uid:
    return;
  return uid[0][0]


@app.route('/get/player/participation', methods=['GET'])
def get_player_participation():
  uid = request.args.get('uid')
  if not uid:
    result = {"code": 400, "description": "UID is required"}
    return send_response(result)

  pid = read_pid({'uid': uid})
  if not pid:
    tguid = request.args.get('tguid')
    result = {"code": 205, "description": "Reset content", "uid": get_uid_by_tguid(tguid)}
    return send_response(result)

  result = {"code": 200, "result": check_if_pid_participates_today(pid)}
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
          AND c.rowid NOT IN (\
            SELECT p.cid FROM par p JOIN cam c ON c.rowid = p.cid WHERE c.type = 0 AND p.pid = {pid}\
          ) ".format(pid = pid)
  
  query += "AND b.rowid IN ({bids}) ".format(bids = bids)
  query += "AND c.date_start <= {date_now} \
            AND c.date_end > {date_now} ".format(date_now = date_now)
  return db_read(query)


def get_campaigns_for_brand_and_pid_for_today(pid, bid):
  date_now = get_today_epoch2()
  query = "SELECT c.rowid, c.ad, c.chance, o.name FROM cam c \
          JOIN orgs o ON c.oid = o.rowid \
          WHERE 1=1 \
          and c.date_start <= {date_now} \
          and c.date_end > {date_now} \
          AND o.bid = {bid} \
          AND c.rowid NOT IN (\
            SELECT p.cid FROM par p JOIN cam c ON c.rowid = p.cid WHERE c.type = 0 AND p.pid = {pid}\
          )".format(pid = pid, bid = bid, date_now = date_now)
  return db_read(query)


@app.route('/get/campaign', methods=['GET'])
def get_campaigns_for_player():
  uid = request.args.get('uid')
  pid = read_pid({'uid': uid})
  if not pid:
    result = {"code": 205, "description": "Reset content"}
    return send_response(result)

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

  """
  # demo
  if pid == 2:
    query = "DELETE FROM par WHERE pid = 2 and date >= 1732505317";
    db_write(query)
  """
  return send_response(result)


##
# Orgs poll again
##
@app.route('/orgs', methods=['POST'])
def submit_vote():
  data = convert_to_dict(request.data)
  pid = read_pid(data)
  if not pid:
    return

  now = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000)
  uid = data['uid']
  region = data['demography'][0]
  if region == 10:
    city = data['demography'][1]
  else:
    city = -1
  sex = data['demography'][2]
  age = data['demography'][3]
  # tguid = int(data['tguid'])
  bids = json.dumps(data['brands'])[1:-1]  # cut braces
  bids = bids.replace(' ', '')
  if not re.match(r'[\d+\,]+', bids) and bids != '':
    return

  command = "UPDATE players SET region = {}, city = {}, sex = {}, age = {}, bids = '{}' WHERE rowid = {}".format(region, city, sex, age, bids, pid)
  db_write(command)
  result = {"code": 200}
  return send_response(result)


@app.route('/orgs/all', methods=['GET'])
def get_orgs():
  orgs = db_read("SELECT rowid, * FROM orgs ORDER BY address")
  result = {"code": 200, "orgs": orgs}
  return send_response(result)


@app.route('/votes/all', methods=['GET'])
def get_votes():
  votes = db_read("SELECT rowid, * FROM players WHERE bids != ''")
  result = {"code": 200, "votes": votes}
  return send_response(result)


@app.route('/get/uid', methods=['GET'])
def get_uid():
  tguid = request.args.get('tguid')
  query = "SELECT uid, churned_since FROM players WHERE tguid = {}".format(tguid)
  uid = db_read(query)
  if not uid:
    result = {"code": 200, "uid": create_player(tguid)}
  else:
    if uid[0][1]:  # if was churned, then unblock to allow notifications
      query = "UPDATE players SET churned_since = NULL WHERE uid = {}".format(uid[0][0])
      db_write(query)
    result = {"code": 200, "uid": uid[0][0]}

  return send_response(result)


@app.route('/get/player/choices', methods=['GET'])
def get_player_choices():
  uid = request.args.get('uid')
  player = read_player({'uid': uid})
  bids = []
  if player[0][8]:
    bids = list(map(int, re.sub(r'^,', '', player[0][8]).split(',')))  # https://stackoverflow.com/questions/6429638/how-to-split-a-string-of-space-separated-numbers-into-integers
  result = {"code": 200, "result": {
    "demography": {
      "region": player[0][3],
      "city": player[0][4],
      "sex": player[0][5],
      "age": player[0][6],
    }, 
    "brands": bids
    }
  }
  return send_response(result)


##
# USER STATS
##
@app.route('/get/stats/players', methods=['GET'])
def get_stats_players():
  p_total = db_read("SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par)")
  today = get_start_of_the_day_epoch(0)
  query = "SELECT COUNT(*) FROM par WHERE status > 0 AND date < {today}".format(today = today)
  w_total = db_read(query)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par WHERE date >= {today})".format(today = today)
  p_today = db_read(query)
  yesterday = get_start_of_the_day_epoch(1)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par WHERE date >= {yesterday} AND date < {today})".format(today = today, yesterday = yesterday)
  p_yesterday = db_read(query)
  query = "SELECT COUNT(*) FROM par WHERE status > 0 AND date < {today} AND date > {yesterday}".format(today = today, yesterday = yesterday)
  w_yesterday = db_read(query)
  result = {"code": 200, "result": {"total": p_total, "total_winners": w_total, "today": p_today, "yesterday": p_yesterday, "yesterday_winners": w_yesterday}}
  return send_response(result)


######### ORGS
##
# CAM CONTROL
##
def calc_players(bid, days_offset_old, days_offset_new = None):
  print(days_offset_old, days_offset_new)
  offset_old = get_start_of_the_day_epoch(days_offset_old)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par p WHERE p.date >= {offset_old} ".format(offset_old = offset_old)
  if days_offset_new is not None:
    offset_new = get_start_of_the_day_epoch(days_offset_new)
    query += "AND p.date < {offset_new} ".format(offset_new = offset_new)
  query += "AND date >= {} ".format(TIMESTAMP_BEGINNING)
  query += "AND pid IN ("
  query += "SELECT rowid FROM players p WHERE 1=1 "
  query += "AND churned_since IS NULL "
  if bid != -1:
    query += "AND p.bids LIKE '%,{bid},%' OR p.bids LIKE '{bid},%' OR p.bids LIKE '%,{bid}'".format(bid = bid)
  query += "))"
  return db_read(query)


def calc_players_brand_total(bid):
  date_begin_9_dec = 1733707800
  # offset_old = get_start_of_the_day_epoch(0)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par p WHERE 1=1 "
  query += "AND cid IN (SELECT rowid FROM cam WHERE date_start >= {date_start} AND oid IN (SELECT rowid FROM orgs WHERE bid = {bid})))".format(bid = bid, date_start = date_begin_9_dec)
  return db_read(query)


def calc_players_brand_today(bid, offset):  # check that optimal
  offset_old = get_start_of_the_day_epoch(offset)
  if offset:
    offset_new = get_start_of_the_day_epoch(offset - 1)

  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par p WHERE p.date >= {offset_old} ".format(offset_old = offset_old)
  if offset:
    query += "AND p.date < {offset_new} ".format(offset_new = offset_new)
  query += "AND cid IN (SELECT rowid FROM cam WHERE oid IN (SELECT rowid FROM orgs WHERE bid = {bid})))".format(bid = bid)
  return db_read(query)


def get_values_from_query(query_result):
  result = []
  for each in query_result:
    result.append(each[0])
  return result


def get_cohorts(bid):
  date_final = get_start_of_the_day_epoch(0)
  step = 86400
  date_start = TIMESTAMP_BEGINNING
  cohorts = []
  pids_existing = []
  while date_start < date_final + step:
    date_end = date_start + step
    query = "SELECT DISTINCT pid FROM par WHERE date >= {date_start} AND date < {date_end} ".format(date_start = date_start, date_end = date_end)
    query += "AND pid NOT IN ({}) ".format(','.join(map(str, pids_existing)))
    if bid != -1:
      query += "AND pid IN (SELECT rowid FROM players WHERE bids LIKE '{bid},%' OR bids LIKE '%,{bid}' OR bids LIKE '%,{bid},%' OR bids = '{bid}') ".format(bid = bid)
    # query += "AND pid NOT IN (SELECT rowid FROM players WHERE churned_since IS NOT NULL) "
    q = db_read(query)
    pids = get_values_from_query(q)

    new_pids = []
    for pid in pids:
      if pid not in pids_existing:
        new_pids.append(pid)

    cohort = []
    date_start2 = date_start
    while date_start2 < date_final + step:
      date_end2 = date_start2 + step
      query = "SELECT DISTINCT pid FROM par WHERE date >= {date_start2} AND date < {date_end2} ".format(date_start2 = date_start2, date_end2 = date_end2)
      query += "AND pid in ({}) ".format(','.join(map(str, new_pids)))
      if bid != -1:
        query += "AND pid IN (SELECT rowid FROM players WHERE bids LIKE '{bid},%' OR bids LIKE '%,{bid}' OR bids LIKE '%,{bid},%' OR bids = '{bid}') ".format(bid = bid)
      # query += "AND pid NOT IN (SELECT rowid FROM players WHERE churned_since IS NOT NULL) "
      q = db_read(query)
      pids2 = get_values_from_query(q)
      cohort.append(len(pids2))
      date_start2 = date_end2

    cohorts.append(cohort)
    pids_existing = pids_existing + pids
    date_start = date_end

  return cohorts


def calc_churned():
  query = "SELECT COUNT(*) FROM players WHERE churned_since IS NOT NULL"
  return db_read(query)[0]


@app.route('/get/control', methods=['GET'])
def get_control_data():
  query = "SELECT DISTINCT pid FROM par WHERE date >= {}".format(TIMESTAMP_BEGINNING)
  pids_unique = db_read(query)

  bid = int(request.args.get('bid'))
  query = "SELECT COUNT(*) FROM players WHERE 1=1 "
  if bid != -1:
    query += "AND (bids LIKE '{bid},%' OR bids LIKE '%,{bid}' OR bids LIKE '%,{bid},%' OR bids = '{bid}') ".format(bid = bid)
  query += "AND rowid IN (SELECT DISTINCT pid FROM par WHERE date >= {}) ".format(TIMESTAMP_BEGINNING)
  query += "AND churned_since IS NULL "
  players_brand = db_read(query)

  cohorts = get_cohorts(bid)
  players_total = len(pids_unique)
  players_churned = calc_churned()[0]
  players_total_active = players_total - players_churned
  result = {"code": 200, "audience": {
      "players_total": players_total,
      "players_churned": players_churned,
      "players_total_active": players_total_active,
      "players_brand": players_brand[0][0],
      "players_today": calc_players(bid, 0)[0][0],
      "players_yesterday": calc_players(bid, 1, 0)[0][0],
      "players_day_before_yesterday": calc_players(bid, 2, 1)[0][0],
      "players_week": calc_players(bid, 7)[0][0],
      "players_month": calc_players(bid, 30)[0][0],
      "players_quarter": calc_players(bid, 90)[0][0],
    },
    "campaign": {
      "par_total": calc_players_brand_total(bid),
      "par_today": calc_players_brand_today(bid, 0),
      "par_yesterday": calc_players_brand_today(bid, 1),
    },
    "cohorts": cohorts
  }
  return send_response(result)
