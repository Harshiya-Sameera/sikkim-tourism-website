🌄 AI-Powered Sikkim Tourism & Monastery Discovery Platform

The AI-Powered Sikkim Tourism and Monastery Discovery Platform is a full-stack intelligent web application designed to enhance tourism in Sikkim through AI-driven features and centralized data access.

This platform helps tourists:

. Discover monasteries and tourist places
. Plan personalized itineraries
. Interact with an AI chatbot (Virtual Monk)
. Identify landmarks using image recognition
. Explore locations on an interactive map

🚀 Live Demo

🔗 Deployment Link:
👉 https://degrees-scores-cake-turtle.trycloudflare.com/

🎯 Problem Statement

Tourists visiting Sikkim face:

. Fragmented information across multiple sources
. No centralized platform for monasteries
. Lack of AI-based guidance and itinerary planning

This project solves these issues by providing a single intelligent tourism platform.

✨ Features

🧭 1. Explore Tourist Places
-Browse all Sikkim attractions
-Category-based filtering (Monasteries, Lakes, Viewpoints, etc.)
-Detailed place information (timings, fees, images)

🤖 2. AI Chatbot – Virtual Monk
-AI-powered tourism assistant
-Cultural and contextual responses
-Suggests places dynamically
-Supports image-based queries

🗺️ 3. Interactive Map
-Google Maps integration
-All locations plotted with markers
-Easy navigation

📅 4. AI Itinerary Planner
-Generates day-wise travel plans
-Based on:
-Travel duration
-Interests
-Arrival details

📸 5. AI Lens (Image Recognition)
-Upload image of a place
-AI identifies landmark
-Displays details from database

👤 6. User Dashboard
-Save favorite places
-View generated itineraries
-Personalized experience

🛠️ 7. Admin Panel
-Manage places & categories
-Analytics dashboard
-AI usage tracking
-Bulk JSON data upload

🏗️ Tech Stack

💻 Frontend
HTML5
Tailwind CSS
JavaScript

⚙️ Backend
Python
Django (MVT Architecture)

🧠 AI Integration
Google Gemini API (Multimodal)

🗄️ Database
SQLite

🌍 APIs Used
Google Maps JavaScript API

🧩 System Architecture
The system follows a 4-layer architecture:

. Presentation Layer (UI)
. Application Layer (Django Backend)
. AI Service Layer (Gemini API)
. Data Layer (SQLite Database)

📂 Project Structure
sikkim-tourism/
│── portal/
│── chatbot/
│── tourism/
│── itinerary/
│── users/
│── templates/
│── static/
│── media/
│── manage.py
│── requirements.txt
│── README.md

⚙️ Installation & Setup

1️⃣ Clone Repository
git clone https://github.com/Harshiya-Sameera/sikkim-tourism-website.git
cd sikkim-tourism

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables
Create .env file:
GEMINI_API_KEY=your_api_key

5️⃣ Run Migrations
python manage.py migrate

6️⃣ Start Server
python manage.py runserver

📊 Key Modules
-Authentication System
-Tourism Data Management
-AI Chatbot Module
-Itinerary Generator
-AI Lens Recognition
-Admin Intelligence System

🧪 Testing
Functional Testing ✅
Edge Case Testing ✅
API Testing ✅
Performance Testing ✅

👩‍💻 Team
Shaik Harshiya Sameera
Teeguri Vyshnavi
Tiyyagura Ayyappa Reddy
Tellagorla Yallamanda

📜 License
This project is for academic and educational purposes only.
