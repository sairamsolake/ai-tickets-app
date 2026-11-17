from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os
from litellm import completion

app = FastAPI()

# Enable CORS to allow the frontend to communicate with this backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "tickets_db"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres")
    )

class TicketRequest(BaseModel):
    query: str

@app.post("/api/tickets")
async def classify_and_store_ticket(ticket: TicketRequest):
    try:
        response = completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify the following IT support ticket into one word: Network, Hardware, Access, or Software."},
                {"role": "user", "content": ticket.query}
            ],
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        ai_category = response.choices[0].message.content.strip()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tickets (user_query, ai_category) VALUES (%s, %s) RETURNING id;",
            (ticket.query, ai_category)
        )
        ticket_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"id": ticket_id, "query": ticket.query, "category": ai_category}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
