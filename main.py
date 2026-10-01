import json
from groq import Groq
from supabase import create_client, Client

SUPABASE_URL = "https://gyynkdzsxlwfqtdnitno.supabase.co"
SUPABASE_KEY = "sb_publishable_pdgK3lE8T7LKrPufXZf79A_6BlxqnYL"
GROQ_API_KEY = "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"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 1. FUNZIONI DI SCRITTURA (INSERT)
# ==========================================
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

# ==========================================
# 2. FUNZIONI DI LETTURA (SELECT)
# ==========================================
def consulta_spese(limite: int = 10) -> str:
    try:
        res = supabase.table("spese_e_finanze").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore durante la lettura delle spese: {e}"

def consulta_pasti(limite: int = 10) -> str:
    try:
        res = supabase.table("dieta_e_nutrizione").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore durante la lettura della dieta: {e}"

def consulta_impegni(limite: int = 10) -> str:
    try:
        res = supabase.table("impegni_e_task").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore durante la lettura degli impegni: {e}"

def consulta_allenamenti(limite: int = 10) -> str:
    try:
        res = supabase.table("allenamenti").select("*").order("created_at", desc=True).limit(limite).execute()
        return json.dumps(res.data, ensure_ascii=False)
    except Exception as e:
        return f"Errore durante la lettura degli allenamenti: {e}"

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

# ==========================================
# 3. SCHEMA TOOL COMPLETO
# ==========================================
tools = [
    # WRITE TOOLS
    {"type": "function", "function": {"name": "registra_spesa", "description": "Registra spesa/entrata", "parameters": {"type": "object", "properties": {"descrizione": {"type": "string"}, "importo": {"type": "number"}, "categoria": {"type": "string"}, "tipo": {"type": "string", "enum": ["entrata", "uscita"]}}, "required": ["descrizione", "importo"]}}},
    {"type": "function", "function": {"name": "traccia_pasto", "description": "Traccia cibo e calorie", "parameters": {"type": "object", "properties": {"alimento_o_pasto": {"type": "string"}, "calorie": {"type": "integer"}, "proteine_g": {"type": "number"}, "carboidrati_g": {"type": "number"}, "grassi_g": {"type": "number"}}, "required": ["alimento_o_pasto"]}}},
    {"type": "function", "function": {"name": "aggiungi_impegno", "description": "Aggiunge task/impegno", "parameters": {"type": "object", "properties": {"titolo": {"type": "string"}, "categoria": {"type": "string"}, "priorita": {"type": "string"}}, "required": ["titolo"]}}},
    {"type": "function", "function": {"name": "registra_allenamento", "description": "Registra allenamento", "parameters": {"type": "object", "properties": {"nome_allenamento": {"type": "string"}, "durata_minuti": {"type": "integer"}, "dettaglio_esercizi": {"type": "string"}}, "required": ["nome_allenamento"]}}},
    # READ TOOLS
    {"type": "function", "function": {"name": "consulta_spese", "description": "Legge gli ultimi record delle spese dal database", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "consulta_pasti", "description": "Legge gli ultimi pasti e calorie registrati dal database", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "consulta_impegni", "description": "Legge la lista dei prossimi impegni e task dal database", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}},
    {"type": "function", "function": {"name": "consulta_allenamenti", "description": "Legge gli ultimi allenamenti registrati dal database", "parameters": {"type": "object", "properties": {"limite": {"type": "integer"}}}}}
]

# Inizializzazione Cronologia Conversazione
cronologia_chat = [
    {
        "role": "system",
        "content": (
            "Sei JARVIS, l'assistente personale dell'utente. "
            "Hai accesso completo al database Supabase sia in lettura che in scrittura. "
            "Se l'utente ti chiede informazioni su cosa ha speso, mangiato o fatto, usa le funzioni 'consulta_*' "
            "per leggere i dati reali e poi rispondi sintetizzando i risultati con precisione."
        )
    }
]

def invia_a_jarvis(prompt: str):
    # Aggiunge il messaggio utente alla memoria
    cronologia_chat.append({"role": "user", "content": prompt})

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=cronologia_chat,
            tools=tools,
            tool_choice="auto"
        )
    except Exception as e:
        print(f"⚠️ Errore durante l'invio: {e}")
        return

    response_message = response.choices[0].message
    cronologia_chat.append(response_message)

    # Gestione Chiamata Funzioni (Tool Calling)
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
            
            if fn_name in TOOLS_MAP:
                risultato_tool = TOOLS_MAP[fn_name](**fn_args)
                print(f"[JARVIS BACKEND]: Eseguito {fn_name}")

                # Risponde alla chat col risultato del database
                cronologia_chat.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(risultato_tool)
                })

        # Chiamata secondaria per far analizzare i dati a JARVIS e generare la risposta finale
        seconda_risposta = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=cronologia_chat
        )
        testo_finale = seconda_risposta.choices[0].message.content
        cronologia_chat.append({"role": "assistant", "content": testo_finale})
        print(f"\nJARVIS: {testo_finale}")

    elif response_message.content:
        print(f"\nJARVIS: {response_message.content}")

print("🤖 JARVIS 2.0 (Lettura + Scrittura + Memoria) attivo! Scrivi un messaggio:")
while True:
    user_input = input("\nTu: ")
    if user_input.lower() in ["exit", "esci", "quitta"]:
        print("JARVIS disattivato.")
        break
    if user_input.strip():
        invia_a_jarvis(user_input)
