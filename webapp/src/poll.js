var orgs;

const c = {
  'Кафе, рестораны, бары': [
    'Кафе-бар',
    'Кондитерская',
    'Кафе',
    'Кафе, бар',
    'Магазин кулинарии, производство кондитерских и хлебобулочных изделий',
    'Суши-бар',
    'Кальян-бар, антикафе',
    'Быстрое питание',
    'Пиццерия, кафе',
    'Ресторан',
    'Быстрое питание, ресторан, кафе',
    'Кафе, ресторан, быстрое питание',
    'Кафе, мороженое',
    'Кафе, столовая',
    'Рестораны',
    'Бары',
    'Магазин кулинарии',
    'Трактир',
    'Доставка еды и обедов, магазин суши и роллов',
    'Магазин японской кухни',
  ],
  'Красота': [
    'Парикмахерские',
    'Салон красоты',
    'Ногтевые студии',
    'Парикмахерская',
    'Студия красоты',
    'Ногтевая студия',
    'Магазин парфюмерии и косметики',
    'Магазин парфюмерии и косметики, магазин хозтоваров',
    'Сеть магазинов косметики и бытовой химии',
    'Магазин косметики и товаров для дома',
  ],
  'Отдых': [
    'Гостиница',
    'Баня, сауна',
    'Сауна',
    'Компьютерный клуб, киберспорт',
    'Развлекательный центр',
    'Кинотеатр',
    'Товары для рыбалки, магазин верхней одежды',
    'Детский развлекательный центр',
    'Гостиницы',
    'Турагентство, туристический инфоцентр'
  ],
  'Продукты': [
    'Магазин продуктов',
    'Молочный магазин',
    'Супермаркет',
    'Супермаркеты',
    'Продуктовый магазин',
    'Сеть супермаркетов',
    'Рыбный магазин',
    'Продовольственный магазин',
    'Орехи, снеки, сухофрукты, магазин подарков и сухофруктов',
    'Магазин низких цен',
  ],
  'Аптека и оптика': [
    'Аптека',
    'Салон оптики',
  ],
  'Спорт': [
    'Спортивный комплекс',
    'Спортивный магазин, товары для отдыха и туризма',
  ],
  'Авто- и мото-': [
    'Шиномонтаж', 
    'Электро- и бензоинструмент, запчасти для мототехники', 
    'Магазин автозапчастей и автотоваров',
    'Автошкола',
    'Автосервис',
    'Автомойка',
    'АЗС',
    'Автосервис, автотехцентр',
  ],
  'Товары для обустройства дома и дачи': [
    'Магазин для садоводов',
    'Строительный магазин',
    'Строительный магазин, магазин сантехники, электрики',
    'Торговый центр, фасады и фасадные системы',
    'Магазин мебели',
    'Магазин хозтоваров, бытовой химии и строительных материалов',
    'Магазин мебели, светильники, окна',
    'Окна',
    'Окна, жалюзи и рулонные шторы, двери',
    'Торговый центр',
    'Автоматические двери и ворота, двери',
    'Строительная компания',
    'Буровые работы, монтаж и обслуживание систем водоснабжения',
    'Магазин товаров для школы и офиса',
    'Товары для дома',
  ],
  'Бытовая техника и электроника': [
    'Оператор сотовой связи, товары для мобильных телефонов',
    'Компьютерный магазин, магазин электроники',
    'Компьютерный магазин, магазин бытовой техники',
    'Магазин бытовой техники, электроники и детских товаров',
    'Фотоуслуги, ремонт оргтехники, расходные материалы',
  ],
  'Алкоголь': [
    'Магазин разливного пива',
    'Магазин алкогольных напитков',
  ],
  'Одежда и обувь': [
    'Магазин обуви',
    'Магазин одежды',
    'Магазин нижнего белья',
    'Магазин одежды, магазин бижутерии',
    'Секонд-хенд',
    'Ремонт одежды',
    'Магазин ткани, швейная фурнитура',
    'Ателье по пошиву одежды',
  ],
  'Подарки и сувениры': [
    'Магазин подарков и сувениров',
    'Ювелирный магазин',
  ],
  'Товары для детей': [
    'Магазин детских товаров',
  ],
  'Товары для животных': [
    'Магазин',
  ],
  'Стоматология': [
    'Стоматологическая клиника',
    'Частные стоматологии',
    'Стоматологическая клиника, детская стоматология',
  ],
  'Канцтовары': [
    'Канцтовары',
    'Магазин канцтоваров'
  ],
  'Цветы': [
    'Салон',
    'Магазин цветов',
    'Магазин цветов, доставка цветов и букетов',
  ],
  'Страхование и юристы': [
    'Нотариусы',
    'Страховая компания, страхование автомобилей',
    'Агентство недвижимости, земельные участки',
  ],
};

var categories = {};
//var uid;

function draw_orgs() {
  let result = '';
  //result += `<p>${get_uid()}</p>`;
  const new_existing_choices = get_items_from_local_storage('choices5');

  // temp
  const orgs_available = [55, 107, 119, 84, ];
  const orgs_preparing = []; //[203, ];
  const orgs_not_available = [43, 57, 59, 67, 68, 70, 112, 116, 120, 123, 144, 205, 204, 81, ];

  for (key in c) {
    result += `<h4>${key}</h4>`;
    result += '<ul>';
    const em = categories[key];
    em.forEach((e) => {
      result += `<li><label`
      if (orgs_available.includes(e[1]))
        result += ' class="available"';
      else if (orgs_preparing.includes(e[1]))
        result += ' class="preparing"';
      else if (orgs_not_available.includes(e[1]))
        result += ' class="not-available"';
      result += `><input type="checkbox" id="orgs-${e[1]}" value="${e[1]}"`;

      if (new_existing_choices.brands.includes(e[1]))
        result += ' checked';

      result += `> <b>${e[3]}</b> (${e[4]}) <br><span class="address">${e[11]}</span></label></li>`;
    });
    result += '</ul>';
  }
  
  document.getElementById('list').innerHTML = result;
  checkboxes = document.querySelectorAll('input');
  checkboxes.forEach((el) => {
    el.addEventListener('change', function(e) {
      collect_data_from_form();
    });
  });

  selectors = document.querySelectorAll('select');
  selectors.forEach((el) => {
    el.addEventListener('change', function(e) {
      collect_data_from_form();
    });
  });

  set_existing_choises();
}

function save_items_into_local_storage(items) {
  localStorage.setItem('choices5', items);
}
function load_items_from_local_storage() {
  let links = localStorage.getItem('choices5') || "{}";
  return JSON.parse(links);
}

function set_existing_choises() {
  const existing_choises = load_items_from_local_storage();
  if (Object.keys(existing_choises).length == 0)  // pizdec
    return;

  existing_choises.brands.forEach((value) => {
    const f = document.getElementById(`orgs-${value}`);
    if (f)
      f.checked = true;
  });
}

async function save_items_into_remote_storage(data) {
  const response = await fetch(SERVER_HOSTNAME + '/orgs', {
    mode: 'no-cors',
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  //return await response.json();
  //console.log(data);
}

async function get_orgs() {
  const response = await fetch(SERVER_HOSTNAME + '/orgs/all', {});
  const o = await response.json();
  return o;
}

async function get_choices() {
  const response = await fetch(SERVER_HOSTNAME + `/get/player/choices?uid=${uid}`, {});
  const o = await response.json();
  return o;
}

function collect_data_from_form() {
  let d = [];
  document.querySelectorAll('select').forEach((el) => {
    d.push(parseInt(el.value));
  });

  let o = [];
  document.querySelectorAll('input:checked').forEach((el) => {
    o.push(parseInt(el.value));
  });

  const result = JSON.stringify({'uid': uid, 'demography': d, 'brands': o});
  save_items_into_local_storage(result);
  save_items_into_remote_storage(result);

  return result;
}

function fill_categories() {
  categories = {}
  for (let i = 0; i < orgs.length; i++) {
    const e = orgs[i];
    const name = e[3];
    const type = e[4];
    const addr = e[11];
    for (cat in c) {
      if (c[cat].includes(type)) {
        if (cat in categories)
          categories[cat].push(e);
        else
          categories[cat] = [e];

        var index = orgs.indexOf(e);
        if (index !== -1) {
          orgs.splice(index, 1);
          i = i - 1;
        }
        break;
      }
    }
  }
}

async function init_orgs_poll() {
  document.getElementById('brands').style.display = 'unset';
  orgs = (await get_orgs()).orgs;
  //choices = (await get_choices()).result;
  //console.log(choices);
  fill_categories();
  draw_orgs();
  //collect_data_from_form();
}

function hide_orgs_poll() {
  document.getElementById('brands').style.display = 'none';
}