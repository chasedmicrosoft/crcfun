import logging
import azure.functions as func
from azure.data.tables import TableServiceClient, UpdateMode
import os

# Retrieve the connection string from environment variables
TABLE_CONNECTION_STRING = os.getenv('TABLE_CONNECTION_STRING')
TABLE_NAME = "VisitorCount"

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
@app.queue_output(arg_name="msg", queue_name="outqueue", connection="AzureWebJobsStorage")
def HttpExample(req: func.HttpRequest, msg: func.Out[func.QueueMessage]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Initialize TableServiceClient
    table_service = TableServiceClient.from_connection_string(conn_str=TABLE_CONNECTION_STRING)
    table_client = table_service.get_table_client(table_name=TABLE_NAME)

    partition_key = "visitors"
    row_key = "total"
    
    try:
        # Check if table exists
        try:
            # Check if the table exists
            table_client.get_entity(partition_key=partition_key, row_key=row_key)
            entity_exists = True
        except HttpResponseError as e:
            if e.status_code == 404:
                # Table or entity does not exist, create the table and entity
                table_client.create_table()
                table_client.create_entity(
                    entity={
                        'PartitionKey': partition_key,
                        'RowKey': row_key,
                        'count': 1
                    }
                )
                entity_exists = False
                logging.info("Table and entity created.")
            else:
                raise

        if entity_exists:
            # Retrieve the existing entity
            entity = table_client.get_entity(partition_key=partition_key, row_key=row_key)
            current_count = int(entity['count'])
            new_count = current_count + 1
            
            # Update the entity using REPLACE mode
            updated_entity = {
                'PartitionKey': partition_key,
                'RowKey': row_key,
                'count': new_count
            }
            table_client.update_entity(
                mode=UpdateMode.REPLACE,
                entity=updated_entity
            )
        else:
            new_count = 1  # If the entity was just created

        # Process input and set message to queue
        name = req.params.get('name')
        if not name:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                name = req_body.get('name')

        if name:
            msg.set(name)  # Write message to the queue
            response_message = f"Hello, {name}. This HTTP triggered function executed successfully."
        else:
            response_message = "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."

        # Include visitor count in the response
        return func.HttpResponse(f"{response_message} Visitor Count: {new_count}", status_code=200)
    
    except Exception as e:
        logging.error(f"Error processing visitor count: {e}")
        return func.HttpResponse(f"Error processing visitor count: {e}", status_code=500)
