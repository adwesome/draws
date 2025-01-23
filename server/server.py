import re
import json
import sqlite3
import secrets
import datetime
from flask import Flask, request, jsonify
import random

app = Flask(__name__)
DB_NAME = 'adte.db'
TIMESTAMP_BEGINNING = 1732843800  # November 29, 2024 1:30:00 AM


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
  # temporary manual
  status = 0
  gift = ''
  date_now = get_today_epoch2()
  command = "INSERT INTO par VALUES ({cid}, {pid}, {status}, {date_now}, '{gift}', NULL, '')".format(cid = cid, pid = pid, date_now = date_now, status = status, gift = gift)
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
  command = "SELECT c.rowid, c.ad, c.chance, o.name FROM par p JOIN cam c on p.cid = c.rowid JOIN orgs o ON o.rowid = c.oid WHERE p.pid = {pid} AND p.created_at >= {date_start} ".format(pid = pid, date_start = date_start)
  # command += "AND p.created_at < {date_finish}".format(date_finish = date_finish)
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

  bids = []
  weights = []
  for each in brands:
    bids.append(each[0])
    if each[0] == 107:
      weights.append(3)
    else:
      weights.append(1)

  # add brands weights here
  # bid = secrets.choice(bids)
  bid = random.choices(bids, weights, k=1)[0]

  # if bid == 55 and (84 in bids):  # add new chance for pride
  #  bid = secrets.choice([55, 84])
  if bid == 55 and (107 in bids):  # add more chance for magnet
    bid = secrets.choice([55, 107])

  # not participated for pride, go on
  query = "SELECT count(*) FROM par WHERE cid = 32 AND pid = {}".format(pid)
  up = db_read(query)
  # print(up, bids, len(up) == 1, up[0][0] == 0, 84 in bids)
  if len(up) == 1 and up[0][0] == 0 and 84 in bids:
    bid = 84

  campaigns = get_campaigns_for_brand_and_pid_for_today(pid, bid)
  # print(pid, bid, campaigns)
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
  query = "SELECT c.rowid, c.ad, c.chance, b.name, p.status, p.created_at, p.gift, p.rowid FROM par p \
           JOIN cam c on p.cid = c.rowid \
           JOIN orgs o ON o.rowid = c.oid \
           JOIN brands b ON b.rowid = o.bid \
           WHERE p.pid = {pid} \
           ORDER BY p.created_at DESC".format(pid = pid)
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
    query = "DELETE FROM par WHERE pid = 2 and created_at >= 1732505317";
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
  orgs = db_read("SELECT rowid, * FROM orgs")
  result = {"code": 200, "orgs": orgs}
  return send_response(result)


@app.route('/votes/all', methods=['GET'])
def get_votes():
  votes = db_read("SELECT rowid, * FROM players WHERE tguid != -1 and bids != ''")
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
  query = "SELECT COUNT(*) FROM par WHERE status_system > 0 AND created_at < {today}".format(today = today)
  w_total = db_read(query)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par WHERE created_at >= {today})".format(today = today)
  p_today = db_read(query)
  yesterday = get_start_of_the_day_epoch(1)
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par WHERE created_at >= {yesterday} AND created_at < {today})".format(today = today, yesterday = yesterday)
  p_yesterday = db_read(query)
  query = "SELECT COUNT(*) FROM par WHERE status_system > 0 AND created_at < {today} AND created_at > {yesterday}".format(today = today, yesterday = yesterday)
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
  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par p WHERE p.created_at >= {offset_old} ".format(offset_old = offset_old)
  if days_offset_new is not None:
    offset_new = get_start_of_the_day_epoch(days_offset_new)
    query += "AND p.created_at < {offset_new} ".format(offset_new = offset_new)
  query += "AND created_at >= {} ".format(TIMESTAMP_BEGINNING)
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
  query += "AND cid IN (SELECT rowid FROM cam WHERE date_start >= {date_start} ".format(date_start = date_begin_9_dec)
  if bid != -1:
    query += "AND oid IN (SELECT rowid FROM orgs WHERE 1=1 AND bid = {bid}) ".format(bid = bid)
  query += "))"
  return db_read(query)


def calc_players_brand_today(bid, offset):  # check that optimal
  offset_old = get_start_of_the_day_epoch(offset)
  if offset:
    offset_new = get_start_of_the_day_epoch(offset - 1)

  query = "SELECT COUNT(*) FROM (SELECT DISTINCT pid FROM par p WHERE p.created_at >= {offset_old} ".format(offset_old = offset_old)
  if offset:
    query += "AND p.created_at < {offset_new} ".format(offset_new = offset_new)
  if bid != -1:
    query += "AND cid IN (SELECT rowid FROM cam WHERE oid IN (SELECT rowid FROM orgs WHERE bid = {bid}))".format(bid = bid)
  query += ")"
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
    query = "SELECT DISTINCT pid FROM par WHERE created_at >= {date_start} AND created_at < {date_end} ".format(date_start = date_start, date_end = date_end)
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
      query = "SELECT DISTINCT pid FROM par WHERE created_at >= {date_start2} AND created_at < {date_end2} ".format(date_start2 = date_start2, date_end2 = date_end2)
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


def get_participation_chart(bid):
  now = get_today_epoch2()
  result = {"business_days": [], "weekends": [], "today": [], "yesterday": [], "same_day_week_ago": []}
  for day in list(reversed(range(8))):
    midnight = get_start_of_the_day_epoch(day) - 4 * 3600 - 1800  # i don't understand this shift (but it affects chart)
    weekday = datetime.datetime.fromtimestamp(midnight).strftime("%A")  # https://stackoverflow.com/questions/26232658/python-convert-epoch-time-to-day-of-the-week
    r = []
    for hour in range(24):
      time_from = midnight + hour * 3600
      time_to = midnight + (hour + 1) * 3600 - 1
      query = "SELECT COUNT(*) FROM par WHERE 1=1 "
      if bid != -1:
        query += "AND cid IN (SELECT rowid FROM cam WHERE oid IN (SELECT rowid FROM orgs WHERE bid = {})) ".format(bid)
      query += "AND created_at BETWEEN {} AND {}".format(time_from, time_to)
      participants = db_read(query)
      r.append(participants[0][0])

      if time_to >= now:
        break

    if day == 0:
      result["today"].append(r)
    elif day == 1:
      result["yesterday"].append(r)
    elif day == 7:
      result["same_day_week_ago"].append(r)
    
    if day != 0:  # do not include today in stats
      if weekday in ['Saturday', 'Sunday']:
        result["weekends"].append(r)
      else:
        result["business_days"].append(r)

  # print(result)
  return result


@app.route('/get/control', methods=['GET'])
def get_control_data():
  query = "SELECT DISTINCT p.pid FROM par p WHERE p.created_at >= {} ".format(TIMESTAMP_BEGINNING)
  query += "UNION SELECT rowid FROM players WHERE rowid NOT IN (SELECT DISTINCT p.pid FROM par p WHERE p.created_at >= {}) AND tguid != -1".format(TIMESTAMP_BEGINNING)  # started bot but not participated
  pids_unique = db_read(query)

  bid = int(request.args.get('bid'))
  query = "SELECT COUNT(*) FROM players WHERE 1=1 "
  if bid != -1:
    query += "AND (bids LIKE '{bid},%' OR bids LIKE '%,{bid}' OR bids LIKE '%,{bid},%' OR bids = '{bid}') ".format(bid = bid)
  query += "AND rowid IN (SELECT DISTINCT pid FROM par WHERE created_at >= {}) ".format(TIMESTAMP_BEGINNING)
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
      # "players_quarter": calc_players(bid, 90)[0][0],
    },
    "campaign": {
      "par_total": calc_players_brand_total(bid),
      "par_today": calc_players_brand_today(bid, 0),
      "par_yesterday": calc_players_brand_today(bid, 1),
    },
    "cohorts": cohorts,
    "charts": {
      "participation": get_participation_chart(bid)
    }
  }
  return send_response(result)


##
# DRAWS CODES
##
def get_codes():
  #if tguid in [1731725782227, 1730926893589]:
  oid = 107

  query = "SELECT p.gift, p.status_system, p.comment, p.gifted_at from par p where 1=1 "
  query += "AND status_system >= 1 "
  query += "AND created_at >= 1733707800 "  # 9 Dec 2024
  query += "AND cid in (SELECT c.rowid from cam c WHERE c.oid = {}) ".format(oid)
  query += "AND gift NOT LIKE 'http%'"

  codes = db_read(query)
  return codes


@app.route('/get/draws/codes', methods=['GET'])
def get_draws_codes():
  # tguid = int(request.args.get('tguid'))
  codes = get_codes()
  return send_response(codes)


def check_code(code):
  print("SQL injection")
  query = "SELECT p.gift, p.status_system, p.comment, p.gifted_at from par p where 1=1 "
  query += "AND gift = '{}'".format(code)
  return db_read(query)


@app.route('/draws/code/check', methods=['GET'])
def draws_code_check():
  code = request.args.get('code')
  result = check_code(code)
  if not result:
    return send_response({'code': 404, 'result': []})
  return send_response({'code': 200, 'result': result})


def update_code(data):
  print("SQL injection")
  oid = 107
  code = data['code']
  comment = data.get('comment', '').strip()
  date_now = get_today_epoch2()
  query = "UPDATE par SET status_system = 2, comment = '{}', gifted_at = {} WHERE gift = '{}' ".format(comment, date_now, code)
  query += "AND cid IN (SELECT c.rowid from cam c WHERE c.oid = {})".format(oid)
  return db_write(query)


@app.route('/draws/code/update', methods=['POST'])
def draws_code_update():
  data = convert_to_dict(request.data)
  update_code(data)
  return send_response({'code': 200})


def get_comments(oid):
  query = "SELECT DISTINCT comment FROM par p WHERE cid IN (SELECT rowid FROM cam WHERE oid = {}) AND status = 2 AND comment != '' ORDER BY 1".format(oid)
  return db_read(query)


@app.route('/get/draws/codes/comments', methods=['GET'])
def draws_codes_comments():
  oid = 107
  return send_response({'code': 200, 'result': get_comments(oid)})


def update_code_status(data):
  rowid = int(data[0])
  status = int(data[1])
  query = "UPDATE par SET status = {} WHERE rowid = {}".format(status, rowid)
  db_write(query)


@app.route('/draws/codes/feedback', methods=['POST'])
def draws_codes_feedback():
  data = convert_to_dict(request.data)
  update_code_status(data)
  return send_response({'code': 200})
