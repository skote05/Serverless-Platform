# Serverless Function Execution Platform

A full-stack, containerized, extensible platform for creating, managing, and executing user-defined serverless functions (Python/JavaScript) with isolation, real-time performance metrics, and interactive dashboard visualization.

## 🚀 Overview
This platform allows you to:
- Create, edit, delete, and execute custom functions (Python/JavaScript)
- Run code in isolated environments (Docker containers & simulated gVisor)
- Monitor performance: execution time, memory, and CPU usage
- Visualize and compare metrics for each function and environment
- Manage everything from an interactive, user-friendly dashboard

Great for learning about containers, serverless architecture, security sandboxes, and resource management!

## 🖼️ Architecture
```
┌────────────┐     HTTP/API      ┌───────────────┐
│            │◄─────────────────▶│               │
│ Frontend   │                   │   Backend     │
│ (Streamlit)│                   │  (Express.js) │
└─────▲──────┘                   └──────▲────────┘
      │                                 │
      │ REST                            │ REST
      │                                 │
      ▼                                 ▼
┌────────────┐                  ┌─────────────┐
│            │    HTTP/API      │             │
│ Execution  │◄───────────────▶ │   MySQL     │
│ Engine     │                  │  Database   │
│ (FastAPI)  │                  │             │
└────────────┘                  └─────────────┘
      ▲
      │ Docker/gVisor
 ┌────┴────────┐
 │ Containers  │
 └─────────────┘
```
- **Frontend**: Dashboard for users (Python Streamlit)
- **Backend API**: Function and metrics management (Node.js/Express)
- **Execution Engine**: Runs user code in Docker/gVisor (Python/FastAPI)
- **Database**: Stores function definitions and metrics (MySQL)

All components run in Docker containers, orchestrated by Docker Compose.

## 🛠️ Tech Stack
|-------------------|-----------------------|------------------------------------------------------------|
| Component         | Technology            | Purpose                                                    |
|-------------------|-----------------------|------------------------------------------------------------|
| Frontend          | Streamlit (Python)    | UI: Functions CRUD, execution, metrics visualization       |
| Backend           | Express.js (Node)     | API: CRUD, execution orchestration, metrics logging        |
| Execution Engine  | FastAPI (Python)      | Runs code in containers, collects performance stats        |
| Database          | MySQL                 | Stores all functions, execution results, and stats         |
| Virtualization    | Docker containers     | Isolated, reproducible code execution; gVisor is simulated |
| Orchestration     | Docker Compose        | One-command full stack build/run                           |
|-------------------|-----------------------|------------------------------------------------------------|

## ✨ Key Features
- **CRUD Operations**: Add, View, Edit, Delete Python/JS functions.
- **Containerized Execution**: All code runs inside real Docker containers (secure, reproducible).
- **Simulated gVisor Mode**: Shows overhead/tradeoffs of extra-isolated execution.
- **Resource Metering**: Tracks and displays per-run execution time, memory, CPU use.
- **Historical Stats & Charts**: Compare Docker vs. gVisor performance interactively.
- **No Host Mess**: Runs entirely in containers—nothing “touches” your laptop beyond Docker.
- **Robust Error Handling**: Duplicate name checks, runtime/code error surfacing.
- **Extensible Architecture**: Easily add more languages, runtimes, or UI enhancements.

## 🌍 Why This Project?
- Learn how real serverless/FaaS platforms work—from code upload to isolated runtime.
- Understand container security and resource throttling (why time/CPU vary).
- Experiment with tradeoffs between speed and isolation (Docker vs. gVisor).
- Build production-grade skills in Docker, full-stack microservices, and API design.

## 🏗️ Quickstart: How to Build and Run
1. **Clone the Repo**
   ```bash
   git clone https://github.com/skote05/Serverless-Platform.git
   cd Serverless-Platform
   ```

2. **Build and Start All Services**
   ```bash
   # Build everything (first time may take a few minutes)
   docker-compose up --build -d
   ```

3. **Check All Containers Are Running**
   ```bash
   docker-compose ps
   ```
   Expected output includes:
   - serverless_mysql
   - serverless_backend
   - serverless_execution_engine
   - serverless_frontend

4. **Access the Web Dashboard**
   Open your browser to:  
   [http://localhost:8502](http://localhost:8502)  
   - Use the **Function Management** tab to create/edit functions.
   - Use the **Function Execution** tab to run and monitor them.

5. **Stopping and Cleaning Up**
   ```bash
   # Stop all containers
   docker-compose down
   ```

## 📚 Detailed Usage
### Creating and Managing Functions
- Choose language (Python or JavaScript)
- Enter a unique name, route, timeout (in ms), and your code
- Click **Create** to save (name must be unique; duplicate routes/names rejected)

### Running Functions
- Select any function in the **Execution** tab
- Choose execution environment: Docker and/or gVisor
- Click **Execute Function**
- Results table and comparison charts show for both Docker and gVisor runs:
  - Output
  - Execution time (ms)
  - Memory used (MB)
  - CPU used (%)

### Interpreting Results
- Execution time, memory, and CPU vary across runs, depending on code, environment, and system activity—typical of containerized, serverless infrastructure.
- gVisor runs simulate stronger isolation but with more overhead (simulated for cross-platform compatibility).

## 🧑💻 Example: How Your Code Flows
1. **Frontend form → backend API**:
   ```python
   # Streamlit: On Create
   requests.post(f"{BACKEND_URL}/api/functions", json={
       "name": name,
       "route": route,
       "language": language,
       "timeout_ms": timeout_ms,
       "code": code
   })
   ```

2. **Backend API endpoint**:
   ```javascript
   // Express.js route
   app.post('/api/functions', async (req, res) => {
       // Save function and code in MySQL
   });
   ```

3. **On execution**:
   - Backend fetches code, sends to Execution Engine:
   ```javascript
   // Express
   const response = await axios.post(`${EXECUTION_ENGINE_URL}/execute`, {function_id, code, language, timeout_ms, executor});
   ```
   - Execution Engine runs code in Docker/“gVisor” container, reporting resource use and result.

## 🔒 Why Containers and Resource Limits?
- Containers ensure each code run is isolated and can’t harm your infrastructure.
- Limits (memory, CPU) prevent buggy or malicious functions from consuming all system resources.
- Simulated gVisor mode demonstrates security best practices (stronger sandbox, more isolation).

## 📝 Common Issues & FAQ
- **Duplicate function name error?**  
  → Names must be unique. Delete old or use a new name.
- **“Hello, World!” still runs on create?**  
  → Fully replace the code in the code editor before creating; update works as expected.
- **Metrics change each run?**  
  → Natural container scheduling/CPU use variability—see the docs section “Why do execution time/memory/CPU change?”
- **Volume mount/file errors?**  
  → The project uses inline code execution (`python -c`/`node -e`) to avoid Docker Desktop volume sharing issues on Mac/Windows.

## 🔌 All Useful Run Commands
```bash
# Build and run everything
docker-compose up --build -d

# Show running services and their ports
docker-compose ps

# View logs for a specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f execution-engine

# Access MySQL CLI
docker exec -it serverless_mysql mysql -u serverless_user -pserverless_pass serverless_db

# Stop all services
docker-compose down
```

## 🗂️ Project Directory Structure
```
serverless-platform/
├── backend/                # Node.js/Express backend API
│   ├── server.js
│   └── Dockerfile
├── frontend/               # Streamlit dashboard
│   ├── app.py
│   └── pages/
│       ├── 1_Function_Management.py
│       └── 2_Function_Execution.py
│   └── Dockerfile
├── execution-engine/       # FastAPI execution microservice
│   ├── server.py
│   └── Dockerfile
├── database/
│   └── init.sql           # MySQL schema and setup
└── docker-compose.yml      # Service orchestration
```

## 🐋 Requirements
- Docker (Desktop for Mac/Windows or Docker Engine for Linux)
- Docker Compose
- No Node.js/Python installs needed on host—everything runs in Docker containers.

## 📚 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Credits
Built by **Shashank Kote**.