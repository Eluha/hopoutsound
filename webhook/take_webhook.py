from fastapi import FastAPI, Request, HTTPException
import hmac, hashlib, os, asyncpg
from dotenv import load_dotenv
from datetime import datetime
import aiohttp

load_dotenv()
app = FastAPI()

# Секрет для верификации вебхука
SECRET = os.getenv("TRIBUTE_SECRET_KEY_VASIL")

# Параметры подключения к PostgreSQL
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
}



# Функция подключения к БД
async def get_db():
    return await asyncpg.connect(**DB_CONFIG)

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("trbt-signature", "")
    # Подпись Tribute (HMAC SHA256)
    computed = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, signature):
        print('[WARNING] Пришел левый запрос')
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Запись в БД
    try:
        data = await request.json()
        payload = data.get("payload", {})
        if not payload:
            print("[WARNING] Пустой payload в теле запроса")
        else:
            event_name = data.get("name", "unknown_event")
            created_at_str = data.get("created_at")
            sent_at_str = data.get("sent_at")

            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.utcnow()
            sent_at = datetime.fromisoformat(sent_at_str.replace("Z", "+00:00")) if sent_at_str else datetime.utcnow()

            donation_request_id = payload.get("donation_request_id", None)
            donation_name = payload.get("donation_name", "")
            message = payload.get("message", "")
            period = payload.get("period", "")
            amount = payload.get("amount", 0)
            currency = payload.get("currency", "")
            anonymously = payload.get("anonymously", False)
            web_app_link = payload.get("web_app_link", "")
            user_id = payload.get("user_id", None)
            telegram_user_id = payload.get("telegram_user_id", None)

        conn = await get_db()
        await conn.execute(
            """
            INSERT INTO donations (
                event_name, created_at, sent_at,
                donation_request_id, donation_name, message, period,
                amount, currency, anonymously, web_app_link,
                user_id, telegram_user_id
            ) VALUES (
                $1, $2, $3,
                $4, $5, $6, $7,
                $8, $9, $10, $11,
                $12, $13
            )
            """,
            event_name, created_at, sent_at,
            donation_request_id, donation_name, message, period,
            amount, currency, anonymously, web_app_link,
            user_id, telegram_user_id
        )
        await conn.close()

        print(f"[OK] Добавлено пожертвование от пользователя {telegram_user_id} на сумму {amount} {currency}", flush=True)

        if telegram_user_id:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url="http://bot:8001/send_pdf",
                    json={"telegram_id": telegram_user_id, "amount": amount}
                ) as resp:
                    print(f"[PDF] Ответ от бота: {resp.status}", flush=True)

    except Exception as e:
        print(f"[ERROR] DB error: {e}", flush=True)
        raise HTTPException(status_code=500, detail="DB write failed")