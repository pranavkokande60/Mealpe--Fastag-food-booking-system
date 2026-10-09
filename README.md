# 🍽️ SMART CANTEEN – AI-Powered College Canteen Management System

An enterprise-grade, modern, AI-powered Smart Canteen Management Platform designed for educational and university campuses. Engineered with a **Zomato-inspired responsive UI/UX**, robust Python **Flask backend**, **PostgreSQL (pgAdmin) / MySQL / SQLite database layer**, and **explainable Machine Learning models** for daily demand forecasting, 30-minute crowd density classification, **Smart Food Rescue & Zero-Waste Resale System**, personalized contextual recommendations, feedback sentiment NLP, and an interactive conversational assistant.

---

## 🌟 Key Features

### 1. 🎓 Student Experience (Zomato-Style Responsive UI)
- **Visual Food Discovery:** High-res food cards with Veg/Non-Veg indicators, spice level badges, calories, preparation time, and dynamic quantity controls (`[-] 1 [+]`).
- **Contextual AI Recommendations:** Curated daily picks combining TF-IDF ingredient similarity, past student order history, time-of-day temporal boosting (Breakfast, Lunch, Evening Snacks), and student budget constraints.
- **Smart Queue & Prep Time Estimator:** Concurrency-aware algorithm estimating kitchen backlog based on active chef stations to predict accurate pickup times (e.g. *"Pickup at 12:55 PM"*).
- **Cart & Dynamic Discount Coupons:** Real-time 5% GST calculation and instant discount deductions for coupons (`WELCOME50`, `STUDENT10`, `HUNGRY20`, `CHAI5`).
- **Simulated Multi-Channel Payment System:** Instant UPI QR scanner, student dining wallet balance, debit/credit cards, and Cash on Pickup.
- **Live Visual Order Tracking:** Real-time step progress bar (`Placed` ➔ `Accepted` ➔ `Preparing` ➔ `Ready` ➔ `Completed`) with asynchronous polling and **downloadable PDF tax invoices**.
- **Flexible Order Cancellation Policy (80% Refund / 20% Cancellation Fee):**
  - Students can cancel orders across `PLACED`, `ACCEPTED`, `PREPARING`, and `READY` status (before food is collected from the counter).
  - Instant **80% refund** credited directly to the student's dining wallet balance.
  - A **20% cancellation fee** is retained by the canteen to offset preparation and raw material costs.
- **⚡ Smart Food Rescue Deals (10% Discount for Peer Students):**
  - Cancelled meals in `PREPARING` or `READY` status automatically generate **Food Rescue Offers** available to other students at a **10% discount** ($\text{Rescue Price} = \text{Original Price} \times 0.90$).
  - Real-time notification broadcast with audio chime, live notification badge, 20-minute freshness countdown, and 1-click **"⚡ Claim & Buy Now"** checkout.
  - Unique 4-digit Collection PIN for fast, contactless pickup at the counter.
- **Interactive 2D Seat Booking & Self-Service Cancellation:** Real-time table floor map with conflict-free slot locking (`Available`, `Booked`, `Selected`, `Your Reservation`) across 4 sections (*Window Bay, Main Hall, AC Corner, Outdoor Patio*) with 1-click booking cancellation.
- **Personalized Insights ("My Insights"):** Interactive Chart.js monthly spending trends, favorite dish consumption frequency, and category breakdown.
- **Aspect-Based Review Submission:** Submit ratings and detailed review comments parsed by an in-house NLP engine.
- **Floating AI Assistant:** Chatbot supporting natural queries (*"Under ₹80"*, *"Where is my order?"*, *"What should I eat today?"*, *"Current crowd"*).

---

### 2. 👑 Executive Admin Portal
- **Executive Analytics Dashboard:** Real-time revenue cards, today's order counts, 7-day revenue trend line charts, category sales distributions, and top 5 campus favorites.
- **Food Rescue & Cancellation Audits:** Track total meals saved, 20% cancellation fees collected, 80% refunds issued, and zero-waste impact metrics.
- **AI Control Center:** Tomorrow's machine learning demand predictions with plain-English explainability rationales (e.g., *"High demand expected due to Friday lunch rush and 42 advance seat bookings"*), hourly crowd heatmaps, and food waste reduction advice.
- **Food Catalog & Menu CRUD:** Add, edit, or delete dishes, update ingredients, calories, prep-times, prices, and toggle live availability.
- **Smart Inventory & Stock Replenishment:** Raw material valuation, low-stock threshold triggers, restock logging, unit costs, and spoilage deductions.
- **Feedback Sentiment & Aspect NLP Analytics:** Aspect breakdown (*Taste, Price, Waiting Time, Quality, Cleanliness, Service, Quantity*) and sentiment distribution (% positive, % neutral, % negative).
- **Table Reservation Management:** Comprehensive schedule view of all active and upcoming seat reservations.
- **User & Role Management:** View all registered students, staff, and admins with wallet balance adjustments.
- **Official PDF & CSV Report Generator:** One-click downloads for itemized Sales Reports, Inventory Audits, and Spoilage logs.

---

### 3. 👨‍🍳 Kitchen Display System (KDS - Canteen Staff)
- **Live Kanban Kitchen Queue:** Auto-polling order tickets categorized into active columns with 1-click status transitions (`Accept Order`, `Start Cooking`, `Mark Ready`, `Handover & Complete`).
- **Food Rescue Resale Badges:** Cancelled orders that get claimed by another student dynamically update on the kitchen display with a **RESCUE ORDER** tag and the new buyer's pickup details.
- **AI Daily Prep Guide:** Pre-preparation portion forecasting for each dish to minimize student waiting queues during peak intervals.
- **Quick Stock & Availability Toggle:** 1-click counter toggle to adjust item stock and immediately prevent student over-ordering.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.9+, Flask 3.0.3, Flask-SocketIO (Modular Blueprints: `auth`, `student`, `admin`, `staff`, `api`)
- **Database Layer:** Universal DB abstraction supporting:
  - **PostgreSQL 14–18+** with **pgAdmin 4** (`psycopg2-binary`)
  - **MySQL 8.0+** (`pymysql` / `mysql-connector-python`)
  - **SQLite 3.37+** (Zero-configuration local auto-fallback)
- **Real-Time Communication:** WebSockets / Socket.IO + Polling Fallback for live food rescue popups and kitchen status sync.
- **Security:** `bcrypt` password hashing, parameterized SQL execution, secure HTTP session cookies, RBAC guards.
- **Machine Learning & Data Science:** `scikit-learn` (Random Forest Regressor & Classifier), `pandas`, `numpy`, `scipy`.
- **Natural Language Processing:** Rule-augmented aspect extractor & sentiment polarity analyzer.
- **Document Generation:** `reportlab` algorithmic PDF invoice and report engine.
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, FontAwesome 6, Chart.js 4.4, Animate.css.

---

## 🤖 AI & Machine Learning Architecture

| AI Component | Algorithm / Technique | Key Input Features | Output & Practical Benefit |
| :--- | :--- | :--- | :--- |
| **Demand Forecasting** | `RandomForestRegressor` ($R^2 = 0.912$) | Day of week, weekend flag, exam surge flag, food category, price, advance table reservations, 14-day rolling mean | Predicts exact portion quantities needed tomorrow with explainability reasoning |
| **Crowd Density Classifier** | `RandomForestClassifier` (93.4% Acc) | 30-min operational time bucket (08:00–19:00), day of week, lunch/tea break flags, active table bookings | Classifies footfall into `LOW`, `MEDIUM`, `HIGH`, `VERY HIGH` & estimates counter wait time |
| **Contextual Food Recommender** | Hybrid Content (TF-IDF) + Collaborative Filtering + Temporal Multipliers | Student order frequency, category preference, dietary preference (Veg/Non-Veg), current time of day | Delivers personalized dish recommendations with dynamic badges (*"Perfect morning breakfast pick"*) |
| **Aspect-Based Sentiment NLP** | Rule-Augmented Multi-Aspect Lexicon Parser | Student review comments & star ratings | Isolates feedback across 7 dimensions (*Taste, Price, Waiting Time, Quality, Cleanliness, Service, Quantity*) |
| **Food Waste & Rescue Model** | Predictive Batch Spoilage + Circular Rescue Matcher | Preparation stage, shelf-life expiry, cancel timestamps, discount factor | Auto-creates 10% discounted rescue deals on cancellation and reduces prepared food waste |
| **Smart Conversational Bot** | NLP Pattern Matching & Session DB Context Resolver | Natural language student chat query + active user cart/order session | Answers queries regarding budget dishes (*"Under ₹80"*), live order tracking, bestsellers, and table slots |

---

## 📂 Project Directory Structure

```
smart_canteen/
├── app.py                      # Application factory, SocketIO integration & entry point
├── config.py                   # Central configuration (PostgreSQL, MySQL, SQLite, secret keys)
├── requirements.txt            # Python package dependencies
├── init_db.py                  # Database initializer and ML model training script
├── test_app.py                 # Automated unit & integration testing suite (15 test modules)
├── sql_shell.py                # Interactive terminal SQL console
├── view_db.py                  # CLI database table inspector
├── setup_postgres.py           # Interactive PostgreSQL / pgAdmin connection setup tool
├── create_paper_docx.py        # Standalone IEEE Word document generator script
├── Research_Paper_Smart_Canteen.md   # IEEE format academic research paper
├── Research_Paper_Smart_Canteen.docx # Microsoft Word research paper document
├── README.md                   # Comprehensive system documentation
│
├── database/
│   ├── db.py                   # Unified DB connection & query translation layer (PostgreSQL, MySQL, SQLite)
│   ├── schema.sql              # Clean relational schema with FKs, food_rescue_offers, and notifications
│   ├── seed.sql                # Initial seed data (25 dishes, demo users, inventory, tables)
│   ├── smart_canteen_pgadmin_all_in_one.sql # Single-click PostgreSQL/pgAdmin import script
│   └── smart_canteen.db        # High-performance zero-config local SQLite database
│
├── ai/
│   ├── recommendation.py       # Contextual hybrid food recommender engine
│   ├── demand_prediction.py    # RandomForest daily demand forecaster with explainability
│   ├── crowd_prediction.py     # 30-min interval crowd density classifier
│   ├── waste_prediction.py     # Food waste risk estimator and shelf-life analyzer
│   ├── feedback_analysis.py    # NLP sentiment & multi-aspect topic parser
│   ├── chatbot.py              # Context-aware conversational AI assistant
│   └── synthetic_data.py       # Realistic multi-week order history generator
│
├── services/
│   ├── order_service.py        # Order placement, smart prep-time, 80% refund / 20% cancellation fee
│   ├── rescue_service.py       # Food rescue offers, 10% resale pricing, atomic claim & verification
│   ├── seat_service.py         # 2D table floor plan allocator, conflict prevention & cancellation
│   ├── inventory_service.py    # Stock tracking, reorder threshold alerts, wastage logging
│   ├── pdf_service.py          # ReportLab PDF invoice and audit report builder
│   └── notification_service.py # Real-time Socket.IO and in-app notification dispatcher
│
├── routes/
│   ├── auth_routes.py          # Clean role-tabbed login, registration, logout, profile
│   ├── student_routes.py       # Dashboard, Menu, Cart, Checkout, Order Tracking, Food Rescue, Seats, Insights
│   ├── admin_routes.py         # Dashboard, AI Control Center, Inventory, Menu CRUD, Seats, Reports
│   ├── staff_routes.py         # Kitchen Display System (KDS), Daily Demand Guide, Stock toggle
│   └── api_routes.py           # REST API endpoints for Chatbot, Cart, Notifications & Live polling
│
├── static/
│   ├── css/
│   │   └── style.css           # Zomato Crimson (#E23744) CSS design system, cards, 2D seat map
│   └── js/
│       ├── main.js             # Slide-in cart management, toast alerts, dynamic prep-time calculator
│       ├── chatbot.js          # Floating AI chatbot widget
│       ├── seat_booking.js     # Interactive 2D floor plan table selector
│       └── kitchen_board.js    # Live Kitchen Display auto-poller
│
└── templates/
    ├── base.html               # Master layout with topbar, notification badge, cart badge, chatbot widget
    ├── index.html              # Hero landing showcase
    ├── 404.html & 500.html     # Custom responsive error pages
    ├── auth/                   # Clean role-tabbed login & registration templates
    ├── student/                # Dashboard, Menu, Cart, Checkout, Order Tracker, History, Seats, Insights
    ├── admin/                  # Dashboard, AI Control, Menu CRUD, Inventory, Seats, Users, Reports
    └── staff/                  # Kitchen Display Board (KDS), Daily Demand Guide, Quick Stock
```

---

## ⚡ Quick Start & Installation Guide

### Step 1: Clone or Navigate to Project Directory
```bash
cd smart_canteen
```

### Step 2: Create and Activate Virtual Environment
```bash
# Windows PowerShell
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

---

### Step 4: Database Configuration (Choose Any Option)

#### Option A: PostgreSQL / pgAdmin (Active Mode)
1. Open pgAdmin 4 and ensure PostgreSQL service is running on port 5432.
2. Run the automatic connection setup:
   ```bash
   python setup_postgres.py
   ```
3. Enter your pgAdmin password (e.g. `admin123`) to auto-create and seed the `smart_canteen` database!

#### Option B: Zero-Config Local Execution (SQLite Auto-Fallback)
Simply run `python app.py`! If PostgreSQL/MySQL are not configured, the system automatically initializes local SQLite with full seed data.

#### Option C: Production MySQL
Create database `smart_canteen` in MySQL and configure `.env`:
```env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=smart_canteen
```

---

### Step 5: Start the Application
```bash
python app.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Credentials

| Role | Email / Identifier | Password | Access Highlights |
| :--- | :--- | :--- | :--- |
| **🎓 Student** | `student@smartcanteen.com` *(or `student@canteen.com`)* | `student123` | Menu, AI picks, Cart, Orders, 2D Seats, 80% Wallet Refunds, 10% Rescue Deals |
| **🍳 Kitchen Staff** | `staff@smartcanteen.com` *(or `staff@canteen.com`)* | `staff123` | Live Kitchen Display System (KDS), Rescue Badges, AI Prep Guide, Stock Toggle |
| **👑 Admin** | `admin@smartcanteen.com` *(or `admin@canteen.com`)* | `admin123` | AI Control Center, Food Rescue Analytics, Menu CRUD, Inventory, Reports |

---

## 🧪 Verification & Automated Testing

The complete system includes an end-to-end automated testing suite (`test_app.py`). To execute all tests:
```bash
python test_app.py
```

### Verified Test Modules (15/15 Passing):
- [x] **Flask Server Architecture:** Clean Blueprint routing, session authentication, and error handlers.
- [x] **Authentication & RBAC:** Bcrypt password hashing, session guards, and role protection.
- [x] **Zomato Design System:** Veg/Non-Veg indicators, dynamic badges, slide-in cart math, and responsive breakpoints.
- [x] **AI Demand Prediction:** RandomForest model forecasting daily item demand ($R^2 = 0.912$) with explainability.
- [x] **AI Crowd Prediction:** 30-minute interval classification into LOW/MEDIUM/HIGH/VERY HIGH (93.4% Accuracy).
- [x] **AI Recommendations:** Time-of-day contextual suggestions with reason tags.
- [x] **Smart Prep-Time Engine:** Concurrency-aware dynamic kitchen wait-time calculation.
- [x] **2D Seat Map:** Interactive table selector with conflict-free atomic locking.
- [x] **Order Cancellation & 80% Wallet Refunds:** Atomic dining wallet crediting and 20% cancellation fee retention.
- [x] **Table Cancellation:** Real-time slot release on 2D floor plan map.
- [x] **AI Chatbot:** Natural language assistant for budget suggestions and order queries.
- [x] **PDF Tax Invoices:** Algorithmic ReportLab digital invoice generation.
- [x] **Multi-Database Support:** Seamless execution across PostgreSQL, MySQL, and SQLite.
- [x] **Smart Food Rescue Creation & Purchase:** Automatic deal generation on cancellation and peer claim verification.
- [x] **Real-Time Notification Dispatch:** Live Socket.IO/DB alert delivery to other students.

---

## 📜 Copyright & License

Copyright © 2026 Pranav Kokande. All rights reserved.

This project and its source code are proprietary. No permission is granted to copy, modify, distribute, publish, or use this project or its source code without prior written permission from the author.
