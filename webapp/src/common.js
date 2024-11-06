var SERVER_HOSTNAME = 'http://127.0.0.1:5000';
if (location.hostname)
  SERVER_HOSTNAME = 'https://scratchit.cards';


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

function set_existing_choices() {
  var existing_choices = get_items_from_local_storage('choices3');
  if (Object.keys(existing_choices).length != 0) {  // pizdec
    ['region', 'city', 'sex', 'age'].forEach((item) => {
      const element = document.getElementById(item);
      element.value = existing_choices.demography[item];
      const event = new Event('change');
      element.dispatchEvent(event);
    });
    return;
  }

  // load possible data from poll
  existing_choices = get_items_from_local_storage('choises2');
  if (Object.keys(existing_choices).length == 0)  // pizdec
    return;

  document.getElementById(`sex`).value = existing_choices.demography[1];
  document.getElementById(`age`).value = existing_choices.demography[2];
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

async function get_orgs() {
  const response = await fetch(SERVER_HOSTNAME + '/orgs/all', {});
  return await response.json();
}

async function collect_demography_data_from_form() {
  let d = {};
  document.querySelectorAll('select').forEach((el) => {
    d[el.id] = parseInt(el.value);
  });

  const result = JSON.stringify({'uid': get_uid(), 'demography': d});
  save_into_local_storage('choices3', result);
  return await save_into_remote_storage('/register/player/demography', result);
}

async function collect_brands_data_from_form() {
  const brands = [];
  document.querySelectorAll('img').forEach((el) => {
    if (el.style.filter == 'unset')
      brands.push(el.classList.value.replace('brand', '').trim());
  });

  const result = JSON.stringify({'uid': get_uid(), 'brands': brands});
  save_into_local_storage('choices4', result);
  return await save_into_remote_storage('/register/player/brands', result);
}

function get_uid() {
  var uid = localStorage.getItem('uid');
  if (uid)
    return parseInt(uid);

  uid = Date.now();
  localStorage.setItem('uid', uid);
  return uid;
}
