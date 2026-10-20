# Shopora - Everything you love, all in one place.

A production-quality Indian online shopping website built with **Django, Python, SQLite, HTML5, Vanilla CSS3, and Vanilla JavaScript**, inspired by Flipkart, Amazon India, and Myntra.

---

## 🌟 Key Features

### 1. Indian E-Commerce Design & UX
- **Festive Announcement Bar**: Top banner showcasing festive discounts, free delivery thresholds, and promo codes (`FESTIVE10`).
- **Header**: Responsive navigation with brand logo ("Shopora"), tagline ("Everything you love, all in one place."), Pincode delivery picker, search bar with category selector, User Account menu, live Wishlist counter, and Cart counter.
- **Category Navigation Strip**: Quick access to all 8 core Indian retail categories with custom icons.
- **Hero Promotional Banner & Deals of the Day**: Flash sale cards with countdown timers, discount badges (up to 70% off), and bank EMI offers.
- **Product Cards**: Display star ratings (`4.5 ★`), Indian Rupee pricing (`₹1,299`), strikethrough MRP (`₹3,990`), discount percentages (`67% off`), "Shopora Assured" badge, and instant wishlist heart toggle.
- **Product Detail Page**:
  - Image gallery with clickable thumbnail switcher.
  - Indian Rupee price breakdown with savings alert.
  - Bank & Partner offers box (HDFC, SBI, RuPay UPI, No-Cost EMI).
  - Interactive 6-digit Indian PIN code delivery checker (`/api/check-pincode/`).
  - Key highlights bullet list and comprehensive technical specifications table.
  - Dual call-to-action buttons: **ADD TO CART** (Golden Yellow) and **BUY NOW** (Flipkart/Amazon Orange).
  - Genuine product guarantee and price verification metadata.
  - Related items recommendation carousel.

### 2. Wishlist System
- Dedicated Wishlist page (`/wishlist/`) for authenticated users.
- One-click wishlist toggle from product cards or detail pages.
- Direct **Move to Cart** action from the wishlist.

### 3. Shopping Cart & Checkout with Indian Address Details
- Itemized shopping cart with dynamic quantity adjustments and stock limits.
- Price details card with MRP total, discount on MRP, delivery fee calculation (Free above ₹499), and packaging fee (₹29).
- Indian Delivery Address Form:
  - Full Name
  - 10-digit Indian Mobile Number validation (starting with 6, 7, 8, or 9)
  - 6-digit Indian PIN code validation
  - City & State
  - Area, Street, House/Flat Number
  - Address Type (Home vs Work)
  - Payment Options: Cash on Delivery (COD) vs UPI / NetBanking / Cards (Demo)
- Transactional checkout (`transaction.atomic()`) with database row locks (`select_for_update()`), stock deduction, locked historical prices in `OrderItem`, and cart clearing.
- Detailed digital invoice receipt with shipment tracking timeline (Confirmed &rarr; Shipped &rarr; Out for Delivery &rarr; Delivered).

---

## 📦 Realistic 245-Product Catalog for the Indian Market

The catalog contains **245 realistic Indian-market products** across all 11 categories:
1. **Mobiles & Tablets** (23 products): Apple iPhone 15, Samsung Galaxy S24 Ultra, OnePlus 12, Google Pixel 8 Pro, iPad Air M2, Xiaomi 14 Ultra.
2. **Laptops & Computers** (22 products): Apple MacBook Air M2, Dell XPS 13, Lenovo Legion Pro 5i, ASUS ROG Zephyrus G14, HP Pavilion 15, ThinkPad E14.
3. **Electronics & Entertainment** (22 products): Sony Bravia 55" 4K Smart TV, Samsung Crystal 4K, LG OLED C3, PlayStation 5, Xbox Series X, Canon EOS R50, GoPro HERO 12.
4. **Audio & Headphones** (23 products): Sony WH-1000XM5, Bose QuietComfort 45, Apple AirPods Pro, boAt Rockerz 450, JBL Flip 6, Marshall Emberton II.
5. **Accessories & Peripherals** (22 products): Logitech MX Master 3S, Keychron K2 Mechanical Keyboard, SanDisk Extreme 1TB SSD, Anker 737 Power Bank, Belkin 7-in-1 Hub.
6. **Smart Home & Security** (22 products): Xiaomi Smart Camera C300, Dyson Pure Cool TP07, TP-Link Tapo Wi-Fi Plugs & Bulbs, Qubo Smart Door Lock, Eufy RoboVac G20.
7. **Fashion & Clothing** (22 products): Levi's 511 Slim Jeans, Allen Solly Shirts, FabIndia Pure Cotton Kurtas, Manyavar Sherwanis, Biba Anarkali Sets, Peter England Suits.
8. **Footwear** (22 products): Nike Air Monarch IV, Air Jordan 1 Low, Adidas Ultraboost Light, Woodland Leather Boots, Red Tape Classic Sneaker, Skechers Go Walk.
9. **Watches & Wearables** (23 products): Titan Neo Analog & Edge Ceramic, Casio Vintage & G-Shock CasiOak, Fossil Gen 6, Ray-Ban Aviators, Wildhorn Leather Wallets.
10. **Home & Kitchen** (22 products): Philips Digital Air Fryer HD9200, Prestige Iris 750W Mixer Grinder, Pigeon Kettle, Wonderchef Cookware, Dyson V8 Vacuum, Kent RO Purifier.
11. **Beauty & Grooming** (22 products): Philips Beard Trimmer BT1232, Minimalist Niacinamide & Salicylic Acid Serums, Kama Ayurveda Pure Rose Water, Forest Essentials Cleansers.

> **Honest Pricing Policy**: All prices reflect verified Indian retail MRP and selling prices in INR (`₹`). Products from brands with official non-discounted pricing (such as Forest Essentials and Kama Ayurveda) are displayed at their actual fixed MRP without artificial discounts.

---

## 🛠️ Technology Stack
- **Backend**: Python 3.13, Django 5.x
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS3 (Custom Responsive System), Vanilla JavaScript
- **Image Processing**: Pillow (local 800x800 high-res studio assets in `media/products/`)

---

## 🚀 Setup & Execution Instructions

1. **Activate Virtual Environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Run Database Migrations**:
   ```powershell
   python manage.py migrate
   ```

3. **Populate Indian E-Commerce Catalog & Assets**:
   ```powershell
   python manage.py seed_catalog
   ```

4. **Run Automated Test Suite**:
   ```powershell
   python manage.py test store
   ```

5. **Start Development Server**:
   ```powershell
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo Credentials
- **Admin Panel** (`http://127.0.0.1:8000/admin/`):
  - Username: `admin`
  - Password: `admin123`
- **Customer Account**:
  - Username: `user1`
  - Password: `password123`
