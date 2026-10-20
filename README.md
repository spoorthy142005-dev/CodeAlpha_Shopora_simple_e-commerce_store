# Shopora — Everything you love, all in one place.

A full-featured, production-ready Indian e-commerce platform built with **Django 5.2, Python 3.13, WhiteNoise, PostgreSQL/SQLite, HTML5, Vanilla CSS3, and Vanilla JavaScript**, inspired by India's leading online shopping experiences (Amazon India, Flipkart, Myntra).

---

## 🌟 Key Features

### 1. Indian E-Commerce Design & UX
- **Festive Announcement Bar**: Top promotional ribbon with promo codes (`FESTIVE10`), festive discounts, and free delivery thresholds.
- **Shopora Navigation Bar**: Brand logo, tagline ("Everything you love, all in one place."), PIN code delivery detector, responsive search with category scope, user authentication state, live Wishlist counter, and Cart counter.
- **Category Navigation Strip**: 11 core Indian market retail categories with custom iconography and responsive horizontal scrolling.
- **Hero Promotional Banner & Deals of the Day**: Flash sale cards with countdown timers, discount badges (up to 70% off), and bank EMI offers.
- **Product Cards**: Indian Rupee (`₹`) pricing, strikethrough MRP, discount percentage badges, "Shopora Assured" certification tag, dynamic star ratings, and one-click wishlist toggling.
- **Product Detail View**:
  - High-resolution studio image gallery with multi-angle perspective thumbnails.
  - Transparent price breakdown with Indian tax and savings alert.
  - Bank offers box (HDFC, SBI, Axis, RuPay UPI, No-Cost EMI).
  - Live 6-digit Indian PIN code delivery checker (`/api/check-pincode/`).
  - Bulleted key highlights and technical specifications table.
  - Dual call-to-action buttons: **ADD TO CART** and **BUY NOW**.
  - Verified product guarantee and price audit timestamp.

### 2. Wishlist System
- Dedicated user wishlist (`/wishlist/`) protected by authentication.
- Single-click toggle from product cards or detail pages with safe HTTP referer redirection.
- Direct **Move to Cart** action with automatic stock check and inventory validation.

### 3. Shopping Cart, Inventory Concurrency & Safe Checkout
- Multi-item shopping cart with quantity adjustment controls capped at retail limits (max 10 items per product).
- Transparent price card: MRP total, discount on MRP, packaging fee (₹29), and delivery charge (Free for orders ₹499+).
- **Concurrency-Safe Checkout**:
  - `transaction.atomic()` with deterministic row-level database locking (`select_for_update()`) ordered by product ID to prevent deadlocks and race conditions.
  - Exact stock deduction preventing overselling or negative inventory.
  - Snapshot pricing preserved in `OrderItem` to protect against subsequent price changes.
  - Indian delivery form with 10-digit mobile number validation and 6-digit PIN code checking.
  - Home vs Work delivery address tags.
  - Cash on Delivery (COD) and UPI/NetBanking payment options.

---

## 📦 Verified 245-Product Indian Catalog

The catalog includes **245 authentic products** across 11 retail categories:
1. **Mobiles & Tablets** (23 products): Apple iPhone 15, Samsung Galaxy S24 Ultra, OnePlus 12, Google Pixel 8 Pro, iPad Air M2, Xiaomi 14 Ultra.
2. **Laptops & Computers** (22 products): Apple MacBook Air M2, Dell XPS 13, Lenovo Legion Pro 5i, ASUS ROG Zephyrus G14, HP Pavilion 15.
3. **Electronics & Entertainment** (22 products): Sony Bravia 55" 4K Smart TV, Samsung Crystal 4K, LG OLED C3, PlayStation 5, Xbox Series X, Canon EOS R50.
4. **Audio & Headphones** (23 products): Sony WH-1000XM5, Bose QuietComfort 45, Apple AirPods Pro 2, boAt Rockerz 450, JBL Flip 6.
5. **Accessories & Peripherals** (22 products): Logitech MX Master 3S, Keychron K2, SanDisk Extreme 1TB SSD, Anker GaN Charger, Belkin Multiport Hub.
6. **Smart Home & Security** (22 products): Xiaomi Smart Camera C300, Dyson Pure Cool TP07, TP-Link Tapo Smart Plugs, Qubo Smart Door Lock.
7. **Fashion & Clothing** (22 products): Levi's 511 Slim Jeans, Allen Solly Shirts, FabIndia Pure Cotton Kurtas, Manyavar Sherwanis, Biba Sets.
8. **Footwear** (22 products): Nike Air Monarch IV, Air Jordan 1 Low, Adidas Ultraboost Light, Woodland Leather Boots, Red Tape Classic Sneakers.
9. **Watches & Wearables** (23 products): Titan Neo & Edge Ceramic, Casio G-Shock CasiOak, Fossil Gen 6, Ray-Ban Aviators, Wildhorn Wallets.
10. **Home & Kitchen** (22 products): Philips Digital Air Fryer HD9200, Prestige Iris 750W Mixer, Pigeon Kettle, Wonderchef Cookware, Dyson V8.
11. **Beauty & Grooming** (22 products): Philips Beard Trimmer, Minimalist Serums, Kama Ayurveda Pure Rose Water, Forest Essentials.

> **Idempotent Seeding**: Running `python manage.py seed_catalog` safely updates existing product details and downloads missing gallery photos without duplicating records or damaging existing customer orders.

---

## 🔒 Production Security Hardening

- **Environment-Variable Driven**: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, and SSL parameters managed securely via `.env`.
- **Zero-Warning Production Check**: Passes `python manage.py check --deploy` with 0 warnings:
  - `SECURE_SSL_REDIRECT = True`
  - `SESSION_COOKIE_SECURE = True`
  - `CSRF_COOKIE_SECURE = True`
  - `SECURE_BROWSER_XSS_FILTER = True`
  - `SECURE_CONTENT_TYPE_NOSNIFF = True`
  - `X_FRAME_OPTIONS = 'DENY'`
  - `SECURE_HSTS_SECONDS = 31536000` (1 Year) with subdomains and preload enabled.
- **Static Asset Delivery**: WhiteNoise (`CompressedStaticFilesStorage`) configured with cache headers and gzip/brotli compression.
- **Open Redirect Protection**: Safe redirect helper verifies allowed host and scheme before redirecting from auth and cart actions.
- **Input Validation**: Strict Indian PIN code regex (`^[1-9][0-9]{5}$`) and 10-digit mobile number regex (`^[6-9]\d{9}$`).

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13
- Git

### 2. Clone and Setup Environment
```bash
git clone <repository-url>
cd e-commerce-website

# Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Catalog
```bash
# Apply database migrations
python manage.py migrate

# Seed 245 Indian products and categories
python manage.py seed_catalog
```

### 4. Run Automated Tests
```bash
python manage.py test
```
*Current test suite: **38 automated tests** passing with 100% success rate across Authentication, Catalog, Search, Filtering, Sorting, Wishlist, Cart, Stock Concurrency, Checkout, and Order Isolation.*

### 5. Launch Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🌐 Production Deployment Guide

### Recommended Hosting Platforms

| Platform | Recommended Tier | Database | Persistent Media | Estimated Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Render** *(Recommended)* | Web Service (Starter) | Managed PostgreSQL (Free / $7) | 5GB Persistent Disk ($1.25/mo) | Free tier available / ~$7 - $15/mo |
| **Railway** | Hobby Plan ($5 base) | Railway Postgres Plugin | Persistent Volume | ~$5 - $10/mo (usage-based) |
| **DigitalOcean** | Basic Droplet (1 vCPU, 1GB RAM) | Local Postgres / Managed DB | Block Storage Volume | ~$4 - $12/mo |
| **PythonAnywhere** | Hacker / Custom Web App | MySQL / Postgres addon | Local disk included | ~$5/mo |

---

### Deploying to Render (Step-by-Step)

Shopora includes a ready-to-use [`render.yaml`](file:///c:/Users/SPOORTHI/Downloads/New%20folder/e-commerce%20wesite/render.yaml) blueprint.

1. **Push your repository to GitHub**:
   ```bash
   git add .
   git commit -m "Production ready Shopora deployment"
   git push origin main
   ```

2. **Create Blueprint on Render**:
   - Log in to [Render.com](https://render.com).
   - Click **New +** &rarr; **Blueprint**.
   - Connect your GitHub repository.
   - Render automatically detects `render.yaml` and provisions:
     - Python Web Service with Gunicorn
     - PostgreSQL database (`shopora-db`)
     - 5GB persistent disk for product media (`/opt/render/project/src/media`)

3. **Set Production Environment Variables**:
   In your Render Dashboard &rarr; Service &rarr; **Environment**:
   - `DJANGO_DEBUG`: `False`
   - `DJANGO_SECRET_KEY`: *(Auto-generated 64-character secret key)*
   - `DJANGO_ALLOWED_HOSTS`: `your-app.onrender.com,yourcustomdomain.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://your-app.onrender.com,https://yourcustomdomain.com`
   - `SECURE_SSL_REDIRECT`: `True`

4. **Run Database Migrations & Initial Seed**:
   From the Render **Shell** tab:
   ```bash
   python manage.py migrate
   python manage.py seed_catalog
   ```

---

### Media Storage Strategy for Cloud Deployments

1. **Option A: Persistent Disk (Default on Render/Railway/VPS)**
   - Mount a persistent volume at `media/`.
   - Files uploaded or seeded remain preserved across zero-downtime redeploys.
   - Ideal for low-to-medium traffic without external cloud storage overhead.

2. **Option B: AWS S3 / Cloudflare R2 / Cloudinary (Scalable Multi-Server)**
   - Install `django-storages` and `boto3`.
   - Set `DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`.
   - Unlimited scale, global edge caching via Cloudflare CDN.

---

## ⚙️ Environment Variables Reference

| Variable | Required in Production | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | **Yes** | Dev insecure key | Cryptographic signing key (must be 50+ chars). |
| `DJANGO_DEBUG` | **Yes** | `True` | Set to `False` to enable security protections. |
| `DJANGO_ALLOWED_HOSTS` | **Yes** | `*` (when DEBUG) | Comma-separated domain names allowed to serve requests. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | **Yes** | *None* | Comma-separated list of origins for CSRF POST requests. |
| `DATABASE_URL` | Optional | SQLite `db.sqlite3` | PostgreSQL connection string (`postgres://user:pass@host:port/db`). |
| `SECURE_SSL_REDIRECT` | Optional | `True` (when not DEBUG)| Enforces HTTPS redirection for all HTTP traffic. |
| `SECURE_HSTS_SECONDS` | Optional | `31536000` (1 Year) | HTTP Strict Transport Security header duration. |
| `DJANGO_LOG_LEVEL` | Optional | `INFO` | Console logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## 🔑 Default Accounts (Development Only)

- **Staff / Admin Panel** (`http://127.0.0.1:8000/admin/`):
  - Username: `admin`
  - Password: `admin123`
- **Demo Customer Account**:
  - Username: `user1`
  - Password: `password123`

---

## 📄 License
MIT License. Built for educational and commercial e-commerce applications.
