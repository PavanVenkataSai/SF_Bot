import os
import requests
import logging
from urllib.parse import quote
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SalesforceQueryExecutor:
    def __init__(self):
        self.base_url = os.getenv("SF_INSTANCE_URL", "https://aws-dev-hc-dev-ed.develop.my.salesforce.com")
        self.api_version = os.getenv("SF_API_VERSION", "v54.0")
        self.client_id = os.getenv("SF_CLIENT_ID")
        self.client_secret = os.getenv("SF_CLIENT_SECRET")
        self.username = os.getenv("SF_USERNAME")
        self.password = os.getenv("SF_PASSWORD")
        self.security_token = os.getenv("SF_SECURITY_TOKEN")
        self.logger = logging.getLogger(__name__)

    def get_access_token(self) -> Optional[str]:
        """ Authenticate with Salesforce and get an access token """
        token_url = f"{self.base_url}/services/oauth2/token"
        payload = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": f"{self.password}{self.security_token}"
        }
        # print(payload)

        response = requests.post(token_url, data=payload)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            self.logger.error(f"Salesforce Authentication Failed: {response.text}")
            return None

    def execute_soql_query(
        self, table_name: str, 
        column_name: List[str], 
        condition_column_name: Optional[List[str]] = None, 
        condition_column_values: Optional[List[str]] = None,
        fetchone: Optional[bool] = False, 
        fetchall: Optional[bool] = False
    ) -> Optional[dict]:
        """
        Generates a Salesforce SOQL SELECT query dynamically.

        Args:
            table_name (str): Salesforce object name (e.g., "Account", "Contact").
            column_name (List[str]): List of fields to retrieve.
            condition_column_name (Optional[List[str]], optional): List of condition field names. Defaults to None.
            condition_column_values (Optional[List[str]], optional): List of corresponding condition values. Defaults to None.
            fetchone (Optional[bool], optional): Flag to fetch only one record. Defaults to False.
            fetchall (Optional[bool], optional): Flag to fetch all records. Defaults to False.

        Returns:
            str: The constructed SOQL SELECT query.
        """
        self.logger.info("Building SOQL query...")
        access_token = self.get_access_token()
        if not access_token:
            return None

        if fetchone and fetchall:
            self.logger.error("Invalid query parameters: fetchone and fetchall cannot be True at the same time.")
            return None

        # Generate SOQL Query
        column_str = ", ".join(column_name)
        if condition_column_name and condition_column_values:
            conditions = []
            for col, val in zip(condition_column_name, condition_column_values):
                if isinstance(val, (int, float)):  # Numeric values should NOT be enclosed in quotes
                    conditions.append(f"{col} = {val}")
                else:  # String values should be enclosed in single quotes
                    conditions.append(f"{col} = '{val}'")

            condition_str = " AND ".join(conditions)
            soql_query = f"SELECT {column_str} FROM {table_name} WHERE {condition_str}"
        else:
            soql_query = f"SELECT {column_str} FROM {table_name}"

        # URL Encode Query
        endpoint = f"{self.base_url}/services/data/{self.api_version}/query?q={quote(soql_query)}"
        # print(endpoint)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            result = response.json()
            records = result.get("records", [])

            if fetchone:
                return records[0] if records else None
            elif fetchall:
                return records
            else:
                return result  # Return full response

        else:
            self.logger.error(f"Salesforce Query Failed: {response.text}")
            return None

# Example Usage:
# executor = SalesforceQueryExecutor()
# result = executor.execute_soql_query(
#     table_name="PNEX__DUPIXENT__c",
#     column_name=["PNEX__Copay_Balance_Bylvay__c"],
#     condition_column_name=["PNEX__Patient_Id_Bylvay__c"],
#     condition_column_values=["P005"],
#     fetchone=True
# )
# print(result)
