import streamlit as st

def upload_to_azure(file, filename,blob_service_client,AZURE_CONTAINER_NAME):
    try:
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=filename)
        blob_client.upload_blob(file, overwrite=True)
        blob_data = blob_client.download_blob().readall()
    
        return True, blob_data
    
    except Exception as e:
        st.error(f"Upload to Azure failed: {e}")
        return False, None