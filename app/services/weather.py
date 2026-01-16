import aiohttp

async def get_temperature_by_city(city: str, api_key: str) -> float | None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",   
        "lang": "ru",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                return None

            data = await response.json()
            return data["main"]["temp"]
