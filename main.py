import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from supabase import create_client, Client

app = FastAPI(title="JARVIS Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Funzione sicura per ottenere il client Supabase senza causare crash all'avvio
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL", "https://gyynkdzsxlwfqtdnitno.supabase.co")
    key = os.getenv("SUPABASE_KEY", "sb_publishable_pdgK3lE8T7LKrPufXZf79A_6BlxqnYL")
    if not url or not url.startswith("http"):
        url = "https://gyynkdzsxlwfqtdnitno.supabase.co"
    return create_client(url, key)

class UserRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "online", "message": "JARVIS OS Backend attivo"}

@app.post("/chat")
def chat_endpoint(req: UserRequest):
    if not groq_client:
        return {"response": "Errore critico: chiave API Groq non configurata su Render, Signore."}

    system_prompt = (
        "Sei JARVIS, l'intelligenza artificiale avanzata di Tony Stark (protocollo grafico viola). "
        "Rispondi sempre in italiano, con un tono formale, brillante, sofisticato e rispettoso, "
        "rivolgendoti all'utente chiamandolo sempre 'Signore'. Fornisci risposte complete, utili e intelligenti."
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        answer = completion.choices[0].message.content
        return {"response": answer}
    except Exception as e:
        return {"response": f"Anomalia nei sistemi Stark: {str(e)}"}
