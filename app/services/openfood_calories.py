import aiohttp

async def get_product_calories(product_name: str):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": product_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

    if not data.get("products"):
        return None

    product = data["products"][0]
    nutriments = product.get("nutriments", {})

    calories = nutriments.get("energy-kcal_100g")
    return calories
