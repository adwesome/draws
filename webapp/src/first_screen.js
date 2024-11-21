function set_cities_display_attr(display) {
  document.getElementById('city').style.display = display;
  document.getElementById('city_label').style.display = display;
}

function draw_demography_poll(target) {
  const html = '\
  <label>Регион, в котором вы живете:</label>\
  <select id="region" class="form-select">\
    <option value="-1" selected>- выберите -</option>\
    <option value="51">Мурманская обл.</option>\
    <option value="10">респ. Карелия</option>\
    <option value="29">Архангельская обл.</option>\
    <option value="47">г. Санкт-Петербург и ЛО</option>\
    <option value="35">Вологодская обл.</option>\
    <option value="53">Новгородская обл.</option>\
    <option value="50">г. Москва и МО</option>\
    <option value="-2">- другой -</option>\
  </select>\
  \
  <label id="city_label" style="display: none;">Город, в котором вы живете:</label>\
  <select id="city" class="form-select" style="display: none;">\
    <option value="-1" selected>- выберите -</option>\
    <option value="1">Беломорск</option>\
    <option value="2">Кемь</option>\
    <option value="3">Кондопога</option>\
    <option value="4">Костомукша</option>\
    <option value="5">Лахденпохья</option>\
    <option value="6">Медвежьегорск</option>\
    <option value="7">Олонец</option>\
    <option value="8">Петрозаводск</option>\
    <option value="9">Питкяранта</option>\
    <option value="10">Пудож</option>\
    <option value="11">Сегежа</option>\
    <option value="12">Сортавала</option>\
    <option value="13">Суоярви</option>\
    <option value="-2">- другой -</option>\
  </select>\
  \
  <label>Ваш пол:</label>\
  <select id="sex" class="form-select">\
    <option value="-1" selected>- выберите -</option>\
    <option value="1">Женский</option>\
    <option value="2">Мужской</option>\
  </select>\
  \
  <label>Ваш возраст:</label>\
  <select id="age" class="form-select">\
    <option value="-1" selected>- выберите -</option>\
    <option value="1">до 14 лет включительно</option>\
    <option value="2">15-19 лет</option>\
    <option value="3">20-24 лет</option>\
    <option value="4">25-29 лет</option>\
    <option value="5">30-34 лет</option>\
    <option value="6">35-39 лет</option>\
    <option value="7">40-44 лет</option>\
    <option value="8">45-49 лет</option>\
    <option value="9">50-54 лет</option>\
    <option value="10">55-59 лет</option>\
    <option value="11">60-64 лет</option>\
    <option value="12">65-69 лет</option>\
    <option value="13">от 70 лет включительно</option>\
  </select>';
  document.getElementById(target).innerHTML = html;
}

function draw_demography(target) {
  draw_demography_poll(target);

  const first_screen = document.getElementById('first_screen');
  if (first_screen)
    document.getElementById('first_screen').style.display = 'block';

  const region = document.getElementById('region');
  region.addEventListener('change', function() {
    if (region.value == '10')
      set_cities_display_attr('unset');
    else
      set_cities_display_attr('none');
  });

  const btn_go_to_second = document.getElementById('to_second');
  const all_selects = document.querySelectorAll('select');
  all_selects.forEach((select) => {
    select.addEventListener('change', function() {
      var ready_to_go = true;
      const region = document.getElementById('region');
      for (let i = 0; i < all_selects.length; i++) {
        const s = all_selects[i];

        if (s.style.display == 'none')
          continue;
        if (s.value == '-1') {
          ready_to_go = false;
          break;
        }
      }

      if (first_screen) {
        if (ready_to_go)
          btn_go_to_second.disabled = false;
        else
          btn_go_to_second.disabled = true;
      }
      else {
        collect_demography_data_from_form();
      }
    });
  });

  if (first_screen) {
    btn_go_to_second.addEventListener('click', async function () {
      const data_saved = await collect_demography_data_from_form();
      /*
      console.log(data_saved);
      if (!data_saved)
        return;
      if (data_saved.status != 0)
        return;
      if (!data_saved.ok)  // 200 OK for no-cors
        return;
      */
      document.getElementById('first_screen').style.display = 'none';
      document.getElementById('second_screen').style.display = 'block';
      save_into_local_storage('first_screen_passed', true);
      document.getElementById('first_screen').remove();
      second_screen();
    });

    set_existing_demography_choices();
  }
}
