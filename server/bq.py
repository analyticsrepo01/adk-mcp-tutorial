from typing import Any
from mcp.server.fastmcp import FastMCP
from google.cloud import bigquery

mcp = FastMCP("google_bigquery_server")


@mcp.tool()
async def list_tables(project_id: str, location: str) -> str:
    """List all tables for all datasets in a given Google Cloud BigQuery project.

    Args:
        project_id: The Google Cloud project ID.
        location: The location of the BigQuery datasets (e.g., us-central1, europe-west2).
    """
    try:
        client = bigquery.Client(project=project_id)
        datasets = list(client.list_datasets(project=project_id))

        if not datasets:
            return f"No datasets found in project {project_id}."

        output = []
        for dataset in datasets:
            dataset_id = dataset.dataset_id
            tables = list(client.list_tables(dataset_id))
            output.append(f"Dataset: {dataset_id}")
            if tables:
                for table in tables:
                    output.append(f"  - Table: {table.table_id}")
            else:
                output.append("  No tables found in this dataset.")
        return "\n".join(output)
    except Exception as e:
        return f"Error listing tables: {e}"


@mcp.tool()
async def describe_table(
    project_id: str, location: str, dataset_id: str, table_id: str
) -> str:
    """Describe a specific table in a Google Cloud BigQuery dataset.

    Args:
        project_id: The Google Cloud project ID.
        location: The location of the BigQuery dataset (e.g., us-central1, europe-west2).
        dataset_id: The ID of the dataset containing the table.
        table_id: The ID of the table to describe.
    """
    try:
        client = bigquery.Client(project=project_id)
        table_ref = client.dataset(dataset_id, project=project_id).table(table_id)
        table = client.get_table(table_ref)

        output = [
            f"Table: {table.table_id} (in dataset {table.dataset_id}, project {table.project})"
        ]
        output.append(f"Description: {table.description or 'N/A'}")
        output.append("Schema:")
        for field in table.schema:
            output.append(f"  - {field.name}: {field.field_type} ({field.mode})")
        return "\n".join(output)
    except Exception as e:
        return f"Error describing table {table_id} in dataset {dataset_id}: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
