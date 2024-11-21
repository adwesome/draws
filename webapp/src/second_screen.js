function second_screen() {
  const this_screen = document.getElementById('second_screen');
  if (this_screen.style.display != 'block')
    this_screen.style.display = 'block';

  const all_images = document.querySelectorAll('.brand');
  const btn_go_to_third = document.getElementById('to_third');
  all_images.forEach((img) => {
    img.addEventListener('click', function(event) {
      const brand = event.target.classList[1];
      const all_brand_images = document.querySelectorAll('.brand.' + brand);
      var filter = 'unset';
      if (event.target.style.filter == 'unset')
        filter = 'brightness(3) grayscale(1)';

      all_brand_images.forEach((ab) => {
        ab.style.filter = filter;
      });

      var ready_to_go = 0;
      for (let i = 0; i < all_images.length; i++) {
        const s = all_images[i];
        if (s.style.filter == 'unset')
          ready_to_go += 1;
      }

      if (ready_to_go)
        btn_go_to_third.disabled = false;
      else
        btn_go_to_third.disabled = true;
    });
  });

  btn_go_to_third.addEventListener('click', async function () {
    const data_saved = await collect_brands_data_from_form();
    /*
    console.log(data_saved);
    if (!data_saved)
      return;
    if (data_saved.status != 0)
      return;
    if (!data_saved.ok)  // 200 OK for no-cors
      return;
    */

    //document.getElementById('first_screen').style.display = 'none';
    document.getElementById('second_screen').style.display = 'none';
    //document.getElementById('second_screen_explain').style.display = 'none';
    save_into_local_storage('second_screen_passed', true);
    play();
  });

  set_existing_brands_choices();
}
