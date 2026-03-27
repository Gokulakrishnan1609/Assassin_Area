"""
init_db.py — Run ONCE before starting the Flask app.
Creates phantom.db with all tables and seed data.
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "phantom.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS operators (
    id        INTEGER PRIMARY KEY,
    emp_id    TEXT    NOT NULL UNIQUE,
    username  TEXT    NOT NULL UNIQUE,
    password  TEXT    NOT NULL,
    clearance INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS contracts (
    id       INTEGER PRIMARY KEY,
    ref      TEXT,
    target   TEXT,
    date     TEXT,
    location TEXT,
    method   TEXT,
    status   TEXT,
    notes    TEXT
);

CREATE TABLE IF NOT EXISTS secrets (
    id   INTEGER PRIMARY KEY,
    flag TEXT NOT NULL
);
"""

OPERATORS = [
    ("EMP_756208", "phantom_admin", "CODE_RED", 5),
]

CONTRACTS = [
    ("C-001","A. Mercer",    "2023-03-11","Chennai, TN",    "SILENT", "CLOSED",   "Handled cleanly. No witnesses."),
    ("C-002","R. Krishnan",  "2023-05-22","Bengaluru, KA",  "STAGED", "CLOSED",   "Ruled as accident by local PD."),
    ("C-003","S. Fernandez", "2023-08-07","Mumbai, MH",     "REMOTE", "CLOSED",   "Clean exit. Payment received."),
    ("C-004","D. Varma",     "2023-11-14","Hyderabad, TS",  "SILENT", "CLOSED",   "Target had no protection. Swift."),
    ("C-005","P. Sharma",    "2024-01-30","Delhi, DL",      "STAGED", "CLOSED",   "Vehicle malfunction. Case cold."),
    ("C-006","M. Okonkwo",   "2024-03-05","Pune, MH",       "REMOTE", "PENDING REVIEW",   "Witness reported. Monitoring."),
    ("C-007","T. Naidu",     "2024-05-19","Coimbatore, TN", "SILENT", "CLOSED",   "Untraceable. Funds cleared."),
    ("C-008","J. Rajan",     "2024-07-03","Madurai, TN",    "STAGED", "COMPROMISED","⚠ Police inquiry opened."),
    ("C-009","[ CLASSIFIED ]","2024-██-██","REDACTED",       "PHANTOM","CLOSED",  "⚠ VICTIM DEATH TIME: 23:39 — Locked secure vault. Evidence encrypted."),
    ("C-010","V. Iyer",      "2024-09-27","Chennai, TN",    "REMOTE", "ACTIVE",   "Contract in progress."),
]

FLAG = "CF{You_find_Contract}"

def init():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[*] Removed old phantom.db")

    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)

    con.executemany(
        "INSERT INTO operators (emp_id, username, password, clearance) VALUES (?,?,?,?)",
        OPERATORS,
    )
    con.executemany(
        "INSERT INTO contracts (ref,target,date,location,method,status,notes) VALUES (?,?,?,?,?,?,?)",
        CONTRACTS,
    )
    con.execute("INSERT INTO secrets (id,flag) VALUES (1,?)", (FLAG,))
    con.commit()
    con.close()
    
    print("[+] phantom.db created successfully.")
    print(f"[+] Flag: {FLAG}")
    print(f"[+] Valid credentials: EMP_756208 / CODE_RED")
    print(f"[+] Flag unlock code: 23:39 (Victim death time from C-009)")


if __name__ == "__main__":
    init()