# 🍽️ SMART CANTEEN – AI-Powered College Canteen Management System

An enterprise-grade, modern, AI-powered Smart Canteen Management Platform designed for college campuses. Engineered with a **Zomato-inspired responsive UI/UX**, robust Python **Flask backend**, **MySQL/SQLite database layer**, and **explainable Machine Learning models** for demand forecasting, crowd prediction, food waste minimization, personalized recommendations, feedback sentiment NLP, and an interactive conversational assistant.

---

## 🌟 Key Features

### 1. 🎓 Student Experience (Zomato-Style UI)
- **Visual Food Discovery:** High-res food cards with Veg/Non-Veg indicators, spice level badges, calories, preparation time, and dynamic quantity controls (`[-] 1 [+]`).
- **Contextual AI Recommendations:** Curated daily picks based on student past orders, time of day (Breakfast, Lunch, Evening snacks), and student budget.
- **Smart Queue & Prep Time Estimator:** Real-time formula estimating waiting time and recommending pickup times (e.g. *"Pickup at 12:55 PM"*).
- **Cart & Dynamic Discount Coupons:** Instant discount computation for coupon codes (e.g., `WELCOME50`, `STUDENT10`, `HUNGRY20`).
- **Simulated Payment System:** Instant UPI QR scanner, student dining wallet balance, debit/credit cards, and Cash on Pickup.
- **Live Visual Order Tracking:** Real-time step progress bar (`Placed` ➔ `Accepted` ➔ `Preparing` ➔ `Ready` ➔ `Completed`) with auto-refresh and **downloadable PDF digital invoices**.
- **Interactive 2D Seat Booking:** Real-time table floor map with occupancy color codes (`Available`, `Booked`, `Selected`, `Your Reservation`) across 4 sections (Window Bay, Main Hall, AC Corner, Outdoor Patio).
- **Personalized Insights ("My Insights"):** Monthly spending charts, favorite dish metrics, and category breakdown.
- **Floating AI Assistant:** Chatbot supporting natural queries (*"Under ₹80"*, *"Where is my order?"*, *"What should I eat today?"*, *"Current crowd"*).

### 2. 👑 Executive Admin Portal
- **Executive Analytics Dashboard:** Daily/weekly revenue charts, order counts, peak hours distribution, and campus favorite dishes.
- **AI Control Center:** Tomorrow's machine learning demand predictions with plain-English explainability, hourly crowd heatmaps, and food waste reduction advice.
- **Food Catalog & Menu CRUD:** Add/edit dishes, update ingredients/calories/images, toggle item availability.
- **Smart Inventory & Stock Replenishment:** Material valuation, low-stock threshold triggers, restock logging, and wastage deductions.
- **Feedback Sentiment & Aspect NLP:** Aspect breakdown (Taste, Price, Waiting Time, Quality, Cleanliness, Service, Quantity) and sentiment distribution (% positive, % neutral, % negative).
- **Official PDF & CSV Report Generator:** One-click downloads for Sales, Inventory, and Wastage audit reports.

### 3. 👨‍🍳 Kitchen Display System (KDS - Canteen Staff)
- **Live Kanban Kitchen Queue:** Auto-polling order cards with instant action buttons (`Accept Order`, `Start Cooking`, `Mark Ready`, `Handover & Complete`).
- **AI Daily Prep Guide:** Pre-preparation plan for each dish to minimize student waiting queues.
- **Quick Stock Toggle:** Fast counter toggle to adjust item stock and prevent over-ordering.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.9+, Flask 3.0+
- **Database:** MySQL (Database: `smart_canteen`) with automatic SQLite fallback for zero-friction local execution
- **Security:** `bcrypt` password hashing, parameterized queries (SQL injection prevention), Flask session security
- **Machine Learning & Data Science:** `scikit-learn`, `pandas`, `numpy`, `scipy`
- **PDF Generation:** `reportlab`
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, FontAwesome 6, Chart.js, Animate.css

---

## 🤖 AI & Machine Learning Architecture

| AI Component | Algorithm / Technique | Key Input Features | Output & Benefit |
| :--- | :--- | :--- | :--- |
| **Demand Forecasting** | `RandomForestRegressor` | Day of week, is_weekend, is_exam_period, category_id, food_id, active seat reservations | Predicts quantity needed for every dish tomorrow + Explainability reasoning |
| **Crowd Prediction** | `RandomForestClassifier` | 30-min time slot float, day of week, lunch/tea break flag, active reservations | Classifies crowd as `LOW`, `MEDIUM`, `HIGH`, `VERY HIGH` with % occupancy |
| **Personalized Recommendations** | Hybrid Content + Collaborative + Time-of-Day Context | User order frequency, category preference, dietary preference, time bucket | Curates top dishes with reasons (e.g. *"Popular lunchtime meal"*) |
| **Feedback NLP** | Multi-Aspect Keyword Matching + Sentiment Classifier | Student review text and star rating | Categorizes into 7 aspects (Taste, Price, Waiting Time, etc.) and Sentiment |
| **Food Waste Minimizer** | Shelf-life & Surplus Analyzer | Predicted demand vs current perishable inventory | Computes risk level and provides concrete downsizing recommendations |
| **Smart Chatbot** | Pattern Matching & DB Context Resolver | Natural language user query + active user session | Resolves budget, order status, bestseller, and table queries |

---

## 📂 Project Directory Structure

```
smart_canteen/
├── app.py                      # Application factory and main entry point
├── config.py                   # Configuration (MySQL DB settings, secret keys, fallback mode)
├── requirements.txt            # Python dependencies
├── init_db.py                  # Database initializer and ML model training script
├── README.md                   # System documentation
│
├── database/
│   ├── db.py                   # Unified DB connection & query layer (MySQL + SQLite)
│   ├── schema.sql              # Clean MySQL schema with tables, FKs, indexes
│   └── seed.sql                # Seed data with 25 dishes, demo users, inventory, tables
│
├── ai/
│   ├── recommendation.py       # Personalized hybrid food recommendation engine
│   ├── demand_prediction.py    # RandomForest daily demand forecaster + explainability
│   ├── crowd_prediction.py     # 30-min interval crowd density classifier
│   ├── waste_prediction.py     # Food waste risk estimator and mitigation recommendations
│   ├── feedback_analysis.py    # NLP sentiment & multi-aspect topic classifier
│   ├── chatbot.py              # Context-aware conversational AI assistant
│   └── synthetic_data.py       # Realistic 45-day order history generator
│
├── services/
│   ├── order_service.py        # Order lifecycle, queue management, smart prep-time estimation
│   ├── seat_service.py         # Table allocation, 2D floor plan map, conflict prevention
│   ├── inventory_service.py    # Stock tracking, low-stock threshold alerts, replenishment
│   ├── pdf_service.py          # ReportLab PDF invoice and admin report builder
│   └── notification_service.py # User notifications and live alert manager
│
├── routes/
│   ├── auth_routes.py          # Registration, multi-role login, logout, profile
│   ├── student_routes.py       # Dashboard, Menu, Cart, Checkout, Order Tracking, Seat Booking
│   ├── admin_routes.py         # Dashboard, AI Control Center, Inventory, Menu CRUD, Reports
│   ├── staff_routes.py         # Kitchen Display System (KDS), Daily Demand, Stock toggle
│   └── api_routes.py           # REST endpoints for Chatbot, Cart, Live polling
│
├── static/
│   ├── css/
│   │   └── style.css           # Zomato-inspired CSS design system, cards, badges, 2D map
│   └── js/
│       ├── main.js             # Cart management, real-time toasts, dynamic prep-time
│       ├── chatbot.js          # Floating AI assistant widget
│       ├── seat_booking.js     # 2D table selection interactive handler
│       ├── kitchen_board.js    # Live Kitchen Display auto-poller
│       └── charts.js           # Chart.js analytics renderers
│
└── templates/
    ├── base.html               # Master layout with topbar, cart badge, chatbot widget
    ├── index.html              # Hero landing page
    ├── 404.html & 500.html     # Custom error pages
    ├── auth/                   # Login & Registration templates
    ├── student/                # Student Dashboard, Menu, Cart, Checkout, Tracking, Seats, Insights
    ├── admin/                  # Admin Dashboard, AI Control Center, Menu CRUD, Inventory, Reports
    └── staff/                  # Kitchen Display Board (KDS), Daily Demand, Stock toggle
```

---

## ⚡ Quick Start & Installation Guide

### Step 1: Clone or Navigate to Project Directory
```bash
cd smart_canteen
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup (MySQL or SQLite)
The system supports **MySQL** by default and also includes **seamless auto-fallback to SQLite** with zero configuration.

#### Option A: Using MySQL (Recommended for Production)
1. Open MySQL CLI / phpMyAdmin and create database:
   ```sql
   CREATE DATABASE smart_canteen;
   ```
2. Create a `.env` file in the root directory (optional, or configure `config.py`):
   ```env
   DB_TYPE=mysql
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=smart_canteen
   ```

#### Option B: Zero-Config Local Execution (SQLite)
Simply proceed to Step 5! The initializer automatically detects environment and sets up SQLite with full seed data.

### Step 5: Initialize Database & Train AI Models
Run the initialization script to create tables, seed 25 dishes, 20+ demo users, 15 tables, 12 inventory SKUs, 500+ historical orders, and train the Machine Learning models:
```bash
python init_db.py
```

### Step 6: Start the Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Credentials

You can use the 1-Click Quick Demo Login switcher on the login page or manually enter:

| Role | Email / ID | Password | Access Highlights |
| :--- | :--- | :--- | :--- |
| **🎓 Student** | `student@smartcanteen.com` | `Student@123` | Menu, AI picks, Cart, Orders, 2D Seats, Wallet, Insights |
| **👑 Admin** | `admin@smartcanteen.com` | `Admin@123` | AI Control Center, Sales Analytics, Menu CRUD, Inventory, Reports |
| **👨‍🍳 Staff** | `staff@smartcanteen.com` | `Staff@123` | Live Kitchen Display System (KDS), AI Prep Guide, Stock Toggle |

---

## 🧪 Verification & Testing Completed

- [x] **Flask Server:** Runs smoothly on port 5000 with clean Blueprint routing.
- [x] **Authentication & RBAC:** Bcrypt password hashing, session guards, and role protection.
- [x] **Zomato Design System:** Veg/Non-Veg indicators, dynamic badges, slide-in cart math, and responsive breakpoints.
- [x] **AI Demand Prediction:** RandomForest model forecasting tomorrow's item consumption with plain-English explainability.
- [x] **AI Crowd Prediction:** 30-minute interval classification into LOW/MEDIUM/HIGH/VERY HIGH.
- [x] **AI Recommendations:** Time-of-day contextual suggestions with reason tags.
- [x] **Smart Prep-Time Engine:** Concurrency-aware dynamic kitchen wait-time calculation.
- [x] **2D Seat Map:** Interactive table selector with conflict-free locking.
- [x] **AI Chatbot:** Natural language assistant for budget suggestions and order queries.
- [x] **PDF Generation:** Official digital tax invoices and admin sales reports.
