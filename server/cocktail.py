from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("cocktail-db")

BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/"
USER_AGENT = "cocktail-mcp-server/1.0"


async def _make_cocktaildb_request(
    endpoint: str, params: dict = None
) -> dict[str, Any] | None:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    url = f"{BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url, params=params, headers=headers, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            if data and data.get("drinks") is None and data.get("ingredients") is None:
                return None
            return data
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


def _format_drink_details(drink: dict) -> str:
    details = [
        f"Name: {drink.get('strDrink', 'N/A')}",
        f"Category: {drink.get('strCategory', 'N/A')}",
        f"Alcoholic: {drink.get('strAlcoholic', 'N/A')}",
        f"Glass: {drink.get('strGlass', 'N/A')}",
        f"Instructions: {drink.get('strInstructions', 'N/A')}",
    ]

    ingredients = []
    for i in range(1, 16):
        ingredient = drink.get(f"strIngredient{i}")
        measure = drink.get(f"strMeasure{i}")
        if ingredient:
            if measure:
                ingredients.append(f"{measure.strip()} {ingredient.strip()}")
            else:
                ingredients.append(ingredient.strip())
    if ingredients:
        details.append(f"Ingredients: {', '.join(ingredients)}")

    return "\n".join(details)


@mcp.tool()
async def search_cocktail_by_name(name: str) -> str:
    """
    Search for cocktails by name.

    Args:
        name: The name of the cocktail to search for.
    """
    data = await _make_cocktaildb_request("search.php", {"s": name})
    if not data or not data["drinks"]:
        return "No cocktails found with that name."

    drinks = data["drinks"]
    formatted_drinks = []
    for drink in drinks:
        formatted_drinks.append(
            f"ID: {drink.get('idDrink')}, Name: {drink.get('strDrink')}, "
            f"Category: {drink.get('strCategory', 'N/A')}"
        )
    return "\n---\n".join(formatted_drinks)


@mcp.tool()
async def list_cocktails_by_first_letter(letter: str) -> str:
    """
    List all cocktails by their first letter.

    Args:
        letter: The first letter of the cocktail (single character).
    """
    if not letter or len(letter) != 1 or not letter.isalpha():
        return "Please provide a single alphabetical character."

    data = await _make_cocktaildb_request("search.php", {"f": letter.lower()})
    if not data or not data["drinks"]:
        return f"No cocktails found starting with the letter '{letter.upper()}'."

    drinks = data["drinks"]
    formatted_drinks = []
    for drink in drinks:
        formatted_drinks.append(
            f"ID: {drink.get('idDrink')}, Name: {drink.get('strDrink')}"
        )
    return "\n".join(formatted_drinks)


@mcp.tool()
async def search_ingredient_by_name(name: str) -> str:
    """
    Search for an ingredient by name.

    Args:
        name: The name of the ingredient to search for.
    """
    data = await _make_cocktaildb_request("search.php", {"i": name})
    if not data or not data["ingredients"]:
        return "No ingredients found with that name."

    ingredients = data["ingredients"]
    formatted_ingredients = []
    for ing in ingredients:
        formatted_ingredients.append(
            f"Ingredient: {ing.get('strIngredient')}\n"
            f"ID: {ing.get('idIngredient')}\n"
            f"Description: {ing.get('strDescription', 'N/A')}\n"
            f"Alcoholic: {ing.get('strAlcohol', 'N/A')}\n"
            f"Type: {ing.get('strType', 'N/A')}"
        )
    return "\n---\n".join(formatted_ingredients)


@mcp.tool()
async def list_random_cocktails() -> str:
    """
    Lookup a random cocktail.
    """
    data = await _make_cocktaildb_request("random.php")
    if not data or not data["drinks"]:
        return "Could not fetch a random cocktail at this time."

    drink = data["drinks"][0]
    return _format_drink_details(drink)


@mcp.tool()
async def lookup_cocktail_details_by_id(id: str) -> str:
    """
    Lookup full cocktail details by its ID.

    Args:
        id: The ID of the cocktail.
    """
    data = await _make_cocktaildb_request("lookup.php", {"i": id})
    if not data or not data["drinks"]:
        return f"No cocktail found with ID: {id}."

    drink = data["drinks"][0]
    return _format_drink_details(drink)


if __name__ == "__main__":
    mcp.run(transport="stdio")
