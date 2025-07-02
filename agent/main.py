from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import run_agent

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    content: str
    slots: list = []

@app.post("/run", response_model=AgentResponse)
def run_prompt(req: PromptRequest):
    """
    Accepts a JSON body {"prompt": "..."} and returns {'content': ..., 'slots': [...]}.
    """
    try:
        result = run_agent(req.prompt)
        if isinstance(result, dict) and 'content' in result:
            return {'content': result['content'], 'slots': result.get('slots', [])}
        else:
            return {'content': str(result), 'slots': []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))