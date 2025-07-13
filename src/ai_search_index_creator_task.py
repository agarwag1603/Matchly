from azure.search.documents.indexes.models import (
   SearchIndex,
   SimpleField,
   SearchableField,
   SemanticConfiguration,
   SemanticField,
   SemanticSearch,
   SemanticPrioritizedFields
)
 
from azure.core.exceptions import ResourceNotFoundError
import base64
import json
 
def create_search_index(index_client,index_name):
    # Define fields for the index
    fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="FullName", type="Edm.String"),
    SearchableField(name="Email", type="Edm.String"),
    SearchableField(name="Phone", type="Edm.String"),
    SearchableField(name="Location", type="Edm.String"),
    SearchableField(name="Skills", type="Edm.String"),
    SearchableField(name="Certifications", type="Collection(Edm.String)"),
    SearchableField(name="Education", type="Edm.String"),  # JSON string of list of dicts
    SearchableField(name="WorkExperience", type="Edm.String"),  # JSON string of list of dicts
    SearchableField(name="ProfileSummary", type="Edm.String")]
   
    semantic_config = SemanticConfiguration(name="semantic-config-search",
                                           prioritized_fields=SemanticPrioritizedFields(
       title_field=SemanticField(field_name="ProfileSummary"),
       keywords_fields=[SemanticField(field_name="ProfileSummary"),SemanticField(field_name="Skills"),
                        SemanticField(field_name="Location"),SemanticField(field_name="WorkExperience")],
       content_fields=[SemanticField(field_name="ProfileSummary"),SemanticField(field_name="Skills"),
                        SemanticField(field_name="Location"),SemanticField(field_name="WorkExperience")]))
   
   
   
    semantic_settings = SemanticSearch(configurations=[semantic_config])
    # Define the index
    index = SearchIndex(name=index_name, fields=fields,semantic_search=semantic_settings)
 
    try:
        # Check if the index already exists
        index_client.get_index(index_name)
        print(f"Index '{index_name}' already exists.")
    except ResourceNotFoundError:
        # If the index doesn't exist, create it
        index_client.create_or_update_index(index)
        print(f"Index '{index_name}' created successfully!")
 
def upload_to_search_index(extracted_data, filename, search_client):
 
    # Format the document for Azure Search
    safe_filename = base64.urlsafe_b64encode(filename.encode()).decode().strip("=")
    def safe_get(value, fallback):
        return fallback if value is None else value
 
    document = {
        "id": safe_filename,
        "FullName": safe_get(extracted_data.get("Full Name"), "N/A"),
        "Email": safe_get(extracted_data.get("Email"), "N/A"),
        "Phone": safe_get(extracted_data.get("Phone"), "N/A"),
        "Location": safe_get(extracted_data.get("Location"), "N/A"),
        "Skills": safe_get(extracted_data.get("Skills"), "N/A"),
        "Certifications": safe_get(extracted_data.get("Certifications"), "N/A"),
        "Education": json.dumps(safe_get(extracted_data.get("Education"), [])),
        "WorkExperience": json.dumps(safe_get(extracted_data.get("Work Experience"), [])),
        "ProfileSummary": safe_get(extracted_data.get("Profile Summary"), "N/A")
        }
 
   
    #Upload document to the search index
    search_client.upload_documents(documents=[document])
 
def create_search_index_jd(index_client,index_name):
    # Define fields for the index
    fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="JobRole", type="Edm.String"),
    SearchableField(name="Skills", type="Edm.String"),
    SearchableField(name="Location", type="Edm.String"),
    SearchableField(name="JDSummary", type="Edm.String"),
    SearchableField(name="JobReference", type="Edm.String"),
    SearchableField(name="CorporateTitle", type="Edm.String"),
    SearchableField(name="BusinessUnit", type="Edm.String"),
    SearchableField(name="BusinessSector", type="Edm.String"),
    SearchableField(name="BusinessSegment", type="Edm.String")
    ]
 
    semantic_config = SemanticConfiguration(name="semantic-config-search-jd",
                                           prioritized_fields=SemanticPrioritizedFields(
       title_field=SemanticField(field_name="JDSummary"),
       keywords_fields=[SemanticField(field_name="JDSummary"),SemanticField(field_name="Skills"),
                        SemanticField(field_name="JobRole"),SemanticField(field_name="Location"),
                        SemanticField(field_name="JobReference"),SemanticField(field_name="CorporateTitle"),
                        SemanticField(field_name="BusinessUnit"),SemanticField(field_name="BusinessSector"),
                        SemanticField(field_name="BusinessSegment")],
       content_fields=[SemanticField(field_name="JDSummary"),SemanticField(field_name="Skills"),
                        SemanticField(field_name="JobRole"),SemanticField(field_name="Location"),
                        SemanticField(field_name="JobReference"),SemanticField(field_name="CorporateTitle"),
                        SemanticField(field_name="BusinessUnit"),SemanticField(field_name="BusinessSector"),
                        SemanticField(field_name="BusinessSegment")]))
   
    semantic_settings = SemanticSearch(configurations=[semantic_config])
    # Define the index
    index = SearchIndex(name=index_name, fields=fields,semantic_search=semantic_settings)
 
    try:
        # Check if the index already exists
        index_client.get_index(index_name)
        print(f"Index '{index_name}' already exists.")
    except ResourceNotFoundError:
        # If the index doesn't exist, create it
        index_client.create_or_update_index(index)
        print(f"Index '{index_name}' created successfully!")
 
def upload_to_search_index_jd(extracted_data, filename, search_client):
 
    # Format the document for Azure Search
    safe_filename = base64.urlsafe_b64encode(filename.encode()).decode().strip("=")
    def safe_get(value, fallback):
        return fallback if value is None else value
 
    document = {
        "id": safe_filename,
        "JobRole": safe_get(extracted_data.get("JobRole"), "N/A"),
        "Skills": safe_get(extracted_data.get("Skills"), "N/A"),
        "Location": json.dumps(safe_get(extracted_data.get("Location"), [])),
        "JDSummary": json.dumps(safe_get(extracted_data.get("JDSummary"), [])),
        "JobReference": safe_get(extracted_data.get("JobReference"), "N/A"),
        "CorporateTitle": safe_get(extracted_data.get("CorporateTitle"), "N/A"),
        "BusinessUnit": safe_get(extracted_data.get("BusinessUnit"), "N/A"),
        "BusinessSector": safe_get(extracted_data.get("BusinessSector"), "N/A"),
        "BusinessSegment": safe_get(extracted_data.get("BusinessSegment"), "N/A")
        }
   
    #flattened_skills = [skill for sublist in document["Skills"].values() for skill in sublist]
    #document["Skills"] = flattened_skills
    print(document["Skills"])
    print(document)
 
    #Upload document to the search index
    result = search_client.upload_documents(documents=[document])
 
    if result[0].succeeded:
        print(f"Document for {filename} uploaded successfully!")
    else:
        print(f"Failed to upload document for {filename}")


