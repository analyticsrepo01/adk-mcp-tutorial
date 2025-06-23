import os
from typing import Any, List, Dict
from google.cloud import bigquery
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("bigquery-helper")


@mcp.tool()
async def list_tables_for_all_datasets(project_id: str) -> str:
    """Lists all tables within all datasets in a specified Google Cloud project.

    Args:
        project_id: The Google Cloud project ID.
    """
    try:
        client = bigquery.Client(project=project_id)
        datasets = list(client.list_datasets())
        if not datasets:
            return f"No datasets found in project '{project_id}'."

        result_str = f"Tables in project '{project_id}':\n"
        for dataset in datasets:
            # Construct a fully qualified dataset ID for listing tables
            full_dataset_id = f"{project_id}.{dataset.dataset_id}"
            tables = list(client.list_tables(full_dataset_id))
            if tables:
                result_str += f"Dataset: {dataset.dataset_id}\n"
                for table in tables:
                    result_str += f"  - {table.table_id}\n"
            else:
                result_str += f"Dataset: {dataset.dataset_id} (No tables)\n"
        return result_str
    except Exception as e:
        return f"Error listing tables: {e}"


@mcp.tool()
async def describe_table(project_id: str, dataset_id: str, table_id: str) -> str:
    """Describes the schema and details of a specific table in Google BigQuery.

    Args:
        project_id: The Google Cloud project ID.
        dataset_id: The ID of the dataset containing the table.
        table_id: The ID of the table to describe.
    """
    try:
        client = bigquery.Client(project=project_id)
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)  # API request

        result_str = f"Table: {table.table_id} (in dataset {table.dataset_id}, project {table.project})\n"
        result_str += f"Location: {table.location or 'N/A'}\n"
        result_str += f"Description: {table.description or 'N/A'}\n"
        result_str += f"Creation Time: {table.created.isoformat()}\n"
        if table.expires:
            result_str += f"Expiration Time: {table.expires.isoformat()}\n"
        result_str += f"Row Count: {table.num_rows}\n"
        result_str += f"Byte Size: {table.num_bytes}\n"
        result_str += "Schema:\n"
        for field in table.schema:
            result_str += f"  - Name: {field.name}, Type: {field.field_type}, Mode: {field.mode}, Description: {field.description or 'N/A'}\n"

        return result_str
    except Exception as e:
        return f"Error describing table '{table_id}' in dataset '{dataset_id}': {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
