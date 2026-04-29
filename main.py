from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import os
from datetime import datetime

app = FastAPI()

HISTORY_FILE = "car_history.json"


class ValkyrieEngine:
    def __init__(self):
        self.active = False
        self.speed = 0.0
        self.score = 0.0
        self.lane = 0.0
        self.distance = 0.0
        self.boost_cooldown = 0
        self.boost_active = False
        self.boost_time = 0
        self.lives = 3
        self.base_speed = 1.2
        self.max_speed = 10.0
        self.race_length = 15000.0

    def reset(self):
        self.active = True
        self.speed = self.base_speed
        self.score = 0.0
        self.lane = 0.0
        self.distance = 0.0
        self.boost_cooldown = 0
        self.boost_active = False
        self.boost_time = 0
        self.lives = 3

    def handle_input(self, action: str):
        if action == "left":
            self.lane = max(self.lane - 1.5, -8.0)
        elif action == "right":
            self.lane = min(self.lane + 1.5, 8.0)
        elif action == "boost":
            if self.boost_cooldown <= 0:
                self.boost_active = True
                self.boost_time = 120
                self.boost_cooldown = 300

    def tick(self):
        if not self.active:
            return

        # Boost logic
        if self.boost_active:
            self.boost_time -= 1
            if self.boost_time <= 0:
                self.boost_active = False
        else:
            if self.boost_cooldown > 0:
                self.boost_cooldown -= 1

        # Target speed
        progress = self.distance / self.race_length
        target = self.base_speed + progress * 6
        if self.boost_active:
            target = self.max_speed

        # Smooth acceleration
        self.speed += (target - self.speed) * 0.03
        self.speed = min(self.speed, self.max_speed)

        # Update distance and score
        self.distance += self.speed * 1.2
        self.score += self.speed * 0.1

        # Win condition
        if self.distance >= self.race_length:
            self.active = False
            self.log_history(won=True)
            return "won"

        return "racing"

    def log_history(self, won=False):
        history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append({
            "car": "Valkyrie_AMR_Pro",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": int(self.score),
            "max_speed": int(self.speed * (350 / 14)),
            "distance": int(self.distance),
            "result": "WIN" if won else "DNF"
        })
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

    def get_state(self):
        gear = 1
        s = self.speed
        if s < 3: gear = 1
        elif s < 6: gear = 2
        elif s < 9: gear = 3
        elif s < 12: gear = 4
        else: gear = 5
        if self.boost_active:
            gear_display = "B"
        else:
            gear_display = str(gear)

        return {
            "speed": int(self.speed * (350 / 14)),
            "score": int(self.score),
            "lane": round(self.lane, 2),
            "distance": int(self.distance),
            "lives": self.lives,
            "boost_active": self.boost_active,
            "boost_cooldown": self.boost_cooldown,
            "gear": gear_display,
            "active": self.active
        }


engine = ValkyrieEngine()


@app.get("/")
async def root():
    return FileResponse("index.html")


@app.get("/history")
async def get_history():
    if not os.path.exists(HISTORY_FILE):
        return {"history": []}
    with open(HISTORY_FILE, "r") as f:
        return {"history": json.load(f)}


@app.websocket("/ws")
async def game_socket(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")
    try:
        while True:
            # Non-blocking input read
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                data = json.loads(raw)
                action = data.get("action", "")

                if action == "start":
                    engine.reset()
                    print("Race started")
                elif action in ("left", "right", "boost"):
                    engine.handle_input(action)
                elif action == "stop":
                    engine.log_history(won=False)
                    engine.active = False
                    print("Race stopped")
                elif action == "collision":
                    engine.lives -= 1
                    engine.speed *= 0.4
                    if engine.lives <= 0:
                        engine.active = False
                        engine.log_history(won=False)

            except asyncio.TimeoutError:
                pass
            except json.JSONDecodeError:
                pass

            # Tick engine and send state
            if engine.active:
                result = engine.tick()
                state = engine.get_state()
                state["status"] = result if result else "racing"
                await websocket.send_text(json.dumps(state))
            else:
                # Send idle state
                await websocket.send_text(json.dumps({
                    **engine.get_state(),
                    "status": "idle"
                }))

            await asyncio.sleep(0.03)  # ~33fps tick rate

    except WebSocketDisconnect:
        print("Client disconnected")
        if engine.active:
            engine.log_history(won=False)
            engine.active = False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)