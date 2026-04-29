#  Valkyrie: Apex Racing Engine

A high-performance 3D racing simulator featuring the Aston Martin Valkyrie. This project utilizes a Python-based physics engine and a Three.js frontend to deliver a real-time racing experience.

##  Features
- **Real-Time Physics:** Powered by a FastAPI backend and WebSockets.
- **High-Fidelity 3D Rendering:** GLTF model integration with dynamic lighting.
- **V12 Telemetry:** Live speed tracking and engine status HUD.
- **Interactive Controls:** Full keyboard (keypad) support for steering and acceleration.

##  Technical Stack
- **Frontend:** Three.js, GSAP, WebGL
- **Backend:** Python, FastAPI, Uvicorn
- **Communication:** Bi-directional WebSockets

##  Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/marymicy/Aston-Martin-Valkyrie.git](https://github.com/marymicy/Aston-Martin-Valkyrie.git)
cd Aston-Martin-Valkyrie

2. Install Dependencies
Bash
pip install "fastapi[standard]" uvicorn
3. Run the Physics Engine
Bash
python main.py
4. Launch the Game
Open a second terminal and run:

Bash
python -m http.server 8080
Then navigate to http://localhost:8080 in your browser.

🎮 Controls
Up Arrow: V12 Boost / Accelerate

Left/Right Arrows: Precision Steering

Mouse Scroll: Zoom in/out (Main Menu)

Mouse Drag: Rotate car (Main Menu)


---
