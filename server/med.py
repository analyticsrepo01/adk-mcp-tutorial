import httpx
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("medlineplus")

API_BASE_URL = "https://wsearch.nlm.nih.gov/ws/query"
USER_AGENT = "MedlinePlusMCP/1.0 (mcp-dev@example.com)"  # Descriptive User-Agent with contact info


@mcp.tool()
async def get_medical_term(term: str) -> str:
    """
    Retrieves the full summary/explanation for a medical term from MedlinePlus.

    Args:
        term: The medical term to search for (e.g., "asthma", "diabetes medicines").
    """
    params = {
        "db": "healthTopics",  # Search English health topics database
        "term": term,
        "rettype": "brief",  # Request brief format which includes the FullSummary directly
        "tool": "MedlinePlusMCP_TermTool",  # Custom tool identifier for API usage tracking
        "email": "mcp-dev@example.com",  # Contact email for API usage
    }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/xml",  # Explicitly request XML response
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                API_BASE_URL, params=params, headers=headers, timeout=30.0
            )
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            root = ET.fromstring(response.text)

            # Find the first <document> element in the response
            document_element = root.find(".//document")

            if document_element is None:
                # No documents found for the given term
                return f"No medical term information found for '{term}'. Please try a different term or check spelling."

            # Find the <content> element with name='FullSummary' within the document
            full_summary_element = document_element.find(
                "./content[@name='FullSummary']"
            )

            if full_summary_element is not None and full_summary_element.text:
                # The summary might contain HTML formatting, returning as is.
                return full_summary_element.text.strip()
            else:
                # A document was found, but no full summary was available in 'brief' format.
                return f"A detailed explanation (full summary) could not be retrieved for '{term}'."

        except httpx.HTTPStatusError as e:
            return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        except httpx.RequestError as e:
            return f"Network error occurred: {e}"
        except ET.ParseError:
            return "Failed to parse XML response from MedlinePlus API. The API might have returned malformed XML."
        except Exception as e:
            return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
