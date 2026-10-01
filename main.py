import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connessioni
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_with_jarvis(req: ChatRequest):
    user_msg = req.message
    
    system_prompt = (
        "Sei JARVIS, l'intelligenza artificiale avanzata in stile Marvel (con protocollo viola). "
        "Rispondi sempre in italiano, con un tono formale, efficiente e da maggiordomo digitale di Tony Stark. "
        "Gestisci finanze (spese_e_finanze), nutrizione (dieta_e_nutrizione), impegni (impegni_e_task), "
        "allenamenti (allenamenti) e la nuova sezione lezioni ed esami (lezioni_esami). "
        "Se l'utente chiede ricerche online, rispondi integrando informazioni aggiornate."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        answer = completion.choices[0].message.content
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
