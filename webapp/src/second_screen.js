function second_screen() {
  const all_images = document.querySelectorAll('.brand');
  const btn_go_to_third = document.getElementById('to_third');
  all_images.forEach((img) => {
    img.addEventListener('click', function(event) {
      if (event.target.style.filter != 'unset')
        event.target.style.filter = 'unset';
      else
        event.target.style.filter = 'brightness(3) grayscale(1)';

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

  btn_go_to_third.addEventListener('click', function () {
    document.getElementById('second_screen').style.display = 'none';
    document.getElementById('second_screen_explain').style.display = 'none';
    play();
  });
}
