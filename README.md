# Leaf Letang Enterprises — Corporate Website

Professional corporate website for **Leaf Letang Enterprises**, a sustainable manufacturing enterprise in Letang Municipality, Morang, Koshi Province, Nepal.

**Tagline:** From Local Leaves to Sustainable Value.

## Features

- Premium, responsive public website (Home, About, Products, Process, Sustainability, Community, Gallery, Contact)
- Official logo and brand colour system
- Contact form with CSRF protection and database storage
- Secure admin panel (messages, products, gallery)
- SQLAlchemy models compatible with SQLite (dev) and PostgreSQL (production)
- SEO metadata, Open Graph, JSON-LD, robots.txt, sitemap
- Favicons and web manifest
- Vercel-ready Flask configuration
- Accessible, minimal JavaScript, respects reduced motion

## Technology

| Layer        | Stack                                      |
|--------------|--------------------------------------------|
| Frontend     | HTML5, CSS3, Vanilla JS                    |
| Backend      | Python, Flask, Jinja2                      |
| Database     | SQLite (dev) / PostgreSQL (prod via URL)   |
| Forms        | Flask-WTF, WTForms                         |
| Auth         | Session + Werkzeug password hashing        |
| Deploy       | Gunicorn, Vercel, Render/Railway/VPS       |

## Project Structure

```
leaf-letang/
├── app.py              # Application factory & entry
├── config.py           # Configuration
├── requirements.txt
├── vercel.json
├── api/index.py        # Vercel entry
├── models/             # SQLAlchemy models
├── routes/             # Blueprints (main, contact, admin)
├── templates/          # Jinja2 templates
├── static/             # CSS, JS, images, favicon
└── instance/           # Local SQLite (gitignored)
```

## Installation (Local)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env — set SECRET_KEY and optionally ADMIN_PASSWORD_HASH
python app.py
```

Open: http://127.0.0.1:5000

### Admin login (development)

If `ADMIN_PASSWORD_HASH` is not set:

- Username: `admin` (or value of `ADMIN_USERNAME`)
- Password: `change-me-on-first-login`

**Always set a proper hash for production:**

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-secure-password'))"
```

Put the output in `.env` as `ADMIN_PASSWORD_HASH=...`

## Environment Variables

See `.env.example`. Important:

- `SECRET_KEY` — required in production
- `DATABASE_URL` — SQLite by default; use PostgreSQL URL in production
- `ADMIN_USERNAME` / `ADMIN_PASSWORD_HASH`
- Optional: `COMPANY_EMAIL`, `COMPANY_PHONE`, social URLs

## Production

```bash
export FLASK_ENV=production
export SECRET_KEY=...
export DATABASE_URL=postgresql://...
export ADMIN_PASSWORD_HASH=...
gunicorn app:app --bind 0.0.0.0:8000
```

Do **not** use the Flask development server in production.

### Vercel

1. Push the repo to GitHub.
2. Import project in Vercel.
3. Set environment variables (`SECRET_KEY`, `DATABASE_URL` to a managed Postgres, `ADMIN_*`).
4. Deploy. The `vercel.json` and `api/index.py` route all traffic to the Flask app.

**Note:** Vercel’s filesystem is ephemeral — do not rely on local SQLite for permanent data. Use PostgreSQL (or similar) via `DATABASE_URL`.

## Image Replacement

- Logo: `static/images/logo.png` (official logo already placed)
- Product images: `static/images/products/`
- Gallery: place files in `static/images/gallery/` and register via Admin → Gallery
- Hero / factory / farmers: use placeholders until real photography is available. Do not present stock imagery as company photos.

## Contact Information

Company contact details (phone, email, social) are configured via environment variables. Leave blank if not verified — icons and fields will not invent data.

## Security

- Password hashing (Werkzeug)
- CSRF on forms
- Session-based admin auth
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, CSP, HSTS in production)
- No secrets in frontend or source control

## Licence & Attribution

Website built for Leaf Letang Enterprises. Official logo © Leaf Letang Enterprises. Do not redesign or distort the logo.

---

**Made in Letang, Nepal.**

## Public vs Admin Separation

The public website and admin panel are strictly separated:

- **Public** (`/`, `/about`, `/products`, …): no admin links, menus, or controls in any template, CSS, or JS.
- **Admin** (`/admin/login`, `/admin/dashboard`, …): private; requires authentication. `/admin` redirects to login when not signed in.
- Admin templates live under `templates/admin/` and use `admin/base.html` only.
- Admin CSS/JS (`admin.css`, `admin-responsive.css`, `admin.js`) are never loaded on public pages.
- `robots.txt` disallows `/admin`. Admin pages send `noindex, nofollow`.
- Content managed in admin (products, gallery, founders, settings, messages) appears on the public site as data only — never as management UI.
