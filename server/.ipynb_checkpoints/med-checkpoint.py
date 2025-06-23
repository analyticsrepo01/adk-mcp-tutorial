import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("medlineplus_term_explainer")

MEDLINEPLUS_API_BASE = "https://wsearch.nlm.nih.gov/ws/query"
USER_AGENT = "medlineplus-mcp-server/1.0"


async def make_medlineplus_request(params: dict[str, Any]) -> str | None:
    """Make a request to the MedlinePlus Web Service API."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/xml"}

    # Manually encode term if it's a phrase for better URL readability
    if "term" in params and " " in params["term"]:
        params["term"] = quote_plus(params["term"])

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                MEDLINEPLUS_API_BASE, params=params, headers=headers, timeout=30.0
            )
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            return response.text
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors specifically
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        # Handle network errors
        print(f"An error occurred while requesting {e.request.url!r}: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return None


@mcp.tool()
async def get_medical_term(medical_term: str) -> str:
    """Get explanation for a medical term from MedlinePlus.

    Args:
        medical_term: The medical term to get an explanation for (e.g., 'diabetes', 'hypertension').
    """
    params = {
        "db": "healthTopics",
        "term": medical_term,
        "rettype": "topic",  # Request full topic XML
    }

    xml_response = await make_medlineplus_request(params)

    if not xml_response:
        return f"Could not retrieve information for '{medical_term}'. Please try again later or check the term."

    try:
        root = ET.fromstring(xml_response)

        # Namespace might be present, handle it generically
        # Find the healthTopic content node
        health_topic_content = root.find('.//content[@name="healthTopic"]')

        if health_topic_content is None or not health_topic_content.text:
            return f"No detailed topic content found for '{medical_term}'. It might not be available or the term is too broad/specific."

        # Parse the inner XML of the healthTopic content
        topic_root = ET.fromstring(health_topic_content.text)

        # Look for summary or description sections in the detailed topic XML
        # Common paths based on MedlinePlus XML DTD
        summary_section = topic_root.find("./summary_section/summary_content")
        if summary_section is not None and summary_section.text:
            return f"Summary for {medical_term}: {summary_section.text.strip()}"

        description_section = topic_root.find(
            "./description_section/description_content"
        )
        if description_section is not None and description_section.text:
            return f"Explanation for {medical_term}: {description_section.text.strip()}"

        # If specific sections not found, return a generic message with the full topic URL if available
        topic_url = (
            root.find(".//document").get("url")
            if root.find(".//document") is not None
            else "N/A"
        )
        return f"Could not find a specific summary or description for '{medical_term}'. You can find more information at: {topic_url}"

    except ET.ParseError as e:
        return f"Failed to parse XML response for '{medical_term}': {e}"
    except Exception as e:
        return (
            f"An unexpected error occurred during XML parsing for '{medical_term}': {e}"
        )


if __name__ == "__main__":
    mcp.run(transport="stdio")
