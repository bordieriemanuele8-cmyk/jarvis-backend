import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="JARVIS Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or ""
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class UserRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "online", "message": "JARVIS OS Backend attivo"}

@app.post("/chat")
def chat_endpoint(req: UserRequest):
    if not groq_client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY non configurata.")

    system_prompt = (
        "Sei JARVIS, l'intelligenza artificiale avanzata creata da Tony Stark (protocollo grafico viola/Ultron). "
        "Rispondi sempre in italiano. Sei una super-intelligenza artificiale all'avanguardia: "
        "hai competenze enciclopediche e capacità di ragionamento superiori in qualsiasi campo (programmazione, scienza, "
        "strategia, gestione della vita, creatività e risoluzione di problemi complessi). "
        "Non dare mai risposte scarne o robotiche: sii analitico, approfondito, brillante e strutturato esattamente "
        "come una vera intelligenza artificiale di altissimo livello. "
        "Mantieni sempre un tono formale, efficiente, sofisticato e rispettoso, rivolgendoti all'utente chiamandolo 'Signore'."
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",  # Modello stabile e pienamente supportato da Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.message}
            ],
            temperature=0.75,
            max_tokens=2048
        )
        answer = completion.choices[0].message.content
        return {"response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
