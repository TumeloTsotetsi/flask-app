"""
CyberDiary — Flask + SQLite
Run locally:  python app.py
VPS deploy:   gunicorn -w 4 -b 0.0.0.0:8000 app:app
"""

import sqlite3
import json
import os
import re
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, abort,
                   redirect, session, g, flash, url_for)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cyberdiary-dev-secret-change-in-prod")

DATABASE = os.path.join(os.path.dirname(__file__), "cyberdiary.db")

# ─────────────────────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db:
        db.close()


def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


# ─────────────────────────────────────────────────────────────
# SCHEMA
# ─────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT    UNIQUE NOT NULL,
    title        TEXT    NOT NULL,
    excerpt      TEXT    NOT NULL,
    category     TEXT    NOT NULL DEFAULT 'Fundamentals',
    tag_color    TEXT    NOT NULL DEFAULT '#e8678a',
    hero_icon    TEXT    NOT NULL DEFAULT 'pencil',
    photo        TEXT    DEFAULT '',
    read_time    TEXT    NOT NULL DEFAULT '5 min read',
    content_json TEXT    NOT NULL DEFAULT '[]',
    published    INTEGER NOT NULL DEFAULT 1,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS diaries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    tagline       TEXT    NOT NULL,
    price         REAL    NOT NULL,
    color_main    TEXT    NOT NULL,
    color_light   TEXT    NOT NULL,
    color_accent  TEXT    NOT NULL,
    color_bg      TEXT    NOT NULL,
    emoji         TEXT    NOT NULL DEFAULT '📓',
    pages         INTEGER NOT NULL DEFAULT 200,
    features_json TEXT    NOT NULL DEFAULT '[]',
    in_stock      INTEGER NOT NULL DEFAULT 1,
    badge         TEXT    DEFAULT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name  TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    address        TEXT NOT NULL,
    city           TEXT NOT NULL,
    postal         TEXT NOT NULL,
    total          REAL NOT NULL,
    shipping       REAL NOT NULL DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'pending',
    created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    diary_id   INTEGER NOT NULL REFERENCES diaries(id),
    diary_name TEXT    NOT NULL,
    price      REAL    NOT NULL,
    qty        INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.commit()

    if db.execute("SELECT COUNT(*) FROM posts").fetchone()[0] == 0:
        _seed_posts(db)

    if db.execute("SELECT COUNT(*) FROM diaries").fetchone()[0] == 0:
        _seed_diaries(db)

    if db.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        db.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?,?)",
            ("admin", _hash_password("cyberdiary2026"))
        )
        db.commit()
        print("=" * 55)
        print("  Default admin created:")
        print("    Username : admin")
        print("    Password : cyberdiary2026")
        print("  Change this at /admin/settings !")
        print("=" * 55)

    db.close()


def _seed_posts(db):
    posts = [
        {
            "slug": "what-is-encryption",
            "title": "What Is Encryption? Your Digital Lockbox Explained",
            "excerpt": "Encryption turns your private messages into unreadable scrambled data — so only the right person can unlock it.",
            "category": "Fundamentals", "tag_color": "#e8678a", "hero_icon": "🔒",
            "photo": "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=900&q=85",
            "read_time": "5 min read",
            "content_json": json.dumps([
                {"type": "intro", "text": "Imagine writing a secret letter in a code only your friend knows. Even if someone intercepts it, they just see gibberish. That's encryption — and it protects almost everything you do online."},
                {"type": "heading", "text": "The Simple Version"},
                {"type": "paragraph", "text": "Encryption takes readable data (plaintext) and scrambles it using a mathematical algorithm and a key — producing unreadable ciphertext. Only someone with the correct key can reverse the process."},
                {"type": "analogy", "icon": "🗝️", "title": "The Padlock Analogy", "text": "Think of encryption like a padlock. You lock a box (encrypt), send it through the mail (internet), and only the person with the matching key can open it (decrypt). Even the mailman can't read what's inside."},
                {"type": "heading", "text": "Where You Use It Every Day"},
                {"type": "list", "entries": ["That padlock icon in your browser? That's HTTPS using encryption.", "WhatsApp and Signal messages are end-to-end encrypted.", "Your phone's passcode encrypts all stored data.", "Online banking transactions are always encrypted."]},
                {"type": "takeaway", "text": "Without encryption, every password, message, and credit card number you send online would be readable by anyone watching network traffic. It's the backbone of all digital privacy."}
            ]),
        },
        {
            "slug": "phishing-attacks-explained",
            "title": "Phishing: When Hackers Fish for Your Password",
            "excerpt": "Phishing is the art of tricking you into handing over your credentials — and it works because it targets humans, not computers.",
            "category": "Threats", "tag_color": "#d44f7a", "hero_icon": "🎣",
            "photo": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=900&q=85",
            "read_time": "6 min read",
            "content_json": json.dumps([
                {"type": "intro", "text": "You get an urgent email: 'Your account has been compromised. Click here immediately to secure it.' The logo looks real. But something is very wrong — you've just been phished."},
                {"type": "heading", "text": "What Makes Phishing Work"},
                {"type": "paragraph", "text": "Phishing exploits human psychology, not software vulnerabilities. Attackers create urgency, fear, or curiosity to override your critical thinking."},
                {"type": "analogy", "icon": "🎭", "title": "The Costume Party Trick", "text": "A phishing attack is like someone wearing a convincing bank uniform asking for your PIN. The uniform looks real, the authority feels legitimate — but it's all a costume."},
                {"type": "heading", "text": "How to Spot a Phish"},
                {"type": "list", "entries": ["Hover over links before clicking — does the URL match the brand?", "Check the sender's actual email address, not just the display name.", "Urgent language ('Act NOW!') is a major red flag.", "Legitimate companies never ask for passwords via email."]},
                {"type": "takeaway", "text": "Pause before you click. Phishing only works when you're in a rush. Take 10 seconds to verify the sender and URL."}
            ]),
        },
        {
            "slug": "two-factor-authentication",
            "title": "Two-Factor Auth: Why Your Password Alone Isn't Enough",
            "excerpt": "A stolen password is useless when there's a second lock on the door. Here's why 2FA is one of the most powerful security upgrades you can make.",
            "category": "Defense", "tag_color": "#b07a95", "hero_icon": "🛡️",
            "photo": "https://images.unsplash.com/photo-1555421689-d68471e189f2?w=900&q=85",
            "read_time": "4 min read",
            "content_json": json.dumps([
                {"type": "intro", "text": "In 2024, billions of passwords were leaked in data breaches. Two-factor authentication (2FA) is the insurance policy that makes a stolen password worthless."},
                {"type": "heading", "text": "The Two Factors"},
                {"type": "comparison", "entries": [
                    {"name": "Something You Know", "icon": "🧠", "desc": "Passwords, PINs. Can be guessed, stolen, or phished.", "example": "Your Gmail password"},
                    {"name": "Something You Have", "icon": "📱", "desc": "A physical device — your phone or a hardware key. Much harder to steal remotely.", "example": "Code from Google Authenticator"}
                ]},
                {"type": "heading", "text": "2FA Methods Ranked"},
                {"type": "list", "entries": ["Hardware keys (YubiKey) — nearly impossible to phish.", "Authenticator apps (Google Authenticator, Authy) — excellent and free.", "Push notifications (Duo) — convenient and strong.", "SMS codes — better than nothing, but vulnerable to SIM swapping."]},
                {"type": "takeaway", "text": "Enable 2FA on every account that matters. This single step blocks 99% of automated account takeover attacks."}
            ]),
        },
        {
            "slug": "what-is-a-vpn",
            "title": "VPNs Demystified: What They Do (and Don't) Protect",
            "excerpt": "VPN ads promise total online anonymity. The reality is more nuanced — VPNs are powerful, but understanding their limits is just as important.",
            "category": "Privacy", "tag_color": "#9b59b6", "hero_icon": "🌐",
            "photo": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=900&q=85",
            "read_time": "7 min read",
            "content_json": json.dumps([
                {"type": "intro", "text": "VPN stands for Virtual Private Network. Ads make it sound like a magic invisibility cloak for the internet. It's actually more like a secure tunnel."},
                {"type": "heading", "text": "What a VPN Actually Does"},
                {"type": "paragraph", "text": "Your internet traffic is encrypted and routed through a server in another location. Your ISP can't see what you're doing, and websites see the VPN server's IP address instead of yours."},
                {"type": "analogy", "icon": "🚇", "title": "The Secret Tunnel", "text": "Imagine a network of roads where anyone can watch which roads you take. A VPN is like a private underground tunnel — but the tunnel owner still knows exactly where you're going."},
                {"type": "heading", "text": "Protects vs Doesn't Protect"},
                {"type": "list", "entries": ["Hides browsing from your ISP.", "Protects you on public WiFi.", "Does NOT protect against malware on your device.", "Does NOT stop browser cookies tracking you."]},
                {"type": "takeaway", "text": "A VPN is great for ISP privacy and public WiFi. It is not a silver bullet — use it as one layer in a broader privacy strategy."}
            ]),
        },
        {
            "slug": "social-engineering",
            "title": "Social Engineering: Hacking the Human Brain",
            "excerpt": "The most sophisticated firewall can't stop an employee who's been manipulated into handing over their login. Social engineering is cybercrime's most effective weapon.",
            "category": "Threats", "tag_color": "#d44f7a", "hero_icon": "🧠",
            "photo": "https://images.unsplash.com/photo-1573165231977-3f0e27806045?w=900&q=85",
            "read_time": "6 min read",
            "content_json": json.dumps([
                {"type": "intro", "text": "Kevin Mitnick, once the world's most wanted hacker, said he rarely needed to break computer systems — he just asked people for what he needed. That's social engineering."},
                {"type": "heading", "text": "Psychological Triggers Attackers Use"},
                {"type": "list", "entries": ["Authority: 'This is IT support. I need your password.'", "Urgency: 'Your account will be deleted in 2 hours.'", "Reciprocity: Giving something small before asking for something big.", "Social proof: 'All your colleagues have already done this.'"]},
                {"type": "analogy", "icon": "🎪", "title": "The Con Artist Playbook", "text": "Social engineering is digital con artistry. A con artist builds trust, creates a false scenario, and exploits your instincts."},
                {"type": "takeaway", "text": "Verify before you trust. Any request for credentials — even from someone who sounds official — should be verified through a separate, known channel."}
            ]),
        },
        {
            "slug": "password-managers",
            "title": "Password Managers: One Password to Rule Them All",
            "excerpt": "Using the same password everywhere is a disaster waiting to happen. Password managers solve this elegantly.",
            "category": "Defense", "tag_color": "#b07a95", "hero_icon": "🗄️",
            "photo": "https://images.unsplash.com/photo-1586931793709-82f67f0f8c58?w=900&q=85",
            "read_time": "5 min read",
            "content_json": json.dumps([
                {"type": "intro", "text": "The average person has 100+ online accounts. Remembering a unique, strong password for each is impossible — so most people reuse passwords. Password managers break this cycle."},
                {"type": "heading", "text": "How They Work"},
                {"type": "paragraph", "text": "A password manager is an encrypted vault. You remember one strong master password. The manager generates, stores, and auto-fills unique passwords for every site."},
                {"type": "analogy", "icon": "🏦", "title": "The Safety Deposit Box", "text": "Your password manager is like a bank vault. You need one key (master password) to enter. Inside, each box holds a unique key for a different account."},
                {"type": "heading", "text": "What to Look For"},
                {"type": "list", "entries": ["Zero-knowledge architecture: the company cannot see your passwords.", "AES-256 encryption with PBKDF2 or Argon2 key derivation.", "2FA support for accessing the vault itself.", "Cross-device sync so you're never locked out."]},
                {"type": "takeaway", "text": "If you do one thing after reading this blog, install a password manager. It's the single highest-impact security improvement most people can make in under 30 minutes."}
            ]),
        },
    ]
    for p in posts:
        db.execute(
            """INSERT INTO posts (slug,title,excerpt,category,tag_color,hero_icon,photo,read_time,content_json)
               VALUES (:slug,:title,:excerpt,:category,:tag_color,:hero_icon,:photo,:read_time,:content_json)""",
            p
        )
    db.commit()


def _seed_diaries(db):
    data = [
        ("Rose Petal",       "Classic pink — the original CyberDiary",  24.99, "#e8678a","#fce4ec","#d44f7a","#fff0f5","🌸",200,1,"Most Popular"),
        ("Midnight Lavender","Dreamy purple for late-night learning",    24.99, "#9b59b6","#f3e5f5","#7d3c98","#faf0ff","💜",200,1,"New"),
        ("Ocean Mint",       "Fresh teal — cool, calm, and secure",      24.99, "#26a69a","#e0f2f1","#00796b","#f0fffe","🌊",200,1,None),
        ("Golden Hour",      "Warm gold — radiant and resilient",        27.99, "#f4a829","#fff8e1","#e08c00","#fffbf0","✨",240,1,"Premium"),
        ("Cherry Blossom",   "Soft coral — delicate but powerful",       24.99, "#ef6c6c","#fce8e8","#d44444","#fff5f5","🌺",200,1,None),
        ("Starry Night",     "Deep navy — mystery and encryption",       27.99, "#3a5ba0","#e8eef8","#1a3a7a","#f0f4ff","🌙",240,1,"Premium"),
        ("Forest Sage",      "Earthy green — grounded and safe",         24.99, "#5a9e6f","#e8f5e9","#3d7a52","#f2faf4","🌿",200,0,"Sold Out"),
        ("Sunset Peach",     "Warm peach — bright and cheerful",         24.99, "#f4845f","#fde8df","#d4633a","#fff8f5","🍑",200,1,None),
    ]
    base = ["Guided cybersecurity prompts","Password log pages","Threat tracker","Ribbon bookmark"]
    for row in data:
        name,tagline,price,cm,cl,ca,cb,emoji,pages,in_stock,badge = row
        feats = base + (["Foil cover"] if pages == 240 else [])
        db.execute(
            """INSERT INTO diaries (name,tagline,price,color_main,color_light,color_accent,
               color_bg,emoji,pages,features_json,in_stock,badge)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (name,tagline,price,cm,cl,ca,cb,emoji,pages,json.dumps(feats),in_stock,badge)
        )
    db.commit()


# ─────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────

def _hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    h    = hashlib.sha256((salt + pw).encode()).hexdigest()
    return f"{salt}:{h}"


def _check_password(pw: str, stored: str) -> bool:
    try:
        salt, h = stored.split(":", 1)
        return hashlib.sha256((salt + pw).encode()).hexdigest() == h
    except Exception:
        return False


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


def _diary(row) -> dict:
    d = dict(row)
    d["features"] = json.loads(d.pop("features_json", "[]"))
    d["in_stock"]  = bool(d["in_stock"])
    return d


def _post(row) -> dict:
    p = dict(row)
    p["content"] = json.loads(p.pop("content_json", "[]"))
    try:
        dt      = datetime.strptime(p["created_at"][:10], "%Y-%m-%d")
        p["date"] = dt.strftime("%B %-d, %Y")
    except Exception:
        p["date"] = p["created_at"][:10]
    return p


# ─────────────────────────────────────────────────────────────
# CART HELPERS
# ─────────────────────────────────────────────────────────────

def get_cart():
    return session.get("cart", {})


def cart_count():
    return sum(get_cart().values())


def cart_total():
    total = 0.0
    for did, qty in get_cart().items():
        row = query("SELECT price FROM diaries WHERE id=?", (int(did),), one=True)
        if row:
            total += row["price"] * qty
    return round(total, 2)


app.jinja_env.globals.update(cart_count=cart_count)


# ─────────────────────────────────────────────────────────────
# ADMIN AUTH DECORATOR
# ─────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.path))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────────
# PUBLIC ROUTES — blog
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    rows  = query("SELECT * FROM posts WHERE published=1 ORDER BY created_at DESC")
    posts = [_post(r) for r in rows]
    if not posts:
        return render_template("index.html", featured=None, all_posts=[], categories=[])
    categories = list({p["category"] for p in posts})
    return render_template("index.html", featured=posts[0],
                           all_posts=posts, categories=categories)


@app.route("/post/<slug>")
def post(slug):
    row = query("SELECT * FROM posts WHERE slug=? AND published=1", (slug,), one=True)
    if not row:
        abort(404)
    article     = _post(row)
    related_rows = query(
        "SELECT * FROM posts WHERE category=? AND slug!=? AND published=1 LIMIT 2",
        (article["category"], slug)
    )
    return render_template("post.html", post=article,
                           related=[_post(r) for r in related_rows])


@app.route("/category/<name>")
def category(name):
    rows = query(
        "SELECT * FROM posts WHERE category=? AND published=1 ORDER BY created_at DESC",
        (name,)
    )
    return render_template("category.html",
                           posts=[_post(r) for r in rows], category_name=name)


# ─────────────────────────────────────────────────────────────
# PUBLIC ROUTES — shop
# ─────────────────────────────────────────────────────────────

@app.route("/shop")
def shop():
    rows = query("SELECT * FROM diaries ORDER BY id")
    return render_template("shop.html", diaries=[_diary(r) for r in rows])


@app.route("/shop/diary/<int:diary_id>")
def diary_detail(diary_id):
    row = query("SELECT * FROM diaries WHERE id=?", (diary_id,), one=True)
    if not row:
        abort(404)
    others = [_diary(r) for r in
              query("SELECT * FROM diaries WHERE id!=? LIMIT 3", (diary_id,))]
    return render_template("diary_detail.html", diary=_diary(row), others=others)


# ─────────────────────────────────────────────────────────────
# CART ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/cart")
def cart():
    items = []
    for did, qty in get_cart().items():
        row = query("SELECT * FROM diaries WHERE id=?", (int(did),), one=True)
        if row:
            d = _diary(row)
            items.append({"diary": d, "qty": qty,
                          "subtotal": round(d["price"] * qty, 2)})
    return render_template("cart.html", items=items, total=cart_total())


@app.route("/cart/add/<int:diary_id>", methods=["POST"])
def add_to_cart(diary_id):
    cart    = get_cart()
    key     = str(diary_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart
    return redirect(request.form.get("next", "/cart"))


@app.route("/cart/remove/<int:diary_id>", methods=["POST"])
def remove_from_cart(diary_id):
    cart = get_cart()
    cart.pop(str(diary_id), None)
    session["cart"] = cart
    return redirect("/cart")


@app.route("/cart/update/<int:diary_id>", methods=["POST"])
def update_cart(diary_id):
    cart = get_cart()
    key  = str(diary_id)
    qty  = int(request.form.get("qty", 1))
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session["cart"] = cart
    return redirect("/cart")


# ─────────────────────────────────────────────────────────────
# CHECKOUT — saves order to DB
# ─────────────────────────────────────────────────────────────

@app.route("/checkout")
def checkout():
    items = []
    for did, qty in get_cart().items():
        row = query("SELECT * FROM diaries WHERE id=?", (int(did),), one=True)
        if row:
            d = _diary(row)
            items.append({"diary": d, "qty": qty,
                          "subtotal": round(d["price"] * qty, 2)})
    return render_template("checkout.html", items=items, total=cart_total())


@app.route("/checkout/confirm", methods=["POST"])
def checkout_confirm():
    total    = cart_total()
    shipping = 0.0 if total >= 40 else 4.99
    order_id = execute(
        """INSERT INTO orders
           (customer_name,customer_email,address,city,postal,total,shipping,status)
           VALUES (?,?,?,?,?,?,?,'pending')""",
        (request.form.get("name","Friend"),
         request.form.get("email",""),
         request.form.get("address",""),
         request.form.get("city",""),
         request.form.get("postal",""),
         round(total + shipping, 2), shipping)
    )
    for did, qty in get_cart().items():
        row = query("SELECT * FROM diaries WHERE id=?", (int(did),), one=True)
        if row:
            execute(
                "INSERT INTO order_items (order_id,diary_id,diary_name,price,qty) VALUES (?,?,?,?,?)",
                (order_id, int(did), row["name"], row["price"], qty)
            )
    session["cart"] = {}
    return render_template("order_confirm.html",
                           name=request.form.get("name","Friend"),
                           order_id=order_id)


# ─────────────────────────────────────────────────────────────
# ADMIN — login / logout
# ─────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        row = query("SELECT * FROM admins WHERE username=?",
                    (request.form.get("username",""),), one=True)
        if row and _check_password(request.form.get("password",""),
                                   row["password_hash"]):
            session["admin_logged_in"] = True
            session["admin_username"]  = row["username"]
            return redirect(request.args.get("next", "/admin"))
        flash("Invalid username or password.", "error")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")


# ─────────────────────────────────────────────────────────────
# ADMIN — dashboard
# ─────────────────────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin_dashboard():
    post_count  = query("SELECT COUNT(*) AS c FROM posts",  one=True)["c"]
    order_count = query("SELECT COUNT(*) AS c FROM orders", one=True)["c"]
    diary_count = query("SELECT COUNT(*) AS c FROM diaries",one=True)["c"]
    revenue     = query(
        "SELECT COALESCE(SUM(total),0) AS r FROM orders WHERE status!='cancelled'",
        one=True)["r"]
    recent_orders = query("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")
    return render_template("admin/dashboard.html",
                           post_count=post_count, order_count=order_count,
                           diary_count=diary_count, revenue=round(revenue,2),
                           recent_orders=recent_orders)


# ─────────────────────────────────────────────────────────────
# ADMIN — posts CRUD
# ─────────────────────────────────────────────────────────────

@app.route("/admin/posts")
@admin_required
def admin_posts():
    rows = query("SELECT * FROM posts ORDER BY created_at DESC")
    return render_template("admin/posts.html", posts=rows)


@app.route("/admin/posts/new", methods=["GET","POST"])
@admin_required
def admin_post_new():
    if request.method == "POST":
        f    = request.form
        slug = f.get("slug") or _slugify(f.get("title","post"))
        if query("SELECT id FROM posts WHERE slug=?", (slug,), one=True):
            slug = f"{slug}-{secrets.token_hex(3)}"
        body    = f.get("body","")
        content = [{"type":"paragraph","text":p.strip()}
                   for p in body.split("\n\n") if p.strip()]
        execute(
            """INSERT INTO posts
               (slug,title,excerpt,category,tag_color,hero_icon,photo,read_time,content_json,published)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (slug, f.get("title"), f.get("excerpt"),
             f.get("category","Fundamentals"), f.get("tag_color","#e8678a"),
             f.get("hero_icon","📝"), f.get("photo",""),
             f.get("read_time","5 min read"), json.dumps(content),
             1 if f.get("published") else 0)
        )
        flash("Post published! 🌸", "success")
        return redirect(url_for("admin_posts"))
    return render_template("admin/post_form.html", post=None, body="", action="new")


@app.route("/admin/posts/<int:post_id>/edit", methods=["GET","POST"])
@admin_required
def admin_post_edit(post_id):
    row = query("SELECT * FROM posts WHERE id=?", (post_id,), one=True)
    if not row:
        abort(404)
    if request.method == "POST":
        f       = request.form
        body    = f.get("body","")
        content = [{"type":"paragraph","text":p.strip()}
                   for p in body.split("\n\n") if p.strip()]
        execute(
            """UPDATE posts SET title=?,excerpt=?,category=?,tag_color=?,hero_icon=?,
               photo=?,read_time=?,content_json=?,published=?,updated_at=datetime('now')
               WHERE id=?""",
            (f.get("title"), f.get("excerpt"),
             f.get("category","Fundamentals"), f.get("tag_color","#e8678a"),
             f.get("hero_icon","📝"), f.get("photo",""),
             f.get("read_time","5 min read"), json.dumps(content),
             1 if f.get("published") else 0, post_id)
        )
        flash("Post updated! 🌸", "success")
        return redirect(url_for("admin_posts"))
    p    = _post(row)
    body = "\n\n".join(
        b.get("text","") for b in p["content"]
        if b.get("type") in ("paragraph","intro","takeaway")
    )
    return render_template("admin/post_form.html",
                           post=dict(row), body=body, action="edit")


@app.route("/admin/posts/<int:post_id>/delete", methods=["POST"])
@admin_required
def admin_post_delete(post_id):
    execute("DELETE FROM posts WHERE id=?", (post_id,))
    flash("Post deleted.", "success")
    return redirect(url_for("admin_posts"))


# ─────────────────────────────────────────────────────────────
# ADMIN — orders
# ─────────────────────────────────────────────────────────────

@app.route("/admin/orders")
@admin_required
def admin_orders():
    rows = query("SELECT * FROM orders ORDER BY created_at DESC")
    return render_template("admin/orders.html", orders=rows)


@app.route("/admin/orders/<int:order_id>")
@admin_required
def admin_order_detail(order_id):
    order = query("SELECT * FROM orders WHERE id=?", (order_id,), one=True)
    if not order:
        abort(404)
    items = query("SELECT * FROM order_items WHERE order_id=?", (order_id,))
    return render_template("admin/order_detail.html", order=order, items=items)


@app.route("/admin/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def admin_order_status(order_id):
    status = request.form.get("status","pending")
    execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    flash(f"Order #{order_id} marked as {status}.", "success")
    return redirect(url_for("admin_order_detail", order_id=order_id))


# ─────────────────────────────────────────────────────────────
# ADMIN — diaries stock management
# ─────────────────────────────────────────────────────────────

@app.route("/admin/diaries")
@admin_required
def admin_diaries():
    rows = query("SELECT * FROM diaries ORDER BY id")
    return render_template("admin/diaries.html", diaries=rows)


@app.route("/admin/diaries/<int:diary_id>/stock", methods=["POST"])
@admin_required
def admin_diary_stock(diary_id):
    in_stock = 1 if request.form.get("in_stock") == "1" else 0
    badge    = None if in_stock else "Sold Out"
    execute("UPDATE diaries SET in_stock=?, badge=? WHERE id=?",
            (in_stock, badge, diary_id))
    flash("Stock updated. 🌸", "success")
    return redirect(url_for("admin_diaries"))


# ─────────────────────────────────────────────────────────────
# ADMIN — settings
# ─────────────────────────────────────────────────────────────

@app.route("/admin/settings", methods=["GET","POST"])
@admin_required
def admin_settings():
    if request.method == "POST":
        current = request.form.get("current_password","")
        new_pw  = request.form.get("new_password","")
        confirm = request.form.get("confirm_password","")
        uname   = session.get("admin_username")
        row     = query("SELECT * FROM admins WHERE username=?", (uname,), one=True)
        if not row or not _check_password(current, row["password_hash"]):
            flash("Current password is incorrect.", "error")
        elif new_pw != confirm:
            flash("New passwords do not match.", "error")
        elif len(new_pw) < 8:
            flash("Password must be at least 8 characters.", "error")
        else:
            execute("UPDATE admins SET password_hash=? WHERE username=?",
                    (_hash_password(new_pw), uname))
            flash("Password updated! 🌸", "success")
    return render_template("admin/settings.html",
                           username=session.get("admin_username"))


# ─────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, host="0.0.0.0", port=5000)
