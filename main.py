import os
import json
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

# Recupero variabili d'ambiente con fallback di sicurezza
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gyynkdzsxlwfqtdnitno.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_pdgK3lE8T7LKrPufXZf79A_6BlxqnYL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Inizializzazione sicura dei client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class UserRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "online", "message": "JARVIS OS Backend attivo con Supabase e Groq"}

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
            model="llama3-70b-8192",  # Modello stabile e pienamente supportato
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
