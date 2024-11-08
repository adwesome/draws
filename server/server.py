import json
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = 'adte.db'

import datetime

def get_today_date():
  now = datetime.datetime.now(datetime.timezone.utc)
  today = now - datetime.timedelta(hours = 1) - datetime.timedelta(minutes = 30)
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

DB_INIT_COMMANDS = [
  """
  CREATE TABLE IF NOT EXISTS participants(uid, cid);
  CREATE TABLE IF NOT EXISTS winners(cid, uid);
  CREATE TABLE IF NOT EXISTS campaigns (cid, date_go, ad, who, percent, prize);

  CREATE TABLE IF NOT EXISTS players (uid INTEGER, date_created INTEGER, region INTEGER, city INTEGER, sex INTEGER, age INTEGER, tguid INTEGER);
  CREATE TABLE IF NOT EXISTS brands (name TEXT);
  CREATE TABLE IF NOT EXISTS playersbrands (pid INTEGER, bid INTEGER);
  INSERT INTO brands VALUES ('mk');
  INSERT INTO brands VALUES ('lenta');
  
  CREATE TABLE IF NOT EXISTS org (name TEXT, bid INTEGER);
  INSERT INTO org VALUES ('Магнит Косметик', 1);
  INSERT INTO org VALUES ('Лента', 2);
  CREATE TABLE IF NOT EXISTS cam (oid INTEGER, date_start INTEGER, date_end INTEGER, ad TEXT, winners INTEGER);
  INSERT INTO cam VALUES (1, 0, 0, '/img/ad-mk.jpg', 3);
  INSERT INTO cam VALUES (2, 0, 0, '/img/ad-lenta.jpg', 3);
  CREATE TABLE IF NOT EXISTS par (cid INTEGER, pid INTEGER, status INTEGER);
  """
]
for each_command in DB_INIT_COMMANDS:
  try:
    db_write(each_command)
  except Exception as why:
    print(str(why))


def db_read(command):
  con = sqlite3.connect(DB_NAME)
  cur = con.cursor()
  print(command)
  res = cur.execute(command)
  result = res.fetchall()
  con.close()
  return result


def already_participates_today(uid, cid):
  command = "SELECT * FROM participants WHERE uid = {uid} AND cid = {cid}".format(uid = uid, cid = cid)
  participants = db_read(command)
  print(participants)
  if not participants:
    return False
  return True


def submit_new_participant(uid, cid):
  command = "INSERT INTO participants VALUES ({uid}, {cid})".format(uid = uid, cid = cid)
  db_write(command)


@app.route('/participants', methods=['GET'])
def get_uid():
  uid = request.args.get('uid')
  cid = request.args.get('cid')
  if uid and cid:
    result = {"code": 200, "result": already_participates_today(uid, cid)}
  else:
    result = {"code": 400, "description": "UID and CID are required"}
  return send_response(result)

@app.route('/participants/all', methods=['GET'])
def get_all_participants():
  participants = db_read("SELECT * FROM participants ORDER BY cid DESC")
  result = {}
  previous_cid = participants[0][0]
  for each in participants:
    cid = each[1]
    uid = each[0]
    if cid in result:
      result[cid].append(uid)
    else:
      result[cid] = [uid]

  return send_response({"code": 200, "result": result})


@app.route('/participants', methods=['POST'])
def post_uid():
  data = json.loads(request.data)
  if data['uid'] != -1 and data.get('cid'):
    submit_new_participant(data['uid'], data['cid'])
    result = {"code": 200}
  else:
    result = {"code": 400, "description": "UID is required"}
  return send_response(result)


def get_campaigns_by_date(date_go):
  command = "SELECT ad, cid, who, percent, prize, date_go FROM campaigns "
  if date_go:
    command += "WHERE date_go = '{date_go}' ".format(date_go = date_go)
  command += "ORDER BY cid DESC"
  campaigns = db_read(command)
  print(campaigns)
  return campaigns

def get_winners_by_cid(cid):
  command = "SELECT uid FROM winners WHERE cid = {cid}".format(cid = cid)
  winners = db_read(command)
  print(winners)
  if not winners:
    return []
  return winners

def get_participants_by_cid(cid):
  command = "SELECT uid FROM participants WHERE cid = {cid}".format(cid = cid)
  participants = db_read(command)
  print(participants)
  if not participants:
    return []
  return participants

def get_percent_by_cid(cid):
  command = "SELECT percent FROM campaigns WHERE cid = {cid}".format(cid = cid)
  percent = db_read(command)
  print(percent)
  if not percent:
    return 0
  return percent[0][0]


import random, math, secrets

def get_sample_from_list(participants, percent):
  print(participants, percent)
  number = math.floor(len(participants) * int(percent) / 100)
  # temp stub ignore percent
  if not participants:
    return []
  number = 1
  random.shuffle(participants)
  participants = participants * 5
  random.shuffle(participants)
  participants = participants * 2
  random.shuffle(participants)

  result = []
  for i in range(number):
    result.append(secrets.choice(participants))
  # return random.sample(participants, number)
  return result


def calculate_winners_for_campaign(cid):  # https://www.geeksforgeeks.org/randomly-select-elements-from-list-without-repetition-in-python/
  participants = get_participants_by_cid(cid)
  percent = get_percent_by_cid(cid)
  return get_sample_from_list(participants, percent)

def save_winners_for_cid(winners, cid):
  for each in winners:
    command = "INSERT INTO winners VALUES ({cid}, {uid})".format(cid = cid, uid = each[0])
    db_write(command)


@app.route('/winners', methods=['GET'])
def get_winners_and_calculate_em_if_needed():
  date_go = get_yesterday_date()
  campaigns = get_campaigns_by_date(date_go)
  if not campaigns:
    return []
  
  cid = campaigns[0][1]
  winners = get_winners_by_cid(cid)
  print(winners)
  if not winners:
    winners = calculate_winners_for_campaign(cid)
    print(cid, winners)
    save_winners_for_cid(winners, cid)
  # print(winners)

  result = []
  for each in winners:
    result.append(each[0])

  return send_response({"code": 200, "result": result})


@app.route('/winners/all', methods=['GET'])
def get_all_winners():
  winners = db_read("SELECT * FROM winners ORDER BY cid DESC")
  result = {}
  previous_cid = winners[0][0]
  for each in winners:
    cid = each[0]
    uid = each[1]
    if cid in result:
      result[cid].append(uid)
    else:
      result[cid] = [uid]

  return send_response({"code": 200, "result": result})


@app.route('/campaigns/all', methods=['GET'])
def get_campaigns():
  get_winners_and_calculate_em_if_needed()  # temp
  campaigns = get_campaigns_by_date(None)
  if campaigns:
    result = {"code": 200, "result": campaigns}
  else:
    result = {"code": 404, "description": "No ongoing campaigns"}
  return send_response(result)



"""
@app.route('/orgs', methods=['POST'])
def submit_vote():
  data = json.loads(json.loads(request.data))
  # print(request.data, data)
  exists = db_read("SELECT * FROM voters WHERE uid = " + str(data['uid']))
  now = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp() * 1000)
  orgs = ','.join(str(x) for x in data['orgs'])
  uid = data['uid']
  city = data['demography'][0]
  sex = data['demography'][1]
  age = data['demography'][2]
  comment = data['comment']
  if exists:
    command = "UPDATE voters SET date_last = {}, city = {}, sex = {}, age = {}, orgs = '{}', comment = '{}' WHERE uid = {}".format(now, city, sex, age, orgs, comment, uid)
  else:
    command = "INSERT INTO voters VALUES ({}, {}, {}, {}, {}, {}, '{}', '{}')".format(uid, now, now, city, sex, age, comment, orgs)
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
  votes = db_read("SELECT rowid, * FROM voters")
  result = {"code": 200, "votes": votes}
  return send_response(result)
"""

def send_response(result):
  response = jsonify(result)
  response.headers.add('Access-Control-Allow-Origin', '*')
  # response.headers.remove('Content-Type')
  # response.headers.add('Content-Type', 'text/css; charset=utf-8')  # to no-cors
  return response

def read_player(data):
  uid = int(data['uid'])
  query = "SELECT rowid, * FROM players WHERE uid = {uid}".format(uid = uid)
  return db_read(query)

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
  pid = read_player(data)[0][0]
  query = "DELETE FROM playersbrands WHERE pid = {pid}".format(pid = pid)
  db_write(query)

  query = "SELECT name FROM brands"
  brands = db_read(query)
  available_brands_names = []
  for each in brands:
    available_brands_names.append(each[0])
  
  for brand_name in data['brands']:
    if brand_name not in available_brands_names:
      print(brand_name, 'is not in:', available_brands_names)
      continue

    query = "SELECT rowid, * FROM brands WHERE name = '{brand_name}'".format(brand_name = brand_name)
    brand = db_read(query)[0]
    bid = brand[0]

    command = "INSERT INTO playersbrands VALUES ({pid}, {bid})".format(
      pid = pid,
      bid = bid,
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
def create_player_participation(data):
  pid = read_player(data)[0][0]
  cid = int(data['cid'])
  command = "INSERT INTO par VALUES ({cid}, {pid}, 0)".format(cid = cid, pid = pid)
  db_write(command)

@app.route('/register/player/participation', methods=['POST'])
def register_player_participation():
  data = convert_to_dict(request.data)
  create_player_participation(data)
  result = {"code": 200}
  return send_response(result)
