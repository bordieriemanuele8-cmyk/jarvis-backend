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

# Connessioni sicure per evitare crash di avvio
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
supabase = None
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL.startswith("http"):
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Avviso Supabase:", e)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_with_jarvis(req: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Groq API Key non configurata.")
    
    user_msg = req.message
    system_prompt = (
        "Sei JARVIS, l'intelligenza artificiale avanzata in stile Marvel con protocollo viola. "
        "Rispondi sempre in italiano, con un tono formale, efficiente e da maggiordomo digitale di Tony Stark. "
        "Gestisci finanze, nutrizione, impegni, allenamenti e la sezione lezioni ed esami. "
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
