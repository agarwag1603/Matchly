from io import BytesIO
from PyPDF2 import PdfReader

def extract_text_from_pdf(blob_data):
# Convert to file-like object for PyPDF2
    #pdf_stream = BytesIO(blob_data)

    try:
        reader = PdfReader(blob_data)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                cleaned_text = page_text.strip()
                text += cleaned_text + "\n"
        return text if text.strip() else None
    except Exception as e:
        print(f"PDF parsing failed: {e}")
        return None
    
# Step 2: Send to Azure OpenAI to extract structured info
def extract_resume_info(text,client, deployment,prompt): 
    prompt =f'''
        {prompt}
        {text}
    '''

    messages = [
        {"role": "user", "content": prompt}]

    completion = client.chat.completions.create(
    model=deployment,
    messages=messages,
    max_tokens=2000,
    temperature=0.0,
    top_p=1.0,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False
) 
    response_content = completion.choices[0].message.content
    print(response_content)
    return response_content