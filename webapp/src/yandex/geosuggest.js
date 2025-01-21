// https://yandex.ru/dev/geosuggest/doc/ru/request
// https://suggest-maps.yandex.ru/v1/suggest?apikey=b3e94b05-8847-4633-9fa5-01476236a384&text=something&types=biz&spn=0.1,0.1&ll=61.7849,34.3469&ull=34.3469,61.7849
async function call_geosuggest(text, lat, long) {
  const baseUrl = "https://suggest-maps.yandex.ru/v1/suggest";  
  const apiKey = "b3e94b05-8847-4633-9fa5-01476236a384";
  const spn = "0.1,0.1";
  const types = "biz";
  
  const url = `${baseUrl}?apikey=${apiKey}&text=${encodeURIComponent(text)}&types=${types}&spn=${spn}&ll=${lat},${long}&ull=${long},${lat}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok)
      throw new Error(`API call failed with status: ${response.status} (${response.statusText})`);

    return await response.json();
  } catch (error) {
    console.error("API call error:", error);
    throw error;
  }
}

/*
call_geosuggest("something", 61.7849, 34.3469)
  .then(data => {
    console.log("API Response:", data);
  })
  .catch(error => {
    console.error("Error calling the API:", error);
  });
*/