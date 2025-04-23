from bot import QueryExtractor
from sf_query_executor import SalesforceQueryExecutor
import time

def main():
    # Step 1: Get user query
    user_query = input("Enter your query: ")
    start = time.time()

    table_name = "PNEX__DUPIXENT__c"  # Default table; modify as needed
    # Step 2: Extract query parameters using QueryExtractor
    query_extractor = QueryExtractor(table_name)
    extracted_query = query_extractor.extract_query_parameters(user_query)
    # print("query came -->/n",extracted_query)


    # Step 3: Extract details from extracted_query
    
    column_names = extracted_query.get("column_names", [])
    condition_columns = extracted_query.get("condition_columns_name", [])
    condition_values = extracted_query.get("condition_columns_values", [])
    # print("Things -->/n",column_names,condition_columns,condition_values)

    # Step 4: Fetch data from Salesforce
    sf_executor = SalesforceQueryExecutor()
    sf_response = sf_executor.execute_soql_query(
        table_name=table_name,
        column_name=column_names,
        condition_column_name=condition_columns,
        condition_column_values=condition_values,
        fetchall=True
    )

    # print("SF response-->/n",sf_response)

    # Step 5: Summarize the retrieved content
    summary = query_extractor.summarize_content(user_query, sf_response)

    # Step 6: Return summary to user
    print("\nSummarized Response:")
    print(summary.content)
    end_time = time.time()
    print("time taken: ",end_time-start)

if __name__ == "__main__":
    main()
