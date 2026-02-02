# 📚 AI Study Assistant – Learn Smarter with AI

## 🚀 Features

- 📄 **PDF Upload** – Extracts and explains study content from PDFs  
- 🖼️ **Image Upload** – OCR + explanation for handwritten or printed notes  
- ✍️ **Text Input Mode** – Paste raw notes and get structured explanations  
- 🧠 **Smart Chunking** – Large content is broken into meaningful chunks  
- 🎯 **Keyword-Focused Selection** – Most relevant chunks are prioritized  
- 📘 **Clean Study Output** – Explanations optimized for learning, not verbosity  
- 🔒 **Input Locking UI** – Only one input mode active at a time (PDF / Image / Text)

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

## 📦 How to Run Locally

### 1️⃣ Clone the Repository
```bash
git clone [https://github.com/your-username/ai-study-assistant.git](https://github.com/your-username/ai-study-assistant.git)
cd ai-study-assistant

### 2️⃣ Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

🔤 Install OCR (Required for Image Upload)

This project uses Tesseract OCR for extracting text from images.

Download and install Tesseract OCR for Windows

Make sure Tesseract is added to your system PATH

After installation, restart your terminal

(Do not worry about the exact version — any recent Tesseract OCR build will work.)

### 3️⃣ Frontend Setup
cd frontend
npm install
npm run dev

Then open http://localhost:5173 in your browser 🚀

## 🎥 Demo (Screen Recording)

📽️ Watch the assistant in action:  
📎 [Click here to view screen recording](#)  
*(Add Drive / YouTube link)*

## 🧩 Project Status

✅ Core pipeline working

✅ Frontend upload flow implemented

⚠️ UI/UX polishing in progress

🚧 Advanced study modes (Q&A, flashcards) planned

🧑‍💻 Author

Rudra Mondal
AI / ML • Full-Stack • Learning-Driven Projects

GitHub: [https://github.com/Rudra-1509](https://github.com/Rudra-1509)

