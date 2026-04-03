from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio

app = FastAPI()

# Allow frontend (Netlify) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

running = False
stats = {"success": 0, "failed": 0}

# Default test APIs (SAFE)
API_1 = "https://jsonplaceholder.typicode.com/posts"
API_2 = "https://jsonplaceholder.typicode.com/comments"

@app.post("/start")
async def start_test(data: dict):
    global running, stats
    running = True
    stats = {"success": 0, "failed": 0}

    mode = data.get("mode", "single")
    total = int(data.get("total", 100))
    concurrency = int(data.get("concurrency", 5))

    async def call_api(session, url):
        try:
            async with session.get(url, timeout=5):
                stats["success"] += 1
        except:
            stats["failed"] += 1

    async def worker():
        async with aiohttp.ClientSession() as session:
            while running and (stats["success"] + stats["failed"]) < total:
                if mode == "multi":
                    await asyncio.gather(
                        call_api(session, API_1),
                        call_api(session, API_2)
                    )
                else:
                    await call_api(session, API_1)

    tasks = [worker() for _ in range(concurrency)]
    await asyncio.gather(*tasks)

    running = False
    return stats

@app.get("/stats")
async def get_stats():
    return stats

@app.post("/stop")
async def stop():
    global running
    running = False
    return {"message": "stopped"}