from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("nih_icd10_server")


async def make_nih_request(term: str) -> list[Any] | None:
    """Make a request to the NIH Clinical Tables Search Service API."""
    url = (
        f"https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?terms={term}&count=5"
    )
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None


@mcp.tool()
async def get_icd_10_code(name_or_code: str) -> str:
    """Retrieves ICD-10-CM codes and names based on a search term.

    Args:
        name_or_code: A name or partial code to search for (e.g., "tuberc" or "A15").
    """
    data = await make_nih_request(name_or_code)

    if data is None:
        return "Unable to fetch ICD-10 codes from the NIH API."

    # The API returns a list, and the 4th element (index 3) is the list of display strings
    # in the format [['code', 'name'], ...]
    results = data[3]

    if not results:
        return f"No ICD-10 codes found for '{name_or_code}'."

    formatted_results = []
    for code_name_pair in results:
        code = code_name_pair[0]
        name = code_name_pair[1]
        formatted_results.append(f"Code: {code}, Name: {name}")

    return "\n".join(formatted_results)


if __name__ == "__main__":
    mcp.run(transport="stdio")
