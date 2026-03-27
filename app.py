from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_PATH = os.path.join(os.path.dirname(__file__), "phantom.db")

# ──────────────────────────────────────────────
#  DB helper
# ──────────────────────────────────────────────
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def secure_login(username, password):
    """
    Secure login with parameterized queries.
    Works with: EMP_756208 / CODE_RED
    """
    con = get_db()
    try:
        cur = con.execute(
            "SELECT * FROM operators WHERE emp_id = ? AND password = ?",
            (username, password)
        )
        row = cur.fetchone()
        con.close()
        return row
    except Exception as e:
        con.close()
        print(f"[Error] Login failed: {e}")
        return None


# ──────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    """Main page - serves the HTML interface"""
    return render_template("round2_challenge.html")


@app.route("/api/login", methods=["POST"])
def api_login():
    """API endpoint for login via JavaScript"""
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Fields cannot be empty"}), 400

    user_row = secure_login(username, password)

    if user_row:
        session["operator"] = user_row["username"]
        session["emp_id"] = user_row["emp_id"]
        session["level"] = user_row["clearance"]
        return jsonify({"success": True, "user": user_row["username"]}), 200
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route("/api/records")
def api_records():
    """API endpoint to fetch records"""
    if "operator" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    con = get_db()
    contracts = con.execute("SELECT * FROM contracts ORDER BY id").fetchall()
    flag_row = con.execute("SELECT flag FROM secrets WHERE id=1").fetchone()
    con.close()

    flag = flag_row["flag"] if flag_row else "FLAG_MISSING"

    contracts_list = [
        {
            "id": c["id"],
            "ref": c["ref"],
            "target": c["target"],
            "date": c["date"],
            "location": c["location"],
            "method": c["method"],
            "status": c["status"],
            "notes": c["notes"],
        }
        for c in contracts
    ]

    return jsonify({
        "success": True,
        "operator": session.get("operator"),
        "level": session.get("level"),
        "flag": flag,
        "contracts": contracts_list
    }), 200


@app.route("/api/unlock-flag", methods=["POST"])
def api_unlock_flag():
    """API endpoint to unlock flag with correct time"""
    if "operator" not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401

    data = request.get_json()
    entered_time = data.get("time", "").strip()

    # Correct time: 23:39 (Victim death time for C-009)
    CORRECT_TIME = "23:39"

    if entered_time == CORRECT_TIME:
        # Get the flag from database
        con = get_db()
        flag_row = con.execute("SELECT flag FROM secrets WHERE id=1").fetchone()
        con.close()
        
        flag = flag_row["flag"] if flag_row else "FLAG_MISSING"
        
        print(f"[FLAG UNLOCKED] Operator: {session.get('operator')}, Time: {entered_time}")
        
        return jsonify({
            "success": True,
            "message": "FLAG UNLOCKED! Victim death time verified.",
            "flag": flag
        }), 200
    else:
        print(f"[WRONG TIME] Operator: {session.get('operator')}, Attempted: {entered_time}")
        
        return jsonify({
            "success": False,
            "message": "⚠ INCORRECT TIME — VICTIM DETAIL VERIFICATION FAILED"
        }), 401


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """API endpoint for logout"""
    session.clear()
    return jsonify({"success": True}), 200


@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\n"
        "Disallow: /records\n"
        "Disallow: /admin_panel\n",
        200,
        {"Content-Type": "text/plain"},
    )


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("[!] Database not found. Run: python init_db.py")
    else:
        print("[+] Database found. Starting Flask app...")
    
    app.run(debug=False, host="0.0.0.0", port=5000)