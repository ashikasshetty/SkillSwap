# SkillSwap - Peer-to-Peer Collaborative Skill Exchange Platform

**MCA Mini Project Synopsis – 24MCAS356**  
**Institution:** St Agnes College (Autonomous), PG Department of Computer Applications (MCA)  
**Developers:** Ashika Shetty &amp; Ganavi K.H  
**Register Numbers:** 2584106 &amp; 2584125  
**Class:** II MCA "A"  

---

## 1. Project Overview & Problem Statement
In today's digital world, traditional learning platforms rely almost exclusively on paid courses or one-way instructor teaching. Many students possess valuable skills they want to share, but cannot afford expensive courses to learn what they need.

**SkillSwap** is a reciprocal peer-to-peer web application where knowledge itself is the currency. Users can teach skills they know (e.g. Python, Flask, UI/UX, Spanish) in exchange for skills they want to acquire (e.g. Photography, Video Editing, Machine Learning).

---

## 2. Key Modules Implemented

1. **User Registration and Authentication**:
   - Secure account registration with hashed passwords (Werkzeug).
   - Role-based authorization (`user` and `admin`).
   - Profile management with college affiliation, bio, and statistics.

2. **Skill Management**:
   - Add skills you can teach with proficiency levels (*Beginner*, *Intermediate*, *Advanced*, *Expert*).
   - Add skills you want to learn with target levels.
   - Categorized by domains (Computer Programming, Web Dev, UI/UX, Photography, etc.).

3. **Skill Search and Discovery**:
   - Keyword search across skill names, descriptions, and user names.
   - Filter by categories and proficiency levels.
   - Explore both "Skills Offered" and "Skills Wanted".

4. **Smart Skill Matching Engine**:
   - **100% Perfect Mutual Matches**: Identifies reciprocal pairs where User A teaches what User B wants *AND* User B teaches what User A wants (e.g., Ashika teaches Python &amp; wants Photography; Ganavi teaches Photography &amp; wants Python).
   - Compatibility scoring and match breakdown.
   - One-way teaching and learning discovery tabs.

5. **Swap Request Workflow**:
   - Propose a swap specifying which skill you teach and which skill you want to learn.
   - Track status: `Pending`, `Accepted`, `In Progress`, `Completed`, `Rejected`, `Cancelled`.

6. **In-App Direct Messaging**:
   - Dedicated communication room between accepted swap partners.
   - Live AJAX chat polling and auto-scrolling to coordinate study times and links.

7. **Ratings and Testimonials**:
   - 5-star rating system with written feedback after swap completion.
   - Aggregated trust scores displayed on public student profiles.

8. **Admin Dashboard with Chart.js Analytics**:
   - Visual charts: Category popularity (Bar Chart) and Swap status distribution (Doughnut Chart).
   - User moderation (activate/deactivate user accounts).
   - Category management (create, update, or remove categories).

---

## 3. Technology Stack

- **Backend**: Python 3.14 + Flask 3.1 + SQLAlchemy ORM
- **Database**: Dual Support:
  - **SQLite** (Default, zero-config plug-and-play at `instance/skillswap.db`)
  - **MySQL / XAMPP** (Fully compatible via PyMySQL and `DATABASE_URL` environment variable)
- **Frontend**: HTML5, Vanilla CSS3 (Custom Glassmorphism Design System), JavaScript ES6+
- **Visualizations**: Chart.js
- **Icons & Typography**: FontAwesome 6, Google Fonts (Outfit &amp; Inter)

---

## 4. Quick Start & Execution

### Option A: One-Click Run (Windows)
Double-click `run.bat` in the project root folder.

### Option B: Terminal Command
1. Open PowerShell or Terminal in this folder.
2. Install requirements (already installed):
   ```powershell
   py -m pip install -r requirements.txt
   ```
3. Initialize / Seed the database with demo users:
   ```powershell
   py seed_data.py
   ```
4. Start the server:
   ```powershell
   py app.py
   ```
5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 5. Demo Accounts

| User | Email | Password | Role & Key Highlights |
|---|---|---|---|
| **Ashika Shetty** | `ashika@skillswap.com` | `password123` | Teaches Python &amp; Flask. Wants Photography. |
| **Ganavi K.H** | `ganavi@skillswap.com` | `password123` | Teaches Photography &amp; Video. Wants Python. |
| **Rahul Sharma** | `rahul@skillswap.com` | `password123` | Teaches UI/UX (Figma). Completed swap with Ashika. |
| **Ananya Rao** | `ananya@skillswap.com` | `password123` | Teaches Spanish. Pending proposal to Ganavi. |
| **Administrator** | `admin@skillswap.com` | `admin123` | Full admin privileges &amp; Chart.js analytics. |

*(Quick-login buttons are also available on the Login screen for instant one-click login during viva demonstrations!)*

---

## 6. Switching to XAMPP MySQL (Optional)

If you wish to run the app directly against your XAMPP MySQL database:
1. Start MySQL in the XAMPP Control Panel.
2. Create an empty database in phpMyAdmin:
   ```sql
   CREATE DATABASE skillswap_db;
   ```
3. Set the environment variable in your terminal before launching:
   ```powershell
   $env:DATABASE_URL="mysql+pymysql://root:@localhost/skillswap_db"
   py seed_data.py
   py app.py
   ```
