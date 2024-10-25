from fastapi import FastAPI, HTTPException, File, Depends
import google.generativeai as genai
from typing import List, Optional
import KEY as KEY
import json, asyncio
from fastapi.responses import StreamingResponse
from google.api_core.exceptions import ResourceExhausted
from app.loaders import *

app = FastAPI()
model = Loaders.config_model()
genai.configure(api_key=KEY.GEMINI_API_KEY)
prompt_obj = Prompt()

async def json_stream(option: str, text: str, user_query: str):
    global prompt_obj
    max_retries = 3
    retry_delay = 0.2
    for attempt in range(max_retries):
        try:
            for chunk in model.generate_content(**prompt_obj.generate_response(text, option, user_query), stream=True):
                chunk_dict = chunk.to_dict()
                json_chunk = json.dumps(dict(chunk_dict), allow_nan=True, skipkeys=True)
                yield json_chunk
            break
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise HTTPException(status_code=429, detail="API quota exceeded. Please try again later.")

@app.post("/file/upload/")
async def file_upload(body: FileUploadBody = Depends(), files: List[UploadFile] = File(...)):
    return Process.file_upload(body ,files)

@app.post("/file/download/")
async def file_download(body: FileDownloadBody = Depends()):
    user_id = body.user_id
    file_name = body.file_name    

    bucket = Loaders.config_bucket()
    
    destination_file_name = f'{user_id}/{file_name}'
    blob = bucket.blob(destination_file_name)

    # Check if the file exists
    if not blob.exists():
        raise HTTPException(status_code=404, detail=f"File {file_name} not found in bucket.")
    
    try:
        # Download the file as bytes
        file_data = blob.download_as_bytes()

        # Use StreamingResponse to return the file as a response
        return StreamingResponse(io.BytesIO(file_data), media_type="application/octet-stream", headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

@app.post("/file/extract/")
async def file_text_extraction(file: Optional[UploadFile] = File(None)):
    global model
    ext = file.filename.split('.')[-1].lower()
    return Process.extract_text(file, ext, model)

@app.post("/bucket/check/")
async def file_text_extraction(body: FileDownloadBody = Depends()):
    user_id = body.user_id
    file_name = body.file_name    
    bucket = Loaders.config_bucket()
    destination_file_name = f'{user_id}/{file_name}'
    blob = bucket.blob(destination_file_name)
    if blob.exists():
        return {'details': f"{user_id}/{file_name} found.", 'state': 1}
    return {'details': f"{user_id}/{file_name} not found.", 'state': 0}

@app.get("/gemini/")
async def gemini_porcess(body: MainBody = Depends()):
    print("\n\n\n", body.command, body.prompt, body.option, "\n\n\n")
    # if body.prompt is None and body.command is None:
    #     raise HTTPException(status_code=000, detail="Required endpoints.")
    return StreamingResponse(json_stream(body.option, body.prompt, body.command), media_type="application/json")

@app.get("/")
async def root():
    return {
        "message": "Edunote API",
        "description": "Edunote API, uses Gemini by Google to present you the best note taking experience.",
        "endpoints": {
            "/gemini/": {
                "method": "get",
                "description": "Process prompt and user command.",
                "parameters": {
                    "body": {
                        "prompt": "Provide text to Gemini to use options. Defaults to None.",
                        "command": "Ask AI a question about the content. Defaults to None.",
                        "option": {
                            "user" : "Default option. Provide {{commands}}. Feeds Gemini with user query.",
                            "ask" : "Provide {{propmt}} and {{commands}} to ask a question about the text.",
                            "explain" : "Provide {{propmt}}. Gemini explains the text.",
                            "template" : "Provide {{propmt}}. Gemini creates a template of the text.",
                            "summarize" : "Provide {{propmt}}. Gemini summarizes the text.",
                            "note" : "Provide {{propmt}}. Gemini takes notes for you from the text.",
                            "improve" : "Provide {{propmt}}. Gemini improves the text.",
                            "shorter" : "Provide {{propmt}}. Gemini shorters the text.",
                            "longer" : "Provide {{propmt}}. Gemini longers the text.",
                            "continue" : "Provide {{propmt}}. Gemini continues the text.",
                            "fix" : "Provide {{propmt}}. Gemini fixes the text.",
                            "zap" : "Provide {{commands}}. Gemini generates new text from user query."
                        }
                    }
                }
            }
        }
    }
