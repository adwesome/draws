var campaigns = [];
var participants = [];
var winners = [];

const category_map = {
  'campaigns': [],
  'winners': [],
  'participants': [],
};

const uids_to_names = {
  1096170666: "Кирилл",
  5322015870: "Саша",
  359070623: "Лёша",
  5026988889: "Аксинья",
  1967872358: "Егор",
  1563924371: "Даша 1",
  1636956987: "Ксюша",
  6371357131: "Рома",
  5262399557: "Таня",
  1016952170: "Наташа",
  5838588705: "Алёна",
  6160219684: "Даша 2",
};

function show_history() {
  document.getElementById('show_history').style.display = 'none';
  document.getElementById('hidden-history').style.display = 'unset';
}



async function create_drawings_list() {
  const uid = get_uid();

  let html_next = '';
  let html_now = '';
  let html_past = '';
  let html_just = '';

  let wins = 0;
  let lost = 0;
  let not = 0;

  let past_counter = 0;

  const date_today = today();
  const date_yesterday = yesterday();
  const history = await get_participation_history();
  for (let i = 0; i < history.length; i++) {
    const campaign = history[i];
    const date = new Date(parseInt(campaign[5]) * 1000);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const date_participated = date.toISOString().split('T')[0];
    const chance = campaign[2];
    const brand = campaign[3];
    const status = campaign[4];

    if (date_participated == date_today) {
      html_now += `<p>${day}.${month} <span class="status ongoing">🤞 Вы участвуете</span>`;
      html_now += `${chance}% участников выиграют подарки от <b>${brand}</b></p>`;
    }
    else {
      past_counter += 1;
      if (past_counter == 4)
        html_past += '<p id="show_history"><a href="#" onclick="show_history();">Открыть всю историю</a></p> <div id="hidden-history">';

      html_past += `<p>${day}.${month} <span class="status `;

      if (status >= 1) {
        html_past += 'won">🎉 Вы выиграли';
        wins += 1;
      }
      else {
        if (status == 0) {
          html_past += 'lost">🙁 Вы не выиграли';
          lost += 1;
        }
        else {
          html_past += 'not">😐 Вы не участвовали';
          not += 1;
        }
      }
    }
    if (date_participated < date_today) {
      html_past += `</span>`;
      html_past += `${chance}% участников выиграли подарки от <b>${brand}</b>`;
    }

    if (date_participated == date_yesterday) {
      html_just = html_past + '</p>';
    }
  }

  html_past += '</div>';
  html_past = '<div id="chart-wrapper"><canvas id="chart-stats"></canvas></div>' + html_past;
  if (wins)
    html_past = `<p class="stats-clarify">Вы выиграли ${wins} из ${wins + lost} раз, когда вы участвовали (т.е., на данный момент, вы выигрываете в ${Math.round(wins * 100 / (wins + lost))}% случаев, если участвуете)</p>` + html_past;
  else if (lost)
    html_past = `<p class="stats-clarify">Вы участвовали в розыгрыше ${times(lost)}, но пока ни разу не выиграли. Нужно больше участий. Приходите и участвуйте завтра!</p>` + html_past;

  if (html_just)
    document.getElementById('just').innerHTML = html_just;
  else if (!past_counter)
    document.getElementById('yesterday').style.display = 'none';
  //else if (!html_just && !past_counter)
  //  document.getElementById('just').innerHTML = '<p>Был розыгрыш, но вы в нем не участвовали</p>';
  if (1) //html_next)
    document.getElementById('next').innerHTML = '<p>Приходите узнать результаты прошедшего розыгрыша и поучаствовать в новом!</p>';
  if (html_now)
    document.getElementById('now').innerHTML = html_now;
  if (html_past && past_counter)
    document.getElementById('past').innerHTML = html_past;

  if (wins || lost || not)
    draw_chart(wins, lost, not);
}


function deadline(date) {  // https://stackoverflow.com/questions/948532/how-to-convert-a-date-to-utc
  if (!(date.getUTCHours() <= 1 && date.getUTCMinutes() < 30))
    date.setUTCDate(date.getUTCDate() + 1);
  date.setUTCHours(1,30,0,0);

  return Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds());
}

function start_countdown(time) {  // https://flaviocopes.com/how-to-get-tomorrow-date-javascript/
  time = time || deadline(new Date()) / 1000;
  var flipdown = new FlipDown(time, {
    headings: ["Дни", "Часы", "Минуты", "Секунды"],
  }).start();

  document.getElementsByClassName('rotor-group')[0].style.display = 'none';
}

async function play_demo() {
  swiper_inner.slideTo(1, 2000, false);
  await sleep(2000);
  swiper_inner.slideTo(0, 2000, false);
  await sleep(2000);
  swiper_outer.slideTo(1, 2000, false);
  await sleep(2000);
  swiper_outer.slideTo(0, 2000, false);
}


async function submit_participation(data) {  // https://stackoverflow.com/questions/29775797/fetch-post-json-data
  const response = await fetch(SERVER_HOSTNAME + '/register/player/participation', {
    mode: 'no-cors',
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  //const result = await response.json();
  //console.log(result);
  //return result
}
async function get_participation(data) {  // https://stackoverflow.com/questions/29775797/fetch-post-json-data
  const response = await fetch(SERVER_HOSTNAME + '/get/player/participation?uid=' + data.uid, {});
  return await response.json();
}

async function get_campaign_for_me_today() {
  const uid = get_uid();
  const response = await fetch(SERVER_HOSTNAME + `/get/campaign?uid=${uid}`, {});
  const data = await response.json();
  if (data.code != 200)
    return;

  category_map['campaigns'] = data.result;
}


async function get_participation_history() {
  const uid = get_uid();
  const response = await fetch(SERVER_HOSTNAME + `/get/participation/history?uid=${uid}`, {});
  const data = await response.json();
  if (data.code != 200)
    return;

  return data.result;
}


var swiper_inner;
var swiper_outer;

function is_newcomer() {
  if (!localStorage.getItem('onboarding_complete')) {
    localStorage.setItem('onboarding_complete', true);
    return true;
  }
  return false;
}

async function run_progress_bar(seconds) {
  let i = 0;
  seconds = seconds || 5;  // 5 sec by default
  const rad_to_degree = 57.295779513;

  const ad = document.getElementById('ad');
  const ad_container = document.getElementById('js-container');
  ad_container.style.backgroundColor = 'white';

  var simplebar = new Nanobar();
  const interval = setInterval(async () => {
    simplebar.go(i);

    ad.style.opacity = Math.cos(i * 10 / rad_to_degree) * 0.05 + 0.95;
    i += 1;
    if (i > 100) {
      clearInterval(interval);
      enable_swipe();
      enable_flip();
      await sleep(500);

      if (is_newcomer()) {
        play_demo();
        return;
      }

      swiper_inner.slideTo(1, 2000, false);
      await sleep(2000);
      ad.style.opacity = 1;
    }
  }, seconds * 1000 / 100);
  await sleep(seconds);
}

function enable_flip() {
  swiper_inner = new Swiper(".swiper-inner", {
    speed: 1500,
    effect: "flip",
    loop: true,
    cssMode2: true,
    followFinger: false,
    flipEffect: {
      slideShadows: true,
    },
    pagination: {
      el: ".swiper-inner-pagination",
      clickable: true,
    },
  });
}

function enable_swipe() {
  swiper_outer = new Swiper(".swiper-outer", {
    speed: 1500,
    direction: "vertical",
    cssMode: true,
    pagination: {
      el: ".swiper-outer-pagination",
      clickable: true,
    },
  });
}


function remove_canvas(canvas) {
  if (!canvas)
    return;
  if (!canvas.parentNode)
    return;

  canvas.parentNode.removeChild(canvas);
  document.getElementById('js-canvas-explain').remove();
}


async function play() {
  'use strict';
  start_countdown();

  const this_screen = document.getElementById('third_screen');
  if (this_screen.style.display != 'block')
    this_screen.style.display = 'block';

  const ad_element = document.getElementById('ad');
  const ad_explain = document.getElementById('ad_explain');

  let participates = await get_participation({'uid': get_uid(), 'tguid': get_tguid_from_url()});
  if (participates.result.length != 0) {  // if participated already
    if (document.getElementById('js-canvas-explain'))
      document.getElementById('js-canvas-explain').remove();
    ad_element.style.visibility = 'visible';
    ad_explain.style.visibility = 'visible';
    //await calculate_percent(cid);
    enable_swipe();
    enable_flip();

    const campaign = participates.result[0];
    const ad = campaign[1];
    const percent = campaign[2];
    ad_element.style.background = `no-repeat center url("${ad}?v=${percent}")`;
    const cid = campaign[0];
    const who = campaign[3];
    document.getElementById('who').innerHTML = who;
    document.getElementById('percent').innerHTML = percent;
    create_drawings_list();
    return;
  }


  //await get_all('campaigns', 'uid=' + get_uid()); // need some stub if no ad
  await get_campaign_for_me_today();
  const campaign = category_map['campaigns'];
  //await get_all('winners', 'uid=' + get_uid());
  
  if (campaign.length == 0) {
    const explain = document.getElementById('js-canvas-explain');
    explain.innerHTML = 'Сегодня нет розыгрыша.';
    explain.style.color = 'black';
    explain.style.paddingTop = '95vh';
    enable_swipe();
    await sleep(2000);
    swiper_outer.slideTo(1, 2000, false);
    //await get_all('participants');
    create_drawings_list();
    return;
  }

  if (!localStorage.getItem('onboarding_complete'))
    document.getElementById('js-canvas-explain').style.display = 'block';

  const ad = campaign[1];
  const percent = campaign[2];
  ad_element.style.background = `no-repeat center url("${ad}?v=${percent}")`;
  const cid = campaign[0];
  const who = campaign[3];
  document.getElementById('who').innerHTML = who;
  document.getElementById('percent').innerHTML = percent;
  // const percent = campaign[3];

  var canvas = document.getElementById('js-canvas');
  const canvas_container = document.getElementById('js-container');
  canvas.width = canvas_container.offsetWidth; //window.innerWidth;
  canvas.height = canvas_container.offsetHeight; //window.innerHeight;

  var isDrawing, lastPoint;
  var container    = document.getElementById('js-container'),
      // canvas       = document.getElementById('js-canvas'),
      canvasWidth  = canvas.width,
      canvasHeight = canvas.height,
      ctx          = canvas.getContext('2d', { willReadFrequently: true }),
      image        = new Image(),
      brush        = new Image();
      // console.log(canvasWidth, canvasHeight)
  // base64 Workaround because Same-Origin-Policy
  const images = [ // https://www.vecteezy.com/free-vector/scratch-texture
    'img/scratch-silver.jpg',
    //'img/scratch-rainbow.jpg',
  ];
  //const b = choice(images.length);
  //image.src = images[b];
  image.src = images[0];
  const shift = 0;
  image.onload = function() {
    ctx.drawImage(image, -canvasWidth * shift, 0, canvasWidth * (1 + 2 * shift), canvasHeight);
    ad_element.style.visibility = 'visible';
    ad_explain.style.visibility = 'visible';
  };
  brush.src = 'data:image/png;base64,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';
  
  canvas.addEventListener('mousedown', handleMouseDown, false);
  canvas.addEventListener('touchstart', handleMouseDown, false);
  canvas.addEventListener('mousemove', handleMouseMove, false);
  canvas.addEventListener('touchmove', handleMouseMove, false);
  canvas.addEventListener('mouseup', handleMouseUp, false);
  canvas.addEventListener('touchend', handleMouseUp, false);

  canvas.addEventListener('transitionend', async function() {
    remove_canvas(canvas);
    await run_progress_bar();
    await submit_participation({'uid': get_uid(), 'tguid': get_tguid_from_url(), 'cid': cid});
    //await calculate_percent(cid);
    create_drawings_list();
  });

  function distanceBetween(point1, point2) {
    return Math.sqrt(Math.pow(point2.x - point1.x, 2) + Math.pow(point2.y - point1.y, 2));
  }
  
  function angleBetween(point1, point2) {
    return Math.atan2( point2.x - point1.x, point2.y - point1.y );
  }
  
  // Only test every `stride` pixel. `stride`x faster,
  // but might lead to inaccuracy
  function getFilledInPixels(stride) {
    if (!stride || stride < 1) { stride = 1; }
    
    var pixels   = ctx.getImageData(0, 0, canvasWidth, canvasHeight),
        pdata    = pixels.data,
        l        = pdata.length,
        total    = (l / stride),
        count    = 0;
    
    // Iterate over all pixels
    for(var i = count = 0; i < l; i += stride) {
      if (parseInt(pdata[i]) === 0) {
        count++;
      }
    }
    
    return Math.round((count / total) * 100);
  }
  
  function getMouse(e, canvas) {
    var offsetX = 0, offsetY = 0, mx, my;

    if (canvas.offsetParent !== undefined) {
      do {
        offsetX += canvas.offsetLeft;
        offsetY += canvas.offsetTop;
      } while ((canvas = canvas.offsetParent));
    }

    mx = (e.pageX || e.touches[0].clientX) - offsetX;
    my = (e.pageY || e.touches[0].clientY) - offsetY;

    return {x: mx, y: my};
  }
  
  function handlePercentage(filledInPixels) {
    filledInPixels = filledInPixels || 0;
    //console.log(filledInPixels + '%');
    if (filledInPixels > 72) {
      canvas.classList.add('animate');
    }
  }
  
  function handleMouseDown(e) {
    isDrawing = true;
    lastPoint = getMouse(e, canvas);
  }

  function handleMouseMove(e) {
    if (!isDrawing) { return; }
    
    e.preventDefault();
    document.getElementById('js-canvas-explain').classList.add('animate');

    var currentPoint = getMouse(e, canvas),
        dist = distanceBetween(lastPoint, currentPoint),
        angle = angleBetween(lastPoint, currentPoint),
        x, y;
    
    for (var i = 0; i < dist; i++) {
      x = lastPoint.x + (Math.sin(angle) * i) - 25;
      y = lastPoint.y + (Math.cos(angle) * i) - 25;
      ctx.globalCompositeOperation = 'destination-out';
      ctx.drawImage(brush, x, y);
    }
    
    lastPoint = currentPoint;
    handlePercentage(getFilledInPixels(32));
  }

  function handleMouseUp(e) {
    isDrawing = false;
  }
};

function times(number) {
  const last_digit = number.toString().slice(-1);
  const a = ['2', '3', '4'];
  const b = [12, 13, 14];
  if (a.includes(last_digit) && !b.includes(number))
    return number + ' раза';
  return number + ' раз';
}

function draw_chart(wins, lost, not) {
  let labels = [];
  let data = [];
  let bg_color = [];
  if (wins != 0) {
    labels.push('Выиграли');
    data.push(wins);
    bg_color.push('limegreen');
  }
  if (lost != 0) {
    labels.push('Не выиграли');
    data.push(lost);
    bg_color.push('deepskyblue');
  }
  if (not != 0) {
    labels.push('Не участвовали');
    data.push(not);
    bg_color.push('orangered');
  }

  new Chart('chart-stats', {
    type: 'doughnut',
    options: {
      plugins: {
        legend: {
          position: 'bottom',
        },
        tooltip: {
          enabled: false,
        }
      },
    },
    data: {
      labels: labels,
      datasets: [{
        //label: 'My First Dataset',
        data: data,
        backgroundColor: bg_color,
        hoverOffset: 4
      }]
    }
  });
}