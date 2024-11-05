function set_cities_display_attr(display) {
  document.getElementById('city').style.display = display;
  document.getElementById('city_label').style.display = display;
}

window.onload = function() {
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

      if (ready_to_go)
        btn_go_to_second.disabled = false;
      else
        btn_go_to_second.disabled = true;
    });
  });

  btn_go_to_second.addEventListener('click', function () {
    document.getElementById('first_screen').style.display = 'none';
    document.getElementById('second_screen').style.display = 'unset';
  })
}