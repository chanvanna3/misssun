# 🌻 MISS SUNFLOWER CAMBODIA - FULL-STACK WEB APPLICATION
> គេហទំព័រផ្លូវការ និងផ្ទាំងគ្រប់គ្រងទិន្នន័យផលិតផលថែរក្សាសម្រស់ Miss Sunflower Cambodia (Full-Stack Architecture & Clean Directory Structure)

---

## 🏗️ រចនាសម្ព័ន្ធគម្រោង (Full-Stack Project Structure)

គម្រោងនេះត្រូវបានរៀបចំជា **Full-Stack Architecture** យ៉ាងមានរបៀបរៀបរយ បែងចែកដាច់ស្រឡះរវាង **Frontend (ផ្នែកខាងមុខសម្រាប់ភ្ញៀវ)**, **Admin CMS (ផ្ទាំងគ្រប់គ្រងទិន្នន័យ)**, និង **Backend (ម៉ាស៊ីនបម្រើ API & មូលដ្ឋានទិន្នន័យ SQLite)**៖

```
website/
├── 🌐 frontend/                     # ផ្នែកគេហទំព័រខាងមុខ (Public Storefront)
│   ├── index.html                   # ទំព័រដើមចម្បង (Landing Page & Hero & Sliders)
│   ├── news-detail.html             # ទំព័រអានព័ត៌មាន និងអត្ថបទលម្អិត
│   ├── service-worker.js            # PWA / Offline Caching Service Worker
│   ├── css/
│   │   └── style.css                # Style ចម្បងប្រណិត Dark/Gold & Responsive
│   ├── js/
│   │   ├── app.js                   # Logic ចម្បងរបស់ Storefront & Sync API
│   │   ├── translations.js          # ប្រព័ន្ធបកប្រែ ២ ភាសា (ខ្មែរ / English)
│   │   └── products.js              # ទិន្នន័យផលិតផលបម្រុងទុក (Local Dataset)
│   ├── images/                      # រូបភាព Logo, Angkor Wat Header, Icons
│   └── miss sun prodcut/            # រូបថតផលិតផលពិតៗទាំងអស់ (HQ Product Photos)
│
├── ⚙️ dashboard_admin/               # ផ្ទាំងគ្រប់គ្រងទិន្នន័យ (Admin CMS Portal)
│   ├── index.html                   # ផ្ទាំងគ្រប់គ្រង Admin Dashboard ពេញលេញ (CMS Suite)
│   ├── admin.html                   # Direct Alias សម្រាប់ Admin Dashboard
│   ├── css/                         # Admin Custom Stylesheets
│   └── js/                          # Admin Management Scripts
│
├── 🗄️ backend/                       # ផ្នែកខាងក្រោយ (API & Database Layer)
│   ├── server.py                    # Standalone REST API & Static Server
│   ├── cms_db.py                    # SQLite Model, Table Schema & CRUD Functions
│   ├── requirements.txt             # Python Dependencies
│   ├── database/
│   │   ├── cms.db                   # មូលដ្ឋានទិន្នន័យ SQLite ពិតប្រាកដ (18 Tables)
│   │   └── schema.sql               # SQL Schema Dump ពេញលេញទាំងអស់
│   ├── data/
│   │   ├── products_seed.json       # Seed ទិន្នន័យផលិតផល ២០ មុខ
│   │   └── news_seed.json           # Seed ទិន្នន័យព័ត៌មាន & ព្រឹត្តិការណ៍
│   └── README.md                    # ឯកសារណែនាំ Backend API
│
├── 📁 uploads/                      # ទីតាំងផ្ទុករូបភាពដែលបាន Upload ពី Admin
├── 🐍 .py_runtime/                  # Embedded Python Runtime (សម្រាប់ Windows)
│
├── 🚀 run_server.bat                # ឯកសារចុចដំណើរការ Server លើ Windows (One-Click Run)
├── ⚡ start_server.py               # Full-Stack Server Launcher (Port 8000)
└── 📖 README.md                     # ឯកសារពន្យល់អំពីរចនាសម្ព័ន្ធគម្រោង
```

---

## 🌟 សមាសភាគសំខាន់ៗទាំង ៣ (3 Core Tiers)

### ១. Frontend Storefront (`frontend/`)
* **Creative Editorial UI:** រចនាបថប្រណិតពណ៌មាសផ្កាឈូករ័ត្ន (Golden Aura & Obsidian Black)។
* **Dual Sliders:**
  1. **Hero Top Slider:** ស្លាយស្វាគមន៍នៅផ្នែកខាងលើគេហទំព័រ។
  2. **✨ Campaign Showcase Slider (ថ្មី):** ស្លាយបង្ហាញកញ្ចប់ប្រូម៉ូសិនពិសេស ឈុតផលិតផលពេញនិយម ស្ថិតនៅចន្លោះផលិតផល និងព័ត៌មាន មានប៊ូតុងតំណភ្ជាប់ ព្រួញបញ្ជា ចុចគ្រាប់ចុច និងអូសម្រាមដៃ (Touch Swipe) លើទូរស័ព្ទ។
* **Angkor Wat Header & Animated Flag:** រូបភាពប្រាសាទអង្គរវត្តជាមួយទង់ជាតិខ្មែររស់រវើក និងផ្កាឈូករ័ត្នធ្លាក់ទាក់ទាញភ្នែក។
* **Real-time News View Counter:** ចំនួនអ្នកចូលមើលអត្ថបទកើនឡើងពិតប្រាកដ។
* **Responsive 100%:** ដំណើរការស្អាតឥតខ្ចោះលើ Desktop, Tablet និង Smart Phone។

### ២. Admin CMS Dashboard (`dashboard_admin/`)
* **URL:** `http://localhost:8000/admin.html` ឬ `http://localhost:8000/dashboard_admin/`
* **មុខងារគ្រប់គ្រងទាំងអស់ (12 Modules):**
  1. ✨ **Slider ប្រូម៉ូសិន (Showcase Slider):** Upload រូបច្រើនពីកុំព្យូទ័រ, កំណត់ចំណងជើង, Subtitle, Badge, និង Button Link។
  2. 🌟 **Hero Slider ធំ:** គ្រប់គ្រងផ្ទាំងបដាធំខាងលើ។
  3. 📦 **កាតាឡុកផលិតផល (20 Products):** កែប្រែរូបភាព, អត្ថប្រយោជន៍, និងរូបមន្តផ្សំ។
  4. 📰 **ព័ត៌មាន & ព្រឹត្តិការណ៍ (Company News):** បង្កើតអត្ថបទ, Upload រូបច្រើនសន្លឹក, វីដេអូ YouTube, និងរាប់ចំនួន View ពិតប្រាកដ។
  5. 🔔 **Popup Ads:** គ្រប់គ្រងផ្ទាំងផ្សាយពាណិជ្ជកម្មលោតឡើងស្វ័យប្រវត្តិ។
  6. 🌿 **រូបមន្តផ្សំធម្មជាតិ (Botanical Actives)**
  7. ✨ **ក្បួនថែសម្រស់ (Beauty Rituals - ពេលព្រឹក & ពេលយប់)**
  8. 🏆 **លក្ខណៈពិសេសទុកចិត្ត (Trust Features)**
  9. ℹ️ **អំពី Miss Sunflower (About Brand & Stats)**
  10. 📍 **ទីតាំងហាងសាខាប៉ោយប៉ែត & Google Maps**
  11. 📞 **ព័ត៌មានទំនាក់ទំនង & Telegram Consultant**
  12. 🔒 **សុវត្ថិភាព Admin Account:** ប្តូរ Username និង Passcode ចូលប្រព័ន្ធ។

### ៣. Backend SQLite & REST API (`backend/`)
* **Database Engine:** SQLite3 (`backend/database/cms.db`) រួមបញ្ចូល ១៨ តារាងទំនាក់ទំនង។
* **RESTful Endpoints:**
  * `GET/POST/PUT/DELETE /api/showcase-sliders`
  * `GET/POST/PUT/DELETE /api/products`
  * `GET/POST/PUT/DELETE /api/news`
  * `POST /api/news/<id>/view` (រាប់ចំនួន View ពិតប្រាកដ)
  * `GET/POST /api/settings`
  * `GET/POST /api/footer`
  * `GET/POST /api/sliders`
  * `GET/POST /api/popups`
  * `POST /api/upload` (Base64 Image Upload to `/uploads/`)
  * `POST /api/auth/login` & `/api/auth/change-credentials`

---

## 🚀 របៀបដំណើរការ Server (How to Run)

### វិធីទី ១: ចុចដំណើរការតាមរយៈ Shortcut (ងាយស្រួលបំផុត)
គ្រាន់តែចុចពីរដង (Double Click) លើឯកសារ៖
```cmd
run_server.bat
```

### វិធីទី ២: ដំណើរការតាម Terminal / PowerShell
```powershell
# ដំណើរការម៉ាស៊ីនបម្រើ Full-Stack លើ Port 8000:
.py_runtime\py.exe start_server.py

# ឬប្រសិនបើប្រើប្រព័ន្ធ Python ធម្មតា:
python start_server.py
```

បន្ទាប់មកបើកកម្មវិធីរុករក (Browser) ចូលទៅកាន់៖
* 🌐 **Public Website:** [http://localhost:8000/](http://localhost:8000/)
* ⚙️ **Admin Dashboard:** [http://localhost:8000/admin.html](http://localhost:8000/admin.html)
* 📡 **REST API Test:** [http://localhost:8000/api/settings](http://localhost:8000/api/settings)

---

## 🔒 សុវត្ថិភាព និងការបម្រុងទុក (Security & Backups)
* ទិន្នន័យទាំងអស់ត្រូវបានរក្សាទុកក្នុង SQLite Database `backend/database/cms.db` ដោយស្វ័យប្រវត្តិ។
* រូបភាពដែលបាន upload ត្រូវបានរក្សាទុកក្នុង Folder `uploads/`។
* Passcode របស់អ្នកគ្រប់គ្រងត្រូវបានការពារយ៉ាងរឹងមាំជាមួយ SHA-256 Hashing។

---
© 2026 MISS SUNFLOWER CAMBODIA OFFICIAL. រក្សាសិទ្ធិគ្រប់យ៉ាង។
#   m i s s s u n f l o w e r  
 #   m i s s s u n f l o w e r  
 #   m i s s s u n f l o w e r  
 # misssunflower
#   m i s s s u n f l o w e r  
 