# 📚 AI Study Assistant – Learn Smarter with AI

An AI-powered study assistant that helps you **understand, summarize, and revise study material** from PDFs, images, or raw text.  
Built to bridge the gap between *dumping notes into an LLM* and actually getting **clear, structured explanations** you can study from.

This project focuses on **learning quality**, not just flashy output.

---

## 🎥 Demo (Screen Recording)

📽️ Watch the assistant in action:  
📎 **[Click here to view screen recording](#)**  
*(Add Drive / YouTube link)*

---

## 🚀 Features

- 📄 **PDF Upload** – Extracts and explains study content from PDFs  
- 🖼️ **Image Upload** – OCR + explanation for handwritten or printed notes  
- ✍️ **Text Input Mode** – Paste raw notes and get structured explanations  
- 🧠 **Smart Chunking** – Large content is broken into meaningful chunks  
- 🎯 **Keyword-Focused Selection** – Most relevant chunks are prioritized  
- 📘 **Clean Study Output** – Explanations optimized for learning, not verbosity  
- 🔒 **Input Locking UI** – Only one input mode active at a time (PDF / Image / Text)

---

## 🛠️ Tech Stack

### Frontend
- **React**
- **Vite**
- **Tailwind CSS**
- **React Router**

### Backend
- **FastAPI**
- **Python**
- **LLM APIs** – HuggingFace Encoder & Decoder
- **OCR** (for images)
- **Custom chunking & scoring logic**

### Dev & Deployment *(Discarded)*
- **Docker**
- **Vercel** (Frontend)

📦 Project Root
├── 📄 readme.md                  # Project overview and setup guide
├── 📄 what-i-learned.md          # Development notes and lessons learned
├── 📄 front---back.txt           # Project planning notes
├── 📁 models/                    # Local model artifacts
├── 📁 samples/                   # Example input files
│
├── 📁 backend/
│   ├── 📄 app.py                 # Backend application entry point
│   ├── 📄 controller.py          # Request routing and orchestration
│   ├── 📄 requirements.txt       # Python dependencies
│   ├── 📄 Dockerfile             # Docker configuration
│   ├── 📄 docker-compose.yml     # Container orchestration setup
│   │
│   ├── 📁 api/
│   │   └── 📄 main.py            # API route definitions
│   │
│   ├── 📁 embeddings/
│   │   └── 📄 bert_embedder.py   # Embedding generation logic
│   │
│   ├── 📁 ingestion/             # Input loaders
│   │   ├── 📄 text_loader.py
│   │   ├── 📄 pdf_loader.py
│   │   └── 📄 image_loader.py
│   │
│   ├── 📁 preprocessing/         # Cleaning and chunking logic
│   │
│   ├── 📁 understanding/         # Content understanding modules
│   │   ├── 📄 topic_classifier.py
│   │   ├── 📄 keyword_extractor.py
│   │   └── 📄 difficulty_estimator.py
│   │
│   ├── 📁 generation/
│   │   └── 📄 explainer.py       # Explanation generation logic
│   │
│   └── 📁 evaluation/            # Metrics and logging utilities
│
└── 📁 frontend/
    ├── 📄 index.html             # Application shell
    ├── 📄 package.json           # Frontend dependencies and scripts
    ├── 📄 vite.config.ts         # Vite configuration
    ├── 📄 tsconfig.json
    ├── 📄 tsconfig.app.json
    ├── 📄 tsconfig.node.json
    ├── 📄 eslint.config.js       # Linting rules
    ├── 📄 components.json        # Component metadata
    │
    └── 📁 src/
        ├── 📄 main.tsx           # React app bootstrap
        ├── 📄 App.tsx            # Root React component
        │
        ├── 📁 api/
        │   └── 📄 analyze.ts     # API client for analysis requests
        │
        ├── 📁 hooks/
        │   └── 📄 useAnalyze.ts  # Custom analysis hook
        │
        ├── 📁 components/        # UI components and layouts
        │
        ├── 📁 styles/
        │   └── 📄 global.css     # Global styles
        │
        └── 📁 types/
            └── 📄 study.ts       # Shared TypeScript definitions

## ☁️ Cloudflare AI Setup

This project uses **Cloudflare Workers AI** for LLM inference.

### 1️⃣ Get Cloudflare Credentials

From your Cloudflare dashboard:

- **Account ID**
- **API Token** (with Workers AI permissions)

Generate the token from:  
`Cloudflare Dashboard → My Profile → API Tokens`

---

### 2️⃣ Environment Variables (`.env`)

Create a `.env` file inside your **backend** directory:

```env
# Cloudflare AI
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here

# Model Configuration
CLOUDFLARE_MODEL=@cf/meta/llama-3-8b-instruct

# App Settings
ENV=development

⚠️ **Important**

- Never commit `.env` files to GitHub  
- Add `.env` to your `.gitignore`

---

### 3️⃣ Backend Usage Example

The backend loads environment variables using **`python-dotenv`**:

```python
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
MODEL = os.getenv("CLOUDFLARE_MODEL")

## 🧠 How It Works (High Level)

1. User uploads a **PDF / Image** or enters **Text**
2. Content is:
   - Extracted (PDF parsing / OCR if needed)
   - Split into semantic chunks
3. Chunks are **scored based on keyword density**
4. Top-scoring chunks are selected
5. The LLM generates **clear, study-friendly explanations**
6. Output is formatted for **easy reading and revision**

---

## 🎯 Why This Project Exists

Please refer to the **`what-i-learned.md`** file for detailed reflections and lessons learned while building this project.

---

## 📦 How to Run Locally

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/ai-study-assistant.git
cd ai-study-assistant


2️⃣ Backend Setup
cd backend
python -m venv venv
Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

3️⃣ Frontend Setup
cd frontend
npm install
npm run dev


Then open http://localhost:5173
 in your browser 🚀

🧩 Project Status

✅ Core pipeline working

✅ Frontend upload flow implemented

⚠️ UI/UX polishing in progress

🚧 Advanced study modes (Q&A, flashcards) planned

🧑‍💻 Author

Rudra Mondal
AI / ML • Full-Stack • Learning-Driven Projects

GitHub: https://github.com/Rudra-1509

LinkedIn: (add if you want)

⭐ A Note

This isn’t a “perfect AI product”.
It’s a learning-first project, built by struggling with real problems — and that’s exactly why it exists.