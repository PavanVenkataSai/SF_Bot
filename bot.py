from langchain_aws import ChatBedrock
import boto3
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Get AWS credentials from .env
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

fields = {
    "PNEX__DUPIXENT__c":['Id', 'Name', 'PNEX__Patient_Id_Bylvay__c', 'PNEX__Benefit_Verification_Status_Bylvay__c', 'PNEX__Benefit_Verification_Start_Date_Bylvay__c', 'PNEX__Benefit_Verification_End_Date_Bylvay__c', 'PNEX__PA_Status_Bylvay__c', 'PNEX__Drug_Quantity_Bylvay__c', 'PNEX__PA_Request_Date_Bylvay__c', 'PNEX__PA_Response_Date_Bylvay__c', 'PNEX__Copay_Balance_Bylvay__c', 'PNEX__HCP_Name_Bylvay__c', 'PNEX__HCP_ID_Bylvay__c'],
    
    "PNEX__PRALUENT__c":['Id','Name',  'PNEX__Patient_Id_Iqirvo__c', 'PNEX__Benefit_Verification_End_Date_Iqirvo__c', 'PNEX__Benefit_Verification_Start_Date_Iqirvo__c', 'PNEX__Benefit_Verification_Status_Iqirvo__c', 'PNEX__PA_Status_Iqirvo__c', 'PNEX__PA_Request_Date_Iqirvo__c', 'PNEX__PA_Response_Date_Iqirvo__c', 'PNEX__Drug_Quantity_Iqirvo__c', 'PNEX__Copay_Balance_Iqirvo__c', 'PNEX__HCP_Name_Iqirvo__c', 'PNEX__HCP_ID_Iqirvo__c']
}


# Define the Pydantic model for JSON output
class TransformedQueriesJson(BaseModel):
    condition_columns_values: list = Field(description="List of all conditioned values")
    condition_columns_name: list = Field(description="List of all conditioned columns")
    column_names: list = Field(description="List of all the columns user wants to retrieve")

class QueryExtractor:
    def __init__(self, table_name: str):
        if table_name not in fields:
            raise ValueError(f"Invalid table name: {table_name}")
        
        self.table_name = table_name
        self.llm = self.call_bedrock()
        self.transformed_queries_parser = JsonOutputParser(pydantic_object=TransformedQueriesJson)
        self.query_transform_prompt = self.create_prompt()

    def call_bedrock(self):
        """Initialize the Bedrock LLM model."""
        try:
            bedrock_runtime = boto3.client(
                service_name="bedrock-runtime",
                region_name="us-east-1",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )

            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
            model_kwargs = {"max_tokens": 512, "temperature": 0.3}

            return ChatBedrock(client=bedrock_runtime, model_id=model_id, model_kwargs=model_kwargs)
        
        except Exception as error:
            raise Exception(f"Error in connecting to AWS Bedrock: {error}")

    def create_prompt(self):
        """Create the prompt template for Bedrock LLM."""
        return PromptTemplate(
            template=(
                "Analyze the user query and extract the relevant details based on the available column list. Identify:\n"
                "1. The exact column names that should be retrieved.\n"
                "2. The condition column names on which the query is based.\n"
                "3. The values for the condition columns.\n\n"
                "Use the following column list for reference:\n"
                "{bylvay_columns}\n\n"
                "Provide the output in dictionary format with keys:\n"
                "column_names = <List of columns to retrieve>\n"
                "condition_columns_name = <List of columns used for filtering>\n"
                "condition_columns_values = <List of values for filtering>\n\n"
                "User Query: {question}\n"
                "NOTE: Do not include any explanation just provide the output as per {format_instructions}\n\n"
            ),
            input_variables=["question"],
            partial_variables={
                "bylvay_columns": fields[self.table_name],
                "format_instructions": self.transformed_queries_parser.get_format_instructions()
            },
        )

    def extract_query_parameters(self, user_query):
        """Extract structured query parameters from user input using AWS Bedrock."""
        clean_query_chain = self.query_transform_prompt | self.llm | self.transformed_queries_parser
        return clean_query_chain.invoke({'question': user_query})
    
    def summarize_content(self, user_query, sf_data):
        """Summarizes the retrieved Salesforce content."""

        prompt = PromptTemplate(
            template=(
            "Given the user query:\n{user_query}\n\n"
            "And the retrieved Salesforce data:\n{sf_data}\n\n"
            "Generate a concise summary relevant to the query."
        ),
            input_variables=["user_query","sf_data"]
        )

        clean_query_chain = prompt | self.llm
        return clean_query_chain.invoke({'user_query': user_query,"sf_data":sf_data})


# query_extracter = QueryExtractor("PNEX__PRALUENT__c")
# print(query_extracter.extract_query_parameters("What is the copay balance for the patient P005?"))
# print(query_extracter.summarize_content('What is the copay balance for the patient P005?',{'attributes': {'type': 'PNEX__Bylvay__c', 'url': '/services/data/v54.0/sobjects/PNEX__Bylvay__c/a2eHn000004ZA85IAG'}, 'PNEX__Copay_Balance_Bylvay__c': 30.0}))