var SERVER_HOSTNAME = 'http://127.0.0.1:5000';
if (location.hostname)
  SERVER_HOSTNAME = 'https://scratchit.cards';

function choice(length) {
  return Math.floor(Math.random() * length);
}

function sleep(ms) {  // https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
  return new Promise(resolve => setTimeout(resolve, ms));
}

function today() {
  const date = new Date();
  if (date.getUTCHours() == 0 || (date.getUTCHours() == 1 && date.getUTCMinutes() < 30)) {
    date.setDate(date.getDate() - 1);
    return date.toISOString().split('T')[0];
  }
  else
    return date.toISOString().split('T')[0];
}
function tomorrow() {
  const date = new Date();
  if (date.getUTCHours() == 0 || (date.getUTCHours() == 1 && date.getUTCMinutes() < 30))
    return date.toISOString().split('T')[0];
  else {
    date.setDate(date.getDate() + 1);
    return date.toISOString().split('T')[0];
  }
}
function yesterday() {
  const date = new Date();
  if (date.getUTCHours() == 0 || (date.getUTCHours() == 1 && date.getUTCMinutes() < 30)) {
    date.setDate(date.getDate() - 2);
    return date.toISOString().split('T')[0];
  }
  else {
    date.setDate(date.getDate() - 1);
    return date.toISOString().split('T')[0];
  }
}

function save_into_local_storage(to, items) {
  localStorage.setItem(to, items);
}
function get_items_from_local_storage(from) {
  let links = localStorage.getItem(from) || "{}";
  return JSON.parse(links);
}
function get_item_from_local_storage(item) {
  return localStorage.getItem(item);
}

function set_existing_demography_choices() {
  var existing_choices = get_items_from_local_storage('choices5');
  if (Object.keys(existing_choices).length != 0) {  // pizdec
    ['region', 'city', 'sex', 'age'].forEach((item) => {
      const element = document.getElementById(item);
      element.value = existing_choices.demography[item];
      const event = new Event('change');
      element.dispatchEvent(event);
    });
    return;
  }

  /*
  // load possible data from poll
  existing_choices = get_items_from_local_storage('choises2');
  if (Object.keys(existing_choices).length == 0)  // pizdec
    return;

  document.getElementById(`sex`).value = existing_choices.demography[1];
  document.getElementById(`age`).value = existing_choices.demography[2];
  */
}

function set_existing_brands_choices() {
  var existing_choices = get_items_from_local_storage('choices4');
  if (Object.keys(existing_choices).length != 0) {  // pizdec
    ['107', '55'].forEach((item) => {
      const element = document.getElementById('brand-' + item);
      if (existing_choices.brands.includes(parseInt(item))) {
        element.style.filter == 'unset';
        const event = new Event('click');
        element.dispatchEvent(event);
      }
    });
  }
}

async function save_into_remote_storage(to, data) {
  const response = await fetch(SERVER_HOSTNAME + to, {
    mode: 'no-cors',
    method: 'POST',
    headers: {
      'Accept': 'text/plain',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return await response;
  //console.log(data);
}

/*
async function get_orgs() {
  const response = await fetch(SERVER_HOSTNAME + '/orgs/all', {});
  return await response.json();
}
*/

async function collect_demography_data_from_form() {
  let d = {};
  document.querySelectorAll('select').forEach((el) => {
    d[el.id] = parseInt(el.value);
  });

  const r = {'uid': uid, 'demography': d}
  tguid = get_tguid_from_url();
  if (tguid)
    r['tguid'] = tguid;

  const result = JSON.stringify(r);
  save_into_local_storage('choices3', result);
  return await save_into_remote_storage('/register/player/demography', result);
}

async function collect_brands_data_from_form() {
  const brands = [];
  document.querySelectorAll('img').forEach((el) => {
    if (el.style.filter == 'unset') {
      const bid = parseInt(el.classList.value.replace('brand', '').replace('bid-', '').trim());
      brands.push(bid);
    }
  });

  const result = JSON.stringify({'uid': uid, 'brands': brands});
  save_into_local_storage('choices4', result);
  return await save_into_remote_storage('/register/player/brands', result);
}

async function get_uid(tguid) {
  //var uid = localStorage.getItem('uid');
  //if (uid)
  //  return parseInt(uid);

  const response = await fetch(SERVER_HOSTNAME + `/get/uid?tguid=${tguid}`, {});
  var data = await response.json();
  if (data.code == 200) {
    localStorage.setItem('uid', data.uid);
    return data.uid;
  }

  uid = Date.now();
  localStorage.setItem('uid', uid);
  return uid;
}

function get_tguid_from_url() {  // https://www.sitepoint.com/get-url-parameters-with-javascript/
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  const id = urlParams.get('a');
  if (!id)
    return -1
  return parseInt(id);
}
