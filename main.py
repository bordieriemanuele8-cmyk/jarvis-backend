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

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://gyynkdzsxlwfqtdnitno.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_pdgK3lE8T7LKrPufXZf79A_6BlxqnYL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

class UserRequest(BaseModel):
    message: str

def aggiungi_impegno(titolo: str, categoria: str = "personale", data_ora_inizio: str = None, priorita: str = "media") -> str:
    try:
        data = {"titolo": titolo, "categoria": categoria, "priorita": priorita}
        if data_ora_inizio: data["data_ora_inizio"] = data_ora_inizio
        supabase.table("impegni_e_task").insert(data).execute()
        return f"Impegno salvato: '{titolo}'"
    except Exception as e:
        return f"Errore Supabase: {e}"

def registra_spesa(descrizione: str, importo: float, categoria: str = "altro", tipo: str = "uscita") -> str:
    try:
        data = {"descrizione": descrizione, "importo": importo, "categoria": categoria, "tipo": tipo}
        supabase.table("spese_e_finanze").insert(data).execute()
        return f"Spesa di {importo}€ per '{descrizione}' registrata."
    except Exception as e:
        return f"Errore Supabase: {e}"

def traccia_pasto(alimento_o_pasto: str, calorie: int = 0, proteine_g: float = 0, carboidrati_g: float = 0, grassi_g: float = 0) -> str:
    try:
        data = {"alimento_o_pasto": alimento_o_pasto, "calorie": calorie, "proteine_g": proteine_g, "carboidrati_g": carboidrati_g, "grassi_g": grassi_g}
        supabase.table("dieta_e_nutrizione").insert(data).execute()
        return f"Pasto '{alimento_o_pasto}' ({calorie} kcal) salvato."
    except Exception as e:
        return f"Errore Supabase: {e}"

def registra_allenamento(nome_allenamento: str, durata_minuti: int = 0, dettaglio_esercizi: str = "") -> str:
    try:
        data = {"nome_allenamento": nome_allenamento, "durata_minuti": durata_minuti, "dettaglio_esercizi": {"note": dettaglio_esercizi}}
        supabase.table("allenamenti").insert(data).execute()
        return f"Allenamento '{nome_allenamento}' salvato."
    except Exception as e:
        return f"Errore Supabase: {e}"

def consulta_spese(limite: int = 10) -> str:
    try:
        res = supabase.table("spese_e_finanze").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore lettura spese: {e}"

def consulta_pasti(limite: int = 10) -> str:
    try:
        res = supabase.table("dieta_e_nutrizione").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore lettura pasti: {e}"

def consulta_impegni(limite: int = 10) -> str:
    try:
        res = supabase.table("impegni_e_task").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore lettura impegni: {e}"

def consulta_allenamenti(limite: int = 10) -> str:
    try:
        res = supabase.table("allenamenti").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore lettura allenamenti: {e}"

TOOLS_MAP = {
    "aggiungi_impegno": aggiungi_impegno,
    "registra_spesa": registra_spesa,
    "traccia_pasto": traccia_pasto,
    "registra_allenamento": registra_allenamento,
    "consulta_spese": consulta_spese,
    "consulta_pasti": consulta_pasti,
    "consulta_impegni": consulta_impegni,
    "consulta_allenamenti": consulta_allenamenti
}

tools = [
    {"type": "function", "function": {"name": "registra_spesa", "description": "Registra spesa/entrata", "parameters": {"type": "object", "properties": {"descrizione": {"type": "string"}, "importo": {"type": "number"}, "categoria": {"type": "string"}, "tipo": {"type": "string", "enum": ["entrata", "uscita"]}}, "required": ["descrizione", "importo"]}}},
    {"type": "function", "function": {"name": "traccia_pasto", "description": "Traccia cibo e calorie", "parameters": {"type": "object", "properties": {"alimento_o_pasto": {"type": "string"}, "calorie": {"type": "integer"}, "proteine_g": {"type": "number"}, "carboidrati_g": {"type": "number"}, "grassi_g": {"type": "number"}}, "required": ["alimento_o_pasto"]}}},
    {"type": "function", "function": {"name": "aggiungi_impegno", "description": "Aggiunge task/impegno", "parameters": {"type": "object", "properties": {"titolo": {"type": "string"}, "categoria": {"type": "string"}, "priorita": {"type": "string"}}, "required": ["titolo"]}}},
    {"type": "function", "function": {"name": "registra_allenamento", "description": "Registra allenamento", "parameters": {"type": "object", "properties": {"nome_allenamento": {"type": "string"}, "durata_minuti": {"type": "integer"}, "dettaglio_esercizi": {"type": "string"}}, "required": ["nome_allenamento"]}}},
    {"type": "function", "function": {"name": "consulta_spese", "description": "Legge le ultime spese", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "consulta_pasti", "description": "Legge i pasti registrati", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "consulta_impegni", "description": "Legge gli impegni", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "consulta_allenamenti", "description": "Legge gli allenamenti", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}}
]

@app.get("/")
def home():
    return {"status": "online", "message": "JARVIS OS Backend attivo"}

@app.post("/chat")
def chat_endpoint(req: UserRequest):
    messages = [
        {
            "role": "system",
            "content": "Sei JARVIS, l'assistente personale dell'utente. Gestisci spese, nutrizione, allenamenti e impegni usando le funzioni di lettura e scrittura sul database."
        },
        {"role": "user", "content": req.message}
    ]

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response_message = response.choices[0].message

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
            if fn_name in TOOLS_MAP:
                risultato = TOOLS_MAP[fn_name](**fn_args)
                messages.append(response_message)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(risultato)})

        seconda_risposta = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages
        )
        return {"response": seconda_risposta.choices[0].message.content}

    return {"response": response_message.content or "Nessuna risposta generata."}
