"""
Miss Sunflower FastAPI High-Performance Server
Powered by FastAPI, Uvicorn & SQLite backend.
Auto-generates interactive API docs at http://localhost:8000/docs
"""
import os
import sys
import time
import base64
import hashlib
from typing import Optional, List, Any, Dict
from pathlib import Path

from fastapi import FastAPI, Request, Response, UploadFile, File, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure UTF-8 output on Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure root and backend in sys.path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
ADMIN_DIR = ROOT_DIR / "admin"
UPLOADS_DIR = ROOT_DIR / "uploads"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(1, str(BACKEND_DIR))

try:
    import backend.cms_db as cms_db
except Exception:
    import cms_db

# Create uploads directory if missing
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# FastAPI App Initialization
# -------------------------------------------------------------
app = FastAPI(
    title="Miss Sunflower CMS & Store API",
    description="High-performance backend API for Miss Sunflower e-commerce, customer reviews, and admin CMS.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local dev and storefront
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()
    if path.endswith((".js", ".css", ".html")) or path.startswith("/api/") or path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# -------------------------------------------------------------
# 1. API: Settings & Info
# -------------------------------------------------------------
@app.get("/api/settings", tags=["Settings"], summary="Get store general settings")
async def get_settings():
    return cms_db.get_settings()

@app.post("/api/settings", tags=["Settings"], summary="Update store general settings")
async def update_settings(req: Request):
    data = await req.json()
    updated = cms_db.update_settings(data)
    return {"success": True, "settings": updated}

@app.get("/api/footer", tags=["Settings"], summary="Get footer settings")
async def get_footer():
    return cms_db.get_footer_settings()

@app.post("/api/footer", tags=["Settings"], summary="Update footer settings")
async def update_footer(req: Request):
    data = await req.json()
    updated = cms_db.update_footer_settings(data)
    return {"success": True, "footer": updated}

# -------------------------------------------------------------
# 2. API: Authentication & Users
# -------------------------------------------------------------
@app.post("/api/auth/login", tags=["Admin Auth"], summary="Admin login")
async def admin_login(req: Request):
    data = await req.json()
    username = data.get("username", "").strip()
    passcode = data.get("passcode") or data.get("password", "")
    user = cms_db.verify_admin_credentials(username, passcode)
    if user:
        token = hashlib.sha256(f"{username}:misssunflower_session:{time.time()}".encode()).hexdigest()
        return {
            "success": True,
            "token": token,
            "user": user,
            "message": "ចូលប្រព័ន្ធបានជោគជ័យ (Login successful)"
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ឈ្មោះអ្នកប្រើប្រាស់ ឬ Passcode មិនត្រឹមត្រូវទេ (Invalid credentials)"
    )

@app.get("/api/auth/me", tags=["Admin Auth"], summary="Get current admin user profile")
@app.get("/api/admin/user", tags=["Admin Auth"])
@app.get("/api/admin/profile", tags=["Admin Auth"])
async def get_admin_user():
    user = cms_db.get_admin_user()
    if user:
        return {"success": True, "user": user}
    raise HTTPException(status_code=404, detail="No admin user found")

@app.post("/api/admin/change-credentials", tags=["Admin Auth"], summary="Change admin credentials")
@app.post("/api/auth/change-credentials", tags=["Admin Auth"])
@app.post("/api/admin/settings/account", tags=["Admin Auth"])
async def change_admin_credentials(req: Request):
    data = await req.json()
    current_user = data.get("current_username") or "hena"
    new_user = data.get("new_username")
    new_pass = data.get("new_passcode") or data.get("new_password")
    current_pass = data.get("current_passcode") or data.get("current_password")
    res = cms_db.update_admin_credentials(
        current_username=current_user,
        new_username=new_user,
        new_passcode=new_pass,
        current_passcode=current_pass
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to update"))
    return res

@app.post("/api/user/register", tags=["User Accounts"], summary="Customer register")
async def user_register(req: Request):
    data = await req.json()
    try:
        user = cms_db.register_user(data)
        return {"success": True, "user": user, "message": "ចុះឈ្មោះជោគជ័យ!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/user/login", tags=["User Accounts"], summary="Customer login")
async def user_login(req: Request):
    data = await req.json()
    email = data.get("email")
    password = data.get("password")
    user = cms_db.login_user(email, password)
    if user:
        return {"success": True, "user": user, "message": "ចូលប្រព័ន្ធជោគជ័យ!"}
    raise HTTPException(status_code=401, detail="អ៊ីមែល Gmail ឬ Password មិនត្រឹមត្រូវទេ!")

@app.post("/api/user/google-auth", tags=["User Accounts"], summary="Customer Google/One-tap Auth")
async def user_google_auth(req: Request):
    data = await req.json()
    try:
        user = cms_db.google_auth_user(data)
        return {"success": True, "user": user, "message": "ចូលប្រើជាមួយ Gmail ជោគជ័យ!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/user/profile", tags=["User Accounts"], summary="Get customer profile by ID or email")
async def get_user_profile(id: Optional[int] = None, email: Optional[str] = None):
    u = None
    if id:
        u = cms_db.get_user_by_id(id)
    elif email:
        u = cms_db.get_user_by_email(email)
    if u:
        return {"success": True, "user": u}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/user/profile", tags=["User Accounts"], summary="Update customer profile & bio")
async def update_user_profile(req: Request):
    data = await req.json()
    user_id = data.get("id") or data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID required")
    try:
        updated = cms_db.update_user_profile(int(user_id), data)
        return {"success": True, "user": updated, "message": "បានកែប្រែព័ត៌មានផ្ទាល់ខ្លួនជោគជ័យ!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/user/my-reviews", tags=["User Accounts"], summary="Get reviews posted by a specific user")
async def get_my_reviews(user_id: Optional[int] = None, email: Optional[str] = None, user_email: Optional[str] = None):
    mail = email or user_email
    return cms_db.get_user_reviews(user_id=user_id, user_email=mail)

@app.get("/api/admin/users", tags=["Admin Users"], summary="List all registered customers")
async def get_all_users():
    return cms_db.get_all_users()

# -------------------------------------------------------------
# 3. API: Products
# -------------------------------------------------------------
@app.get("/api/products", tags=["Products"], summary="List products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    return cms_db.get_products(category=category, search=search)

@app.get("/api/products/{prod_id}", tags=["Products"], summary="Get single product")
async def get_product(prod_id: int):
    p = cms_db.get_product(prod_id)
    if p:
        return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/products", tags=["Products"], summary="Create new product")
async def create_product(req: Request):
    data = await req.json()
    new_product = cms_db.create_product(data)
    return {"success": True, "product": new_product}

@app.put("/api/products/{prod_id}", tags=["Products"], summary="Update product")
@app.post("/api/products/{prod_id}/update", tags=["Products"])
async def update_product(prod_id: int, req: Request):
    data = await req.json()
    try:
        updated = cms_db.update_product(prod_id, data)
        return {"success": True, "product": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/products/{prod_id}", tags=["Products"], summary="Delete product")
@app.post("/api/products/{prod_id}/delete", tags=["Products"])
async def delete_product(prod_id: int):
    try:
        cms_db.delete_product(prod_id)
        return {"success": True, "deletedId": prod_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------------------------------------
# 4. API: Customer Reviews
# -------------------------------------------------------------
@app.get("/api/reviews/summary", tags=["Reviews"], summary="Get review statistics and score breakdown")
async def get_reviews_summary():
    return cms_db.get_reviews_summary()

@app.get("/api/reviews", tags=["Reviews"], summary="List customer reviews")
@app.get("/api/customer-reviews", tags=["Reviews"])
async def get_reviews(approved_only: bool = True, featured_only: bool = False):
    return cms_db.get_reviews(approved_only=approved_only, featured_only=featured_only)

@app.get("/api/admin/reviews", tags=["Reviews"], summary="Admin list all reviews")
@app.get("/api/admin/customer-reviews", tags=["Reviews"])
async def get_admin_reviews():
    return cms_db.get_reviews(approved_only=False)

@app.post("/api/reviews", tags=["Reviews"], summary="Create review")
@app.post("/api/customer-reviews", tags=["Reviews"])
async def create_review(req: Request):
    data = await req.json()
    try:
        new_rev = cms_db.create_review(data)
        return {"success": True, "id": new_rev.get("id"), "review": new_rev}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/reviews/{rev_id}", tags=["Reviews"], summary="Update review")
@app.put("/api/customer-reviews/{rev_id}", tags=["Reviews"])
@app.post("/api/reviews/{rev_id}/update", tags=["Reviews"])
@app.post("/api/customer-reviews/{rev_id}/update", tags=["Reviews"])
async def update_review(rev_id: int, req: Request):
    data = await req.json()
    try:
        updated = cms_db.update_review(rev_id, data)
        return {"success": True, "review": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/reviews/{rev_id}/approve", tags=["Reviews"], summary="Approve review")
@app.post("/api/customer-reviews/{rev_id}/approve", tags=["Reviews"])
async def approve_review(rev_id: int, req: Request):
    data = await req.json()
    is_approved = int(data.get("is_approved", 1))
    try:
        updated = cms_db.approve_review(rev_id, is_approved)
        return {"success": True, "review": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/reviews/{rev_id}/pin", tags=["Reviews"], summary="Pin/Feature review")
@app.post("/api/customer-reviews/{rev_id}/pin", tags=["Reviews"])
async def pin_review(rev_id: int, req: Request):
    data = await req.json()
    is_featured = data.get("is_featured")
    try:
        updated = cms_db.pin_review(rev_id, is_featured=is_featured)
        return {"success": True, "review": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/reviews/{rev_id}", tags=["Reviews"], summary="Delete review")
@app.delete("/api/customer-reviews/{rev_id}", tags=["Reviews"])
@app.post("/api/reviews/{rev_id}/delete", tags=["Reviews"])
@app.post("/api/customer-reviews/{rev_id}/delete", tags=["Reviews"])
async def delete_review(rev_id: int):
    try:
        cms_db.delete_review(rev_id)
        return {"success": True, "deletedId": rev_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------------------------------------
# 5. API: News & Posts
# -------------------------------------------------------------
@app.get("/api/news", tags=["News"], summary="List news or get by id query")
@app.get("/api/posts", tags=["News"])
async def get_news(
    id: Optional[int] = None,
    category: Optional[str] = None,
    published_only: bool = False,
    search: Optional[str] = None
):
    if id:
        item = cms_db.get_news_by_id(id, increment_views=False)
        if item:
            return item
        raise HTTPException(status_code=404, detail="News article not found")
    return cms_db.get_all_news(category=category, published_only=published_only, search=search)

@app.get("/api/news/{news_id}", tags=["News"], summary="Get single news article")
@app.get("/api/posts/{news_id}", tags=["News"])
async def get_news_by_id(news_id: int):
    item = cms_db.get_news_by_id(news_id, increment_views=False)
    if item:
        return item
    raise HTTPException(status_code=404, detail="News article not found")

@app.post("/api/news", tags=["News"], summary="Create news post")
@app.post("/api/posts", tags=["News"])
async def create_news(req: Request):
    data = await req.json()
    try:
        created = cms_db.create_news(data)
        return {"success": True, "news": created}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/news/{news_id}", tags=["News"], summary="Update news post")
@app.put("/api/posts/{news_id}", tags=["News"])
@app.post("/api/news/{news_id}/update", tags=["News"])
@app.post("/api/posts/{news_id}/update", tags=["News"])
async def update_news(news_id: int, req: Request):
    data = await req.json()
    try:
        updated = cms_db.update_news(news_id, data)
        return {"success": True, "news": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/news/{news_id}", tags=["News"], summary="Delete news post")
@app.delete("/api/posts/{news_id}", tags=["News"])
@app.post("/api/news/{news_id}/delete", tags=["News"])
@app.post("/api/posts/{news_id}/delete", tags=["News"])
async def delete_news(news_id: int):
    try:
        cms_db.delete_news(news_id)
        return {"success": True, "deletedId": news_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/news/{news_id}/view", tags=["News"], summary="Increment view count")
@app.post("/api/posts/{news_id}/view", tags=["News"])
async def increment_news_view(news_id: int):
    try:
        new_views = cms_db.increment_news_views(news_id)
        return {"success": True, "views_count": new_views}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------------------------------------
# 6. API: Showcase & Sliders
# -------------------------------------------------------------
@app.get("/api/sliders", tags=["Sliders"], summary="Get banner sliders")
async def get_sliders():
    return cms_db.get_sliders()

@app.post("/api/sliders", tags=["Sliders"], summary="Create banner slider")
async def create_slider(req: Request):
    data = await req.json()
    new_id = cms_db.create_slider(data)
    return {"success": True, "id": new_id}

@app.put("/api/sliders/{slider_id}", tags=["Sliders"], summary="Update slider")
@app.post("/api/sliders/{slider_id}/update", tags=["Sliders"])
async def update_slider(slider_id: int, req: Request):
    data = await req.json()
    try:
        updated = cms_db.update_slider(slider_id, data)
        return {"success": True, "slider": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/sliders/{slider_id}", tags=["Sliders"], summary="Delete slider")
@app.post("/api/sliders/{slider_id}/delete", tags=["Sliders"])
async def delete_slider(slider_id: int):
    try:
        cms_db.delete_slider(slider_id)
        return {"success": True, "deletedId": slider_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/showcase", tags=["Showcase"], summary="Get showcase sliders")
@app.get("/api/showcase-sliders", tags=["Showcase"])
async def get_showcase_sliders(active_only: bool = False):
    return cms_db.get_showcase_sliders(active_only=active_only)

@app.post("/api/showcase", tags=["Showcase"], summary="Create showcase slider")
@app.post("/api/showcase-sliders", tags=["Showcase"])
async def create_showcase(req: Request):
    data = await req.json()
    created = cms_db.create_showcase_slider(data)
    return {"success": True, "slider": created}

@app.put("/api/showcase/{slide_id}", tags=["Showcase"], summary="Update showcase slider")
@app.put("/api/showcase-sliders/{slide_id}", tags=["Showcase"])
@app.post("/api/showcase/{slide_id}/update", tags=["Showcase"])
@app.post("/api/showcase-sliders/{slide_id}/update", tags=["Showcase"])
async def update_showcase(slide_id: int, req: Request):
    data = await req.json()
    try:
        updated = cms_db.update_showcase_slider(slide_id, data)
        return {"success": True, "slider": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/showcase/{slide_id}", tags=["Showcase"], summary="Delete showcase slider")
@app.delete("/api/showcase-sliders/{slide_id}", tags=["Showcase"])
@app.post("/api/showcase/{slide_id}/delete", tags=["Showcase"])
@app.post("/api/showcase-sliders/{slide_id}/delete", tags=["Showcase"])
async def delete_showcase(slide_id: int):
    try:
        cms_db.delete_showcase_slider(slide_id)
        return {"success": True, "deletedId": slide_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------------------------------------
# 7. API: Promotions, Menus, Popups, Trust, Botanical, Rituals, About, Contact
# -------------------------------------------------------------
@app.get("/api/promotions", tags=["Promotions"])
async def get_promotions():
    return cms_db.get_promotions()

@app.post("/api/promotions", tags=["Promotions"])
async def update_promotions(req: Request):
    data = await req.json()
    promo_id = data.get("id", 1)
    cms_db.update_promotion(promo_id, data)
    return {"success": True, "promotions": cms_db.get_promotions()}

@app.get("/api/menus", tags=["Menus"])
async def get_menus():
    return cms_db.get_menus()

@app.post("/api/menus", tags=["Menus"])
async def create_menu(req: Request):
    data = await req.json()
    new_id = cms_db.create_menu(data)
    return {"success": True, "id": new_id}

@app.delete("/api/menus/{menu_id}", tags=["Menus"])
async def delete_menu(menu_id: int):
    cms_db.delete_menu(menu_id)
    return {"success": True, "deletedId": menu_id}

@app.get("/api/popups", tags=["Popups"])
async def get_popups():
    return cms_db.get_popups()

@app.post("/api/popups", tags=["Popups"])
async def update_popup(req: Request):
    data = await req.json()
    popup_id = data.get("id", 1)
    cms_db.update_popup(popup_id, data)
    return {"success": True, "popups": cms_db.get_popups()}

@app.get("/api/features", tags=["Features"])
async def get_features():
    return cms_db.get_trust_features()

@app.post("/api/features", tags=["Features"])
async def post_features(req: Request):
    data = await req.json()
    if isinstance(data, list):
        for item in data:
            if "id" in item:
                cms_db.update_trust_feature(item["id"], item)
        return {"success": True, "features": cms_db.get_trust_features()}
    elif "id" in data:
        updated = cms_db.update_trust_feature(data["id"], data)
        return {"success": True, "feature": updated}
    else:
        new_item = cms_db.create_trust_feature(data)
        return {"success": True, "feature": new_item}

@app.delete("/api/features/{feat_id}", tags=["Features"])
@app.post("/api/features/{feat_id}/delete", tags=["Features"])
async def delete_feature(feat_id: int):
    cms_db.delete_trust_feature(feat_id)
    return {"success": True, "deletedId": feat_id}

@app.get("/api/ingredients/header", tags=["Ingredients"])
async def get_ingredients_header():
    return cms_db.get_botanical_header()

@app.post("/api/ingredients/header", tags=["Ingredients"])
async def update_ingredients_header(req: Request):
    data = await req.json()
    updated = cms_db.update_botanical_header(data)
    return {"success": True, "header": updated}

@app.get("/api/ingredients", tags=["Ingredients"])
async def get_ingredients():
    return cms_db.get_botanical_ingredients()

@app.post("/api/ingredients", tags=["Ingredients"])
async def create_ingredient(req: Request):
    data = await req.json()
    new_item = cms_db.create_botanical_ingredient(data)
    return {"success": True, "ingredient": new_item}

@app.put("/api/ingredients/{ing_id}", tags=["Ingredients"])
@app.post("/api/ingredients/{ing_id}/update", tags=["Ingredients"])
async def update_ingredient(ing_id: int, req: Request):
    data = await req.json()
    updated = cms_db.update_botanical_ingredient(ing_id, data)
    return {"success": True, "ingredient": updated}

@app.delete("/api/ingredients/{ing_id}", tags=["Ingredients"])
@app.post("/api/ingredients/{ing_id}/delete", tags=["Ingredients"])
async def delete_ingredient(ing_id: int):
    cms_db.delete_botanical_ingredient(ing_id)
    return {"success": True, "deletedId": ing_id}

@app.get("/api/rituals", tags=["Rituals"])
async def get_rituals(routine_type: Optional[str] = None):
    return cms_db.get_beauty_rituals(routine_type)

@app.post("/api/rituals", tags=["Rituals"])
async def create_ritual(req: Request):
    data = await req.json()
    new_item = cms_db.create_beauty_ritual(data)
    return {"success": True, "ritual": new_item}

@app.put("/api/rituals/{rit_id}", tags=["Rituals"])
@app.post("/api/rituals/{rit_id}/update", tags=["Rituals"])
async def update_ritual(rit_id: int, req: Request):
    data = await req.json()
    updated = cms_db.update_beauty_ritual(rit_id, data)
    return {"success": True, "ritual": updated}

@app.delete("/api/rituals/{rit_id}", tags=["Rituals"])
@app.post("/api/rituals/{rit_id}/delete", tags=["Rituals"])
async def delete_ritual(rit_id: int):
    cms_db.delete_beauty_ritual(rit_id)
    return {"success": True, "deletedId": rit_id}

@app.get("/api/about", tags=["About"])
async def get_about():
    return cms_db.get_about()

@app.post("/api/about", tags=["About"])
async def update_about(req: Request):
    data = await req.json()
    updated = cms_db.update_about(data)
    return {"success": True, "about": updated}

@app.get("/api/location", tags=["Location"])
async def get_location():
    return cms_db.get_location()

@app.post("/api/location", tags=["Location"])
async def update_location(req: Request):
    data = await req.json()
    updated = cms_db.update_location(data)
    return {"success": True, "location": updated}

@app.get("/api/contact", tags=["Contact"])
async def get_contact():
    return cms_db.get_contact_social()

@app.post("/api/contact", tags=["Contact"])
async def update_contact(req: Request):
    data = await req.json()
    updated = cms_db.update_contact_social(data)
    return {"success": True, "contact": updated}

@app.get("/api/messages", tags=["Messages"])
async def get_messages():
    return cms_db.get_contact_messages()

@app.post("/api/messages", tags=["Messages"])
async def create_message(req: Request):
    data = await req.json()
    res = cms_db.create_contact_message(data)
    return res

@app.delete("/api/messages/{msg_id}", tags=["Messages"])
@app.post("/api/messages/{msg_id}/delete", tags=["Messages"])
async def delete_message(msg_id: int):
    cms_db.delete_contact_message(msg_id)
    return {"success": True, "deletedId": msg_id}

# -------------------------------------------------------------
# 8. API: Uploads (Multipart & Base64 JSON support)
# -------------------------------------------------------------
@app.post("/api/upload", tags=["Uploads"], summary="Upload image (multipart or base64)")
async def upload_file(req: Request):
    try:
        content_type = req.headers.get("content-type", "")
        img_bytes = None
        orig_filename = "upload.jpg"

        if "multipart/form-data" in content_type:
            form = await req.form()
            file = form.get("file") or form.get("image")
            if file and hasattr(file, "read"):
                img_bytes = await file.read()
                orig_filename = getattr(file, "filename", "upload.jpg")
        else:
            try:
                data = await req.json()
                orig_filename = data.get("filename", "upload.jpg")
                base64_data = data.get("data", "")
                if "," in base64_data:
                    base64_data = base64_data.split(",", 1)[1]
                if base64_data:
                    img_bytes = base64.b64decode(base64_data)
            except Exception:
                pass

        if not img_bytes:
            raise HTTPException(status_code=400, detail="No image data received (គ្មានទិន្នន័យរូបភាព)")

        ext = Path(orig_filename).suffix.lower()
        if not ext:
            ext = ".jpg"

        new_filename = f"prod_{int(time.time()*1000)}{ext}"
        dest_path = UPLOADS_DIR / new_filename

        with open(dest_path, "wb") as f:
            f.write(img_bytes)

        rel_url = f"uploads/{new_filename}"
        return {
            "success": True,
            "url": rel_url,
            "filename": new_filename,
            "size": len(img_bytes)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload error: {str(e)}")

# -------------------------------------------------------------
# 9. HTML Page Serving & Friendly URLs
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["Pages"])
@app.get("/index.html", response_class=HTMLResponse, tags=["Pages"])
async def serve_home():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/user-dashboard", response_class=HTMLResponse, tags=["Pages"])
@app.get("/user-dashboard.html", response_class=HTMLResponse, tags=["Pages"])
@app.get("/dashboard_user", response_class=HTMLResponse, tags=["Pages"])
@app.get("/dashboard_user.html", response_class=HTMLResponse, tags=["Pages"])
@app.get("/user", response_class=HTMLResponse, tags=["Pages"])
@app.get("/user.html", response_class=HTMLResponse, tags=["Pages"])
async def serve_user_dashboard():
    return FileResponse(FRONTEND_DIR / "user-dashboard.html")

@app.get("/news-detail", response_class=HTMLResponse, tags=["Pages"])
@app.get("/news-detail.html", response_class=HTMLResponse, tags=["Pages"])
async def serve_news_detail():
    return FileResponse(FRONTEND_DIR / "news-detail.html")

@app.get("/service-worker.js", tags=["Pages"])
async def serve_service_worker():
    return FileResponse(FRONTEND_DIR / "service-worker.js", media_type="application/javascript")

@app.get("/admin", response_class=HTMLResponse, tags=["Pages"])
@app.get("/admin.html", response_class=HTMLResponse, tags=["Pages"])
@app.get("/dashboard_admin", response_class=HTMLResponse, tags=["Pages"])
@app.get("/dashboard_admin/index.html", response_class=HTMLResponse, tags=["Pages"])
@app.get("/admin/index.html", response_class=HTMLResponse, tags=["Pages"])
async def serve_admin_dashboard():
    return FileResponse(ADMIN_DIR / "index.html")

# -------------------------------------------------------------
# 10. Static Mounts for Frontend Assets, Admin, and Uploads
# -------------------------------------------------------------
# Static directory mounts
app.mount("/admin", StaticFiles(directory=str(ADMIN_DIR), html=True), name="admin")
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

if (FRONTEND_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
if (FRONTEND_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
if (FRONTEND_DIR / "images").exists():
    app.mount("/images", StaticFiles(directory=str(FRONTEND_DIR / "images")), name="images")
if (FRONTEND_DIR / "miss sun prodcut").exists():
    app.mount("/miss sun prodcut", StaticFiles(directory=str(FRONTEND_DIR / "miss sun prodcut")), name="miss_sun_prodcut")
    app.mount("/admin/miss sun prodcut", StaticFiles(directory=str(FRONTEND_DIR / "miss sun prodcut")), name="admin_miss_sun_prodcut")

# Catch-all frontend static fallback
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend_root")

# -------------------------------------------------------------
# Server Entrypoint
# -------------------------------------------------------------
def run(port: int = 8000, host: str = "0.0.0.0"):
    print("=" * 72, flush=True)
    print("[FASTAPI] MISS SUNFLOWER ENTERPRISE SERVER", flush=True)
    print(f"[*] Public Website:         http://localhost:{port}/", flush=True)
    print(f"[*] User Dashboard:         http://localhost:{port}/user-dashboard", flush=True)
    print(f"[*] Admin CMS:              http://localhost:{port}/admin", flush=True)
    print(f"[*] Interactive API Docs:   http://localhost:{port}/docs", flush=True)
    print(f"[*] ReDoc Documentation:    http://localhost:{port}/redoc", flush=True)
    print(f"[*] SQLite Database:        {cms_db.DB_PATH}", flush=True)
    print("=" * 72, flush=True)
    uvicorn.run("fastapi_server:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    port_to_run = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_to_run = int(sys.argv[1])
    run(port=port_to_run)
