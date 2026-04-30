from flask import Flask, render_template, request, abort
from datetime import datetime

app = Flask(__name__)

POSTS = [
    {
        "id": 1,
        "slug": "what-is-encryption",
        "title": "What Is Encryption? Your Digital Lockbox Explained",
        "category": "Fundamentals",
        "tag_color": "#00ff9f",
        "date": "April 18, 2026",
        "read_time": "5 min read",
        "excerpt": "Encryption turns your private messages into unreadable scrambled data — so only the right person can unlock it. Here's how it actually works.",
        "hero_icon": "🔒",
        "content": [
            {
                "type": "intro",
                "text": "Imagine writing a secret letter in a code only your friend knows. Even if someone intercepts it, they just see gibberish. That's encryption in a nutshell — and it protects almost everything you do online."
            },
            {
                "type": "heading",
                "text": "The Simple Version"
            },
            {
                "type": "paragraph",
                "text": "Encryption takes readable data (called plaintext) and scrambles it using a mathematical algorithm and a key — producing unreadable ciphertext. Only someone with the correct key can reverse the process and read the original data."
            },
            {
                "type": "analogy",
                "icon": "🗝️",
                "title": "The Padlock Analogy",
                "text": "Think of encryption like a padlock. You lock a box (encrypt), send it through the mail (internet), and only the person with the matching key can open it (decrypt). Even the mailman can't read what's inside."
            },
            {
                "type": "heading",
                "text": "Two Main Types"
            },
            {
                "type": "comparison",
                "entries": [
                    {
                        "name": "Symmetric Encryption",
                        "icon": "🔑",
                        "desc": "Same key locks and unlocks. Fast and efficient. Best for encrypting files on your own device.",
                        "example": "AES-256 (used by governments & banks)"
                    },
                    {
                        "name": "Asymmetric Encryption",
                        "icon": "🔐",
                        "desc": "Two keys: a public key (anyone can lock) and a private key (only you can unlock). Used for secure communication.",
                        "example": "RSA (used in HTTPS, email)"
                    }
                ]
            },
            {
                "type": "heading",
                "text": "Where You Use It Every Day"
            },
            {
                "type": "list",
                "entries": [
                    "That padlock icon in your browser? That's HTTPS using encryption.",
                    "WhatsApp and Signal messages are end-to-end encrypted.",
                    "Your phone's passcode encrypts all stored data.",
                    "Online banking transactions are always encrypted."
                ]
            },
            {
                "type": "takeaway",
                "text": "Without encryption, every password, message, and credit card number you send online would be readable by anyone watching network traffic. It's the backbone of all digital privacy."
            }
        ]
    },
    {
        "id": 2,
        "slug": "phishing-attacks-explained",
        "title": "Phishing: When Hackers Fish for Your Password",
        "category": "Threats",
        "tag_color": "#ff4d6d",
        "date": "April 14, 2026",
        "read_time": "6 min read",
        "excerpt": "Phishing is the art of tricking you into handing over your credentials. It's the #1 attack vector in cybersecurity — and it works because it targets humans, not computers.",
        "hero_icon": "🎣",
        "content": [
            {
                "type": "intro",
                "text": "You get an urgent email: 'Your account has been compromised. Click here immediately to secure it.' The logo looks real. The language sounds official. But something is very wrong — you've just been phished."
            },
            {
                "type": "heading",
                "text": "What Makes Phishing Work"
            },
            {
                "type": "paragraph",
                "text": "Phishing exploits human psychology, not software vulnerabilities. Attackers create a sense of urgency, fear, or curiosity to override your critical thinking. The goal: get you to click a malicious link or enter credentials on a fake site."
            },
            {
                "type": "analogy",
                "icon": "🎭",
                "title": "The Costume Party Trick",
                "text": "A phishing attack is like someone wearing a convincing bank uniform knocking on your door and asking for your PIN. The uniform (email design) looks real, the authority (bank branding) feels legitimate — but it's all a costume."
            },
            {
                "type": "heading",
                "text": "Common Phishing Flavors"
            },
            {
                "type": "comparison",
                "entries": [
                    {
                        "name": "Email Phishing",
                        "icon": "📧",
                        "desc": "Mass emails pretending to be banks, Netflix, Amazon. Cast wide nets hoping someone bites.",
                        "example": "'Your Netflix subscription has expired. Update now.'"
                    },
                    {
                        "name": "Spear Phishing",
                        "icon": "🎯",
                        "desc": "Targeted attacks using your name, employer, or recent activity to seem legitimate.",
                        "example": "'Hi [Your Name], re: the Q3 report you sent...'"
                    }
                ]
            },
            {
                "type": "heading",
                "text": "How to Spot a Phish"
            },
            {
                "type": "list",
                "entries": [
                    "Hover over links before clicking — does the URL match the brand?",
                    "Check the sender's actual email address, not just the display name.",
                    "Urgent language ('Act NOW!') is a major red flag.",
                    "Legitimate companies never ask for passwords via email.",
                    "Poor grammar or strange formatting can signal a fake."
                ]
            },
            {
                "type": "takeaway",
                "text": "Pause before you click. Phishing only works when you're in a rush. Take 10 seconds to verify the sender and URL — it could save your account, your money, or your entire company's data."
            }
        ]
    },
    {
        "id": 3,
        "slug": "two-factor-authentication",
        "title": "Two-Factor Auth: Why Your Password Alone Isn't Enough",
        "category": "Defense",
        "tag_color": "#ffd60a",
        "date": "April 10, 2026",
        "read_time": "4 min read",
        "excerpt": "A stolen password is useless when there's a second lock on the door. Here's why 2FA is one of the most powerful — and simple — security upgrades you can make.",
        "hero_icon": "🛡️",
        "content": [
            {
                "type": "intro",
                "text": "In 2024, billions of passwords were leaked in data breaches. If your password is out there, attackers can try it on every service you use. Two-factor authentication (2FA) is the insurance policy that makes a stolen password worthless."
            },
            {
                "type": "heading",
                "text": "The Three Factors of Authentication"
            },
            {
                "type": "paragraph",
                "text": "Authentication is proving you are who you claim to be. There are three ways to prove identity, and combining two of them is what makes 2FA powerful:"
            },
            {
                "type": "comparison",
                "entries": [
                    {
                        "name": "Something You Know",
                        "icon": "🧠",
                        "desc": "Passwords, PINs, security questions. Can be guessed, stolen, or phished.",
                        "example": "Your Gmail password"
                    },
                    {
                        "name": "Something You Have",
                        "icon": "📱",
                        "desc": "A physical device: your phone, a hardware key. Much harder to steal remotely.",
                        "example": "A one-time code from Google Authenticator"
                    }
                ]
            },
            {
                "type": "analogy",
                "icon": "🏦",
                "title": "The Bank Vault Approach",
                "text": "Banks use 2FA too: your debit card (something you have) + your PIN (something you know). Steal just the card? Useless without the PIN. Know the PIN? Useless without the card. Two layers, double the protection."
            },
            {
                "type": "heading",
                "text": "2FA Methods Ranked (Best to Worst)"
            },
            {
                "type": "list",
                "entries": [
                    "Hardware keys (YubiKey) — nearly impossible to phish. Best option.",
                    "Authenticator apps (Google Authenticator, Authy) — excellent and free.",
                    "Push notifications (Duo) — convenient and strong.",
                    "SMS codes — better than nothing, but vulnerable to SIM swapping attacks."
                ]
            },
            {
                "type": "takeaway",
                "text": "Enable 2FA on every account that matters: email, banking, social media. Use an authenticator app over SMS. This single step blocks 99% of automated account takeover attacks."
            }
        ]
    },
    {
        "id": 4,
        "slug": "what-is-a-vpn",
        "title": "VPNs Demystified: What They Do (and Don't) Protect",
        "category": "Privacy",
        "tag_color": "#7b2fff",
        "date": "April 6, 2026",
        "read_time": "7 min read",
        "excerpt": "VPN ads promise total online anonymity. The reality is more nuanced — VPNs are powerful tools, but understanding their limits is just as important as knowing their benefits.",
        "hero_icon": "🌐",
        "content": [
            {
                "type": "intro",
                "text": "VPN stands for Virtual Private Network. Ads make it sound like a magic invisibility cloak for the internet. It's actually more like a secure tunnel — useful, but it doesn't make you invisible to everyone."
            },
            {
                "type": "heading",
                "text": "What a VPN Actually Does"
            },
            {
                "type": "paragraph",
                "text": "When you use a VPN, your internet traffic is encrypted and routed through a server in another location. This means your Internet Service Provider (ISP) can't see what you're doing, and websites see the VPN server's IP address instead of yours."
            },
            {
                "type": "analogy",
                "icon": "🚇",
                "title": "The Secret Tunnel",
                "text": "Imagine a network of roads where anyone can watch which roads you take. A VPN is like a private underground tunnel. People on the surface roads can't see you traveling — but the tunnel owner knows exactly where you're going."
            },
            {
                "type": "heading",
                "text": "VPN: Protects vs Doesn't Protect"
            },
            {
                "type": "comparison",
                "entries": [
                    {
                        "name": "✅ What VPNs Protect",
                        "icon": "🟢",
                        "desc": "Your ISP seeing your browsing. Public WiFi snooping. Hiding your real IP from websites. Geographic content restrictions.",
                        "example": "Safe on coffee shop WiFi"
                    },
                    {
                        "name": "❌ What VPNs Don't Fix",
                        "icon": "🔴",
                        "desc": "Malware on your device. Browser cookies tracking you. Logging by the VPN provider itself. Phishing attacks.",
                        "example": "Still logged into Google? Google still knows."
                    }
                ]
            },
            {
                "type": "list",
                "entries": [
                    "Always choose a VPN with a verified no-logs policy.",
                    "Free VPNs often sell your browsing data — the product is you.",
                    "A VPN is most useful on public/untrusted networks.",
                    "For true anonymity, you'd also need Tor + much more."
                ]
            },
            {
                "type": "takeaway",
                "text": "A VPN is a great tool for privacy from your ISP and public WiFi protection. It is not a silver bullet. Use it as one layer in a broader privacy strategy, not as your only defense."
            }
        ]
    },
    {
        "id": 5,
        "slug": "social-engineering",
        "title": "Social Engineering: Hacking the Human Brain",
        "category": "Threats",
        "tag_color": "#ff4d6d",
        "date": "April 2, 2026",
        "read_time": "6 min read",
        "excerpt": "The most sophisticated firewall in the world can't stop an employee who's been manipulated into handing over their login. Social engineering is cybercrime's most effective weapon.",
        "hero_icon": "🧠",
        "content": [
            {
                "type": "intro",
                "text": "Kevin Mitnick, once the world's most wanted hacker, said he rarely needed to break computer systems — he just asked people for what he needed. Social engineering is the art of manipulating people into doing things or revealing information."
            },
            {
                "type": "heading",
                "text": "Core Psychological Triggers Attackers Use"
            },
            {
                "type": "list",
                "entries": [
                    "Authority: 'This is IT support. I need your password to fix a critical issue.'",
                    "Urgency: 'Your account will be deleted in 2 hours unless you act now.'",
                    "Reciprocity: Giving something small (a gift, a favor) before asking for something big.",
                    "Social proof: 'All your colleagues have already submitted their credentials.'"
                ]
            },
            {
                "type": "analogy",
                "icon": "🎪",
                "title": "The Con Artist Playbook",
                "text": "Social engineering is digital con artistry. A con artist builds trust, creates a false scenario, and exploits your instincts. Attackers do the same — except the 'con' targets your company's network access."
            },
            {
                "type": "heading",
                "text": "Real Attack Scenarios"
            },
            {
                "type": "comparison",
                "entries": [
                    {
                        "name": "Pretexting",
                        "icon": "📞",
                        "desc": "Creating a fabricated scenario to extract info. Example: calling IT pretending to be a new employee who forgot their login.",
                        "example": "Caused the 2020 Twitter hack"
                    },
                    {
                        "name": "Baiting",
                        "icon": "💾",
                        "desc": "Leaving infected USB drives in parking lots, hoping someone plugs one in out of curiosity.",
                        "example": "45% of people plug in found USB drives"
                    }
                ]
            },
            {
                "type": "takeaway",
                "text": "Verify before you trust. Any request for credentials, access, or sensitive data — even from someone who sounds official — should be verified through a separate, known channel. Call back on a number you look up yourself."
            }
        ]
    },
    {
        "id": 6,
        "slug": "password-managers",
        "title": "Password Managers: One Password to Rule Them All",
        "category": "Defense",
        "tag_color": "#ffd60a",
        "date": "March 29, 2026",
        "read_time": "5 min read",
        "excerpt": "Using the same password everywhere is a disaster waiting to happen. Password managers solve this elegantly — here's how they work and why they're safe.",
        "hero_icon": "🗄️",
        "content": [
            {
                "type": "intro",
                "text": "The average person has 100+ online accounts. Remembering a unique, strong password for each is impossible — so most people reuse passwords. When one site gets breached, attackers try that password everywhere else. Password managers break this cycle."
            },
            {
                "type": "heading",
                "text": "How Password Managers Work"
            },
            {
                "type": "paragraph",
                "text": "A password manager is an encrypted vault. You remember one strong master password. The manager generates, stores, and auto-fills unique, complex passwords for every site. The vault is encrypted with your master password, so even the company can't see your passwords."
            },
            {
                "type": "analogy",
                "icon": "🏦",
                "title": "The Safety Deposit Box",
                "text": "Your password manager is like a bank vault full of safety deposit boxes. You need one key (master password) to enter the vault. Inside, each box holds a unique key for a different account. Lose the vault key and you lose access — but nobody else can get in either."
            },
            {
                "type": "heading",
                "text": "What to Look For"
            },
            {
                "type": "list",
                "entries": [
                    "Zero-knowledge architecture: the company cannot see your passwords.",
                    "AES-256 encryption with PBKDF2 or Argon2 key derivation.",
                    "2FA support for accessing the vault itself.",
                    "Cross-device sync so you're never locked out.",
                    "Breach monitoring to alert you when a site is compromised."
                ]
            },
            {
                "type": "comparison",
                "entries": [
                    {
                        "name": "Strong Master Password",
                        "icon": "💪",
                        "desc": "Use a passphrase — four random words strung together. Long, memorable, hard to crack.",
                        "example": "correct-horse-battery-staple"
                    },
                    {
                        "name": "Top Options",
                        "icon": "⭐",
                        "desc": "Bitwarden (open-source, free), 1Password, and Dashlane are all excellent choices with strong security track records.",
                        "example": "Bitwarden is free & audited"
                    }
                ]
            },
            {
                "type": "takeaway",
                "text": "If you do one thing after reading this blog, install a password manager. It's the single highest-impact security improvement most people can make in under 30 minutes."
            }
        ]
    }
]


def get_all_posts():
    return POSTS


def get_post_by_slug(slug):
    return next((p for p in POSTS if p["slug"] == slug), None)


def get_posts_by_category(category):
    return [p for p in POSTS if p["category"].lower() == category.lower()]


@app.route("/")
def index():
    featured = POSTS[0]
    recent = POSTS[1:4]
    all_posts = POSTS
    categories = list({p["category"] for p in POSTS})
    return render_template("index.html", featured=featured, recent=recent,
                           all_posts=all_posts, categories=categories)


@app.route("/post/<slug>")
def post(slug):
    article = get_post_by_slug(slug)
    if not article:
        abort(404)
    related = [p for p in POSTS if p["category"] == article["category"] and p["slug"] != slug][:2]
    return render_template("post.html", post=article, related=related)


@app.route("/category/<name>")
def category(name):
    posts = get_posts_by_category(name)
    return render_template("category.html", posts=posts, category_name=name)


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
