"""
Miss Sunflower Full-Stack Localhost Server
Serves:
1. Public Website (Storefront)
2. Dashboard Admin CMS
3. RESTful API connected directly to SQLite (cms.db)
"""
import http.server
import socketserver
import os
import sys
import json
import urllib.parse
# Ensure root and backend directories are in python search path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_PATH = os.path.join(ROOT_DIR, 'backend')
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_PATH not in sys.path:
    sys.path.insert(1, BACKEND_PATH)

try:
    import backend.cms_db as cms_db
except Exception:
    import cms_db

# Ensure UTF-8 output on Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class FullStackHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # ----------------- Helper Methods -----------------
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def read_post_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length <= 0:
            return {}, None
        raw_bytes = self.rfile.read(content_length)
        content_type = self.headers.get('Content-Type', '')

        # Check if multipart/form-data
        if 'multipart/form-data' in content_type:
            try:
                import email
                msg_bytes = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode('latin-1') + raw_bytes
                msg = email.message_from_bytes(msg_bytes)
                form_fields = {}
                file_info = None
                for part in msg.walk():
                    disp = part.get_params(header='content-disposition')
                    if not disp:
                        continue
                    filename = part.get_filename()
                    if filename:
                        file_info = {
                            'filename': filename,
                            'content': part.get_payload(decode=True)
                        }
                    else:
                        disp_dict = dict(disp)
                        name = disp_dict.get('name')
                        if name:
                            payload = part.get_payload(decode=True)
                            if payload:
                                form_fields[name] = payload.decode('utf-8', errors='ignore')
                return form_fields, file_info
            except Exception:
                pass

        try:
            raw_str = raw_bytes.decode('utf-8')
            return json.loads(raw_str), None
        except Exception:
            return {}, None

    def read_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode('utf-8')
            try:
                return json.loads(raw_body)
            except Exception:
                return {}
        return {}

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def translate_path(self, path):
        # Strip query parameters and URL unquote
        parsed = urllib.parse.urlparse(path)
        clean_path = urllib.parse.unquote(parsed.path)
        clean_path_no_slash = clean_path.rstrip('/')

        # 1. Frontend Web Pages
        if clean_path_no_slash in ('', '/index.html'):
            return os.path.join(DIRECTORY, 'frontend', 'index.html')
        if clean_path_no_slash in ('/news-detail', '/news-detail.html'):
            return os.path.join(DIRECTORY, 'frontend', 'news-detail.html')
        if clean_path_no_slash in ('/user-dashboard', '/user-dashboard.html', '/dashboard_user', '/dashboard_user.html', '/user', '/user.html'):
            return os.path.join(DIRECTORY, 'frontend', 'user-dashboard.html')
        if clean_path_no_slash == '/service-worker.js':
            return os.path.join(DIRECTORY, 'frontend', 'service-worker.js')

        # 2. Admin Dashboard CMS Pages
        if clean_path_no_slash in ('/admin', '/admin.html', '/dashboard_admin', '/dashboard_admin/index.html', '/admin/index.html'):
            return os.path.join(DIRECTORY, 'admin', 'index.html')

        # 3. Requests with /admin/ or /dashboard_admin/ prefix
        for admin_prefix in ('/admin/', '/dashboard_admin/'):
            if clean_path.startswith(admin_prefix):
                sub = clean_path[len(admin_prefix):]
                admin_cand = os.path.join(DIRECTORY, 'admin', sub.replace('/', os.sep))
                if os.path.exists(admin_cand) and not os.path.isdir(admin_cand):
                    return admin_cand
                frontend_cand = os.path.join(DIRECTORY, 'frontend', sub.replace('/', os.sep))
                if os.path.exists(frontend_cand):
                    return frontend_cand

        # 4. Static Frontend Assets (css, js, images, miss sun prodcut)
        for asset_prefix in ('/css/', '/js/', '/images/', '/miss sun prodcut/'):
            if clean_path.startswith(asset_prefix):
                sub = clean_path.lstrip('/')
                frontend_asset = os.path.join(DIRECTORY, 'frontend', sub.replace('/', os.sep))
                if os.path.exists(frontend_asset):
                    return frontend_asset

        # 5. Dynamic Uploads
        if clean_path.startswith('/uploads/'):
            sub = clean_path.lstrip('/')
            return os.path.join(DIRECTORY, sub.replace('/', os.sep))

        # 6. Fallback to frontend or root
        cand_frontend = os.path.join(DIRECTORY, 'frontend', clean_path.lstrip('/').replace('/', os.sep))
        if os.path.exists(cand_frontend):
            return cand_frontend

        return super().translate_path(path)

    # ----------------- GET Request Handling -----------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # ========== REST API Routes ==========
        if path == '/api/settings':
            return self.send_json(cms_db.get_settings())

        elif path == '/api/footer':
            return self.send_json(cms_db.get_footer_settings())

        elif path in ('/api/auth/me', '/api/admin/user', '/api/admin/profile'):
            user = cms_db.get_admin_user()
            if user:
                return self.send_json({'success': True, 'user': user})
            return self.send_json({'success': False, 'error': 'No admin user found'}, status=404)

        elif path == '/api/promotions':
            return self.send_json(cms_db.get_promotions())

        elif path == '/api/menus':
            return self.send_json(cms_db.get_menus())

        elif path == '/api/sliders':
            return self.send_json(cms_db.get_sliders())

        elif path in ('/api/showcase-sliders', '/api/showcase'):
            active_only = query.get('active_only', ['0'])[0] in ('1', 'true', 'yes')
            return self.send_json(cms_db.get_showcase_sliders(active_only=active_only))

        elif path == '/api/reviews/summary':
            return self.send_json(cms_db.get_reviews_summary())

        elif path in ('/api/reviews', '/api/customer-reviews'):
            approved_only = query.get('approved_only', ['1'])[0] in ('1', 'true', 'yes')
            featured_only = query.get('featured_only', ['0'])[0] in ('1', 'true', 'yes')
            return self.send_json(cms_db.get_reviews(approved_only=approved_only, featured_only=featured_only))

        elif path in ('/api/admin/reviews', '/api/admin/customer-reviews'):
            return self.send_json(cms_db.get_reviews(approved_only=False))

        elif path == '/api/user/profile':
            user_id = query.get('id', [None])[0]
            email = query.get('email', [None])[0]
            u = None
            if user_id:
                u = cms_db.get_user_by_id(int(user_id))
            elif email:
                u = cms_db.get_user_by_email(email)
            if u:
                return self.send_json({'success': True, 'user': u})
            return self.send_json({'error': 'User not found'}, status=404)

        elif path == '/api/user/my-reviews':
            user_id = query.get('user_id', [None])[0]
            email = query.get('email', [None])[0] or query.get('user_email', [None])[0]
            reviews = cms_db.get_user_reviews(user_id=int(user_id) if user_id else None, user_email=email)
            return self.send_json(reviews)

        elif path == '/api/admin/users':
            return self.send_json(cms_db.get_all_users())

        elif path == '/api/popups':
            return self.send_json(cms_db.get_popups())

        elif path == '/api/features':
            return self.send_json(cms_db.get_trust_features())

        elif path == '/api/ingredients':
            return self.send_json(cms_db.get_botanical_ingredients())

        elif path == '/api/rituals':
            routine_type = query.get('routine_type', [None])[0]
            return self.send_json(cms_db.get_beauty_rituals(routine_type))

        elif path == '/api/about':
            return self.send_json(cms_db.get_about())

        elif path == '/api/location':
            return self.send_json(cms_db.get_location())

        elif path == '/api/contact':
            return self.send_json(cms_db.get_contact_social())

        elif path == '/api/messages':
            return self.send_json(cms_db.get_contact_messages())

        elif path == '/api/products':
            category = query.get('category', [None])[0]
            search = query.get('search', [None])[0]
            products = cms_db.get_products(category=category, search=search)
            return self.send_json(products)

        elif path.startswith('/api/products/'):
            try:
                prod_id = int(path.split('/')[-1])
                product = cms_db.get_product(prod_id)
                if product:
                    return self.send_json(product)
                return self.send_json({'error': 'Product not found'}, status=404)
            except ValueError:
                return self.send_json({'error': 'Invalid product ID'}, status=400)

        elif path in ('/api/news', '/api/posts'):
            news_id = query.get('id', [None])[0]
            if news_id:
                try:
                    item = cms_db.get_news_by_id(int(news_id), increment_views=False)
                    if item:
                        return self.send_json(item)
                    return self.send_json({'error': 'News article not found'}, status=404)
                except ValueError:
                    return self.send_json({'error': 'Invalid news ID'}, status=400)
            category = query.get('category', [None])[0]
            published_only = query.get('published_only', ['0'])[0] in ('1', 'true', 'yes')
            search = query.get('search', [None])[0]
            return self.send_json(cms_db.get_all_news(category=category, published_only=published_only, search=search))

        elif path.startswith('/api/news/') or path.startswith('/api/posts/'):
            try:
                parts = [p for p in path.split('/') if p]
                news_id = int(parts[-1])
                item = cms_db.get_news_by_id(news_id, increment_views=False)
                if item:
                    return self.send_json(item)
                return self.send_json({'error': 'News article not found'}, status=404)
            except ValueError:
                return self.send_json({'error': 'Invalid news ID'}, status=400)

        # ========== Static Files Handled by translate_path ==========
        return super().do_GET()

    # ----------------- POST Request Handling -----------------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        data, file_info = self.read_post_body()

        if path == '/api/auth/login':
            username = data.get('username', '').strip()
            passcode = data.get('passcode') or data.get('password', '')
            user = cms_db.verify_admin_credentials(username, passcode)
            if user:
                import time, hashlib
                token = hashlib.sha256(f"{username}:misssunflower_session:{time.time()}".encode()).hexdigest()
                return self.send_json({
                    'success': True,
                    'token': token,
                    'user': user,
                    'message': 'ចូលប្រព័ន្ធបានជោគជ័យ (Login successful)'
                })
            else:
                return self.send_json({
                    'success': False,
                    'error': 'ឈ្មោះអ្នកប្រើប្រាស់ ឬ Passcode មិនត្រឹមត្រូវទេ (Invalid username or passcode)'
                }, status=401)

        elif path == '/api/user/register':
            try:
                user = cms_db.register_user(data)
                return self.send_json({'success': True, 'user': user, 'message': 'ចុះឈ្មោះជោគជ័យ!'}, status=201)
            except Exception as e:
                return self.send_json({'success': False, 'error': str(e)}, status=400)

        elif path == '/api/user/login':
            email = data.get('email')
            password = data.get('password')
            user = cms_db.login_user(email, password)
            if user:
                return self.send_json({'success': True, 'user': user, 'message': 'ចូលប្រព័ន្ធជោគជ័យ!'})
            return self.send_json({'success': False, 'error': 'អ៊ីមែល Gmail ឬ Password មិនត្រឹមត្រូវទេ!'}, status=401)

        elif path == '/api/user/google-auth':
            try:
                user = cms_db.google_auth_user(data)
                return self.send_json({'success': True, 'user': user, 'message': 'ចូលប្រើជាមួយ Gmail ជោគជ័យ!'})
            except Exception as e:
                return self.send_json({'success': False, 'error': str(e)}, status=400)

        elif path == '/api/user/profile':
            user_id = data.get('id') or data.get('user_id')
            if not user_id:
                return self.send_json({'error': 'User ID required'}, status=400)
            try:
                updated = cms_db.update_user_profile(int(user_id), data)
                return self.send_json({'success': True, 'user': updated, 'message': 'បានកែប្រែព័ត៌មានផ្ទាល់ខ្លួនជោគជ័យ!'})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path in ('/api/admin/change-credentials', '/api/auth/change-credentials', '/api/admin/settings/account'):
            current_user = data.get('current_username') or 'hena'
            new_user = data.get('new_username')
            new_pass = data.get('new_passcode') or data.get('new_password')
            current_pass = data.get('current_passcode') or data.get('current_password')
            
            res = cms_db.update_admin_credentials(
                current_username=current_user,
                new_username=new_user,
                new_passcode=new_pass,
                current_passcode=current_pass
            )
            status_code = 200 if res.get('success') else 400
            return self.send_json(res, status=status_code)

        elif path == '/api/settings':
            updated = cms_db.update_settings(data)
            return self.send_json({'success': True, 'settings': updated})

        elif path == '/api/footer':
            updated = cms_db.update_footer_settings(data)
            return self.send_json({'success': True, 'footer': updated})

        elif path == '/api/promotions':
            promo_id = data.get('id', 1)
            cms_db.update_promotion(promo_id, data)
            return self.send_json({'success': True, 'promotions': cms_db.get_promotions()})

        elif path == '/api/menus':
            new_id = cms_db.create_menu(data)
            return self.send_json({'success': True, 'id': new_id}, status=201)

        elif path == '/api/sliders':
            new_id = cms_db.create_slider(data)
            return self.send_json({'success': True, 'id': new_id}, status=201)

        elif path in ('/api/showcase-sliders', '/api/showcase'):
            created = cms_db.create_showcase_slider(data)
            return self.send_json({'success': True, 'slider': created}, status=201)

        elif (path.startswith('/api/showcase-sliders/') or path.startswith('/api/showcase/')) and path.endswith('/update'):
            try:
                parts = [p for p in path.split('/') if p]
                slide_id = int(parts[-2])
                updated = cms_db.update_showcase_slider(slide_id, data)
                return self.send_json({'success': True, 'slider': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/showcase-sliders/') or path.startswith('/api/showcase/')) and path.endswith('/delete'):
            try:
                parts = [p for p in path.split('/') if p]
                slide_id = int(parts[-2])
                cms_db.delete_showcase_slider(slide_id)
                return self.send_json({'success': True, 'deletedId': slide_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/popups':
            popup_id = data.get('id', 1)
            cms_db.update_popup(popup_id, data)
            return self.send_json({'success': True, 'popups': cms_db.get_popups()})

        elif path == '/api/products':
            new_product = cms_db.create_product(data)
            return self.send_json({'success': True, 'product': new_product}, status=201)

        elif path == '/api/upload':
            try:
                import base64, time
                img_bytes = None
                filename = 'uploaded_image.jpg'

                if file_info and file_info.get('content'):
                    img_bytes = file_info['content']
                    filename = file_info.get('filename') or 'uploaded_image.jpg'
                elif data:
                    filename = data.get('filename', 'uploaded_image.jpg')
                    base64_data = data.get('data', '')
                    if ',' in base64_data:
                        base64_data = base64_data.split(',', 1)[1]
                    if base64_data:
                        img_bytes = base64.b64decode(base64_data)

                if not img_bytes:
                    return self.send_json({'error': 'No image data received (គ្មានទិន្នន័យរូបភាព)'}, status=400)

                ext = os.path.splitext(filename)[1].lower()
                if not ext:
                    ext = '.jpg'

                new_filename = f"prod_{int(time.time()*1000)}{ext}"
                upload_dir = os.path.join(DIRECTORY, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, new_filename)

                with open(save_path, 'wb') as f:
                    f.write(img_bytes)

                rel_url = f"uploads/{new_filename}"
                return self.send_json({
                    'success': True,
                    'url': rel_url,
                    'filename': new_filename,
                    'size': len(img_bytes)
                }, status=201)
            except Exception as e:
                return self.send_json({'error': f"Upload error: {str(e)}"}, status=400)

        elif path in ('/api/news/view', '/api/posts/view') or ((path.startswith('/api/news/') or path.startswith('/api/posts/')) and path.endswith('/view')):
            news_id = query.get('id', [None])[0]
            if not news_id and data:
                news_id = data.get('id')
            if not news_id:
                parts = [p for p in path.split('/') if p]
                if len(parts) >= 3 and parts[-1] == 'view':
                    news_id = parts[-2]
            if news_id:
                try:
                    new_views = cms_db.increment_news_views(int(news_id))
                    return self.send_json({'success': True, 'views_count': new_views})
                except Exception as e:
                    return self.send_json({'error': str(e)}, status=400)
            return self.send_json({'error': 'Missing news ID'}, status=400)

        elif path in ('/api/news', '/api/posts'):
            try:
                created = cms_db.create_news(data)
                return self.send_json({'success': True, 'news': created}, status=201)
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/news/') or path.startswith('/api/posts/')) and path.endswith('/update'):
            try:
                parts = [p for p in path.split('/') if p]
                news_id = int(parts[-2])
                updated = cms_db.update_news(news_id, data)
                return self.send_json({'success': True, 'news': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/news/') or path.startswith('/api/posts/')) and path.endswith('/delete'):
            try:
                parts = [p for p in path.split('/') if p]
                news_id = int(parts[-2])
                cms_db.delete_news(news_id)
                return self.send_json({'success': True, 'deletedId': news_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/products/') and path.endswith('/update'):
            # Fallback for clients without PUT
            try:
                prod_id = int(path.split('/')[-2])
                updated = cms_db.update_product(prod_id, data)
                return self.send_json({'success': True, 'product': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/products/') and path.endswith('/delete'):
            # Fallback for clients without DELETE
            try:
                prod_id = int(path.split('/')[-2])
                cms_db.delete_product(prod_id)
                return self.send_json({'success': True, 'deletedId': prod_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/sliders/') and path.endswith('/update'):
            try:
                slider_id = int(path.split('/')[-2])
                updated = cms_db.update_slider(slider_id, data)
                return self.send_json({'success': True, 'slider': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/sliders/') and path.endswith('/delete'):
            try:
                slider_id = int(path.split('/')[-2])
                cms_db.delete_slider(slider_id)
                return self.send_json({'success': True, 'deletedId': slider_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/features':
            if isinstance(data, list):
                for item in data:
                    if 'id' in item:
                        cms_db.update_trust_feature(item['id'], item)
                return self.send_json({'success': True, 'features': cms_db.get_trust_features()})
            elif 'id' in data:
                updated = cms_db.update_trust_feature(data['id'], data)
                return self.send_json({'success': True, 'feature': updated})
            else:
                new_item = cms_db.create_trust_feature(data)
                return self.send_json({'success': True, 'feature': new_item}, status=201)

        elif path.startswith('/api/features/') and path.endswith('/update'):
            try:
                feat_id = int(path.split('/')[-2])
                updated = cms_db.update_trust_feature(feat_id, data)
                return self.send_json({'success': True, 'feature': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/features/') and path.endswith('/delete'):
            try:
                feat_id = int(path.split('/')[-2])
                cms_db.delete_trust_feature(feat_id)
                return self.send_json({'success': True, 'deletedId': feat_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/ingredients':
            try:
                new_item = cms_db.create_botanical_ingredient(data)
                return self.send_json({'success': True, 'ingredient': new_item}, status=201)
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/ingredients/') and path.endswith('/update'):
            try:
                ing_id = int(path.split('/')[-2])
                updated = cms_db.update_botanical_ingredient(ing_id, data)
                return self.send_json({'success': True, 'ingredient': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/ingredients/') and path.endswith('/delete'):
            try:
                ing_id = int(path.split('/')[-2])
                cms_db.delete_botanical_ingredient(ing_id)
                return self.send_json({'success': True, 'deletedId': ing_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/rituals':
            try:
                new_item = cms_db.create_beauty_ritual(data)
                return self.send_json({'success': True, 'ritual': new_item}, status=201)
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/rituals/') and path.endswith('/update'):
            try:
                rit_id = int(path.split('/')[-2])
                updated = cms_db.update_beauty_ritual(rit_id, data)
                return self.send_json({'success': True, 'ritual': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/rituals/') and path.endswith('/delete'):
            try:
                rit_id = int(path.split('/')[-2])
                cms_db.delete_beauty_ritual(rit_id)
                return self.send_json({'success': True, 'deletedId': rit_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/about':
            try:
                updated = cms_db.update_about(data)
                return self.send_json({'success': True, 'about': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/location':
            try:
                updated = cms_db.update_location(data)
                return self.send_json({'success': True, 'location': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/contact':
            try:
                updated = cms_db.update_contact_social(data)
                return self.send_json({'success': True, 'contact': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/messages':
            try:
                res = cms_db.create_contact_message(data)
                return self.send_json(res, status=201)
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/messages/') and path.endswith('/delete'):
            try:
                msg_id = int(path.split('/')[-2])
                cms_db.delete_contact_message(msg_id)
                return self.send_json({'success': True, 'deletedId': msg_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path in ('/api/reviews', '/api/customer-reviews'):
            try:
                new_review = cms_db.create_review(data)
                return self.send_json({'success': True, 'id': new_review.get('id'), 'review': new_review}, status=201)
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/reviews/') or path.startswith('/api/customer-reviews/')) and path.endswith('/update'):
            try:
                parts = [p for p in path.split('/') if p]
                rev_id = int(parts[-2])
                updated = cms_db.update_review(rev_id, data)
                return self.send_json({'success': True, 'review': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/reviews/') or path.startswith('/api/customer-reviews/')) and path.endswith('/approve'):
            try:
                parts = [p for p in path.split('/') if p]
                rev_id = int(parts[-2])
                is_approved = int(data.get('is_approved', 1))
                updated = cms_db.approve_review(rev_id, is_approved)
                return self.send_json({'success': True, 'review': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/reviews/') or path.startswith('/api/customer-reviews/')) and path.endswith('/pin'):
            try:
                parts = [p for p in path.split('/') if p]
                rev_id = int(parts[-2])
                is_featured = data.get('is_featured')
                updated = cms_db.pin_review(rev_id, is_featured=is_featured)
                return self.send_json({'success': True, 'review': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif (path.startswith('/api/reviews/') or path.startswith('/api/customer-reviews/')) and path.endswith('/delete'):
            try:
                parts = [p for p in path.split('/') if p]
                rev_id = int(parts[-2])
                cms_db.delete_review(rev_id)
                return self.send_json({'success': True, 'deletedId': rev_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        self.send_json({'error': 'Not found'}, status=404)

    # ----------------- PUT Request Handling -----------------
    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        data = self.read_json_body()

        if path.startswith('/api/products/'):
            try:
                prod_id = int(path.split('/')[-1])
                updated = cms_db.update_product(prod_id, data)
                return self.send_json({'success': True, 'product': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/sliders/'):
            try:
                slider_id = int(path.split('/')[-1])
                updated = cms_db.update_slider(slider_id, data)
                return self.send_json({'success': True, 'slider': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/showcase-sliders/') or path.startswith('/api/showcase/'):
            try:
                parts = [p for p in path.split('/') if p]
                slide_id = int(parts[-1])
                updated = cms_db.update_showcase_slider(slide_id, data)
                return self.send_json({'success': True, 'slider': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/features/'):
            try:
                feat_id = int(path.split('/')[-1])
                updated = cms_db.update_trust_feature(feat_id, data)
                return self.send_json({'success': True, 'feature': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/ingredients/'):
            try:
                ing_id = int(path.split('/')[-1])
                updated = cms_db.update_botanical_ingredient(ing_id, data)
                return self.send_json({'success': True, 'ingredient': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/rituals/'):
            try:
                rit_id = int(path.split('/')[-1])
                updated = cms_db.update_beauty_ritual(rit_id, data)
                return self.send_json({'success': True, 'ritual': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/about':
            try:
                updated = cms_db.update_about(data)
                return self.send_json({'success': True, 'about': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/location':
            try:
                updated = cms_db.update_location(data)
                return self.send_json({'success': True, 'location': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path == '/api/contact':
            try:
                updated = cms_db.update_contact_social(data)
                return self.send_json({'success': True, 'contact': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith('/api/news/') or path.startswith('/api/posts/') or path in ('/api/news', '/api/posts'):
            try:
                news_id = query.get('id', [None])[0]
                if not news_id:
                    parts = [p for p in path.split('/') if p]
                    news_id = parts[-1]
                news_id = int(news_id)
                updated = cms_db.update_news(news_id, data)
                return self.send_json({'success': True, 'news': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/reviews/') or path.startswith('/api/customer-reviews/'):
            try:
                parts = [p for p in path.split('/') if p]
                rev_id = int(parts[-1])
                updated = cms_db.update_review(rev_id, data)
                return self.send_json({'success': True, 'review': updated})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        self.send_json({'error': 'Endpoint not supported for PUT'}, status=404)

    # ----------------- DELETE Request Handling -----------------
    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith('/api/products/'):
            try:
                prod_id = int(path.split('/')[-1])
                cms_db.delete_product(prod_id)
                return self.send_json({'success': True, 'deletedId': prod_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/news/') or path.startswith('/api/posts/') or path in ('/api/news', '/api/posts'):
            try:
                news_id = query.get('id', [None])[0]
                if not news_id:
                    parts = [p for p in path.split('/') if p]
                    news_id = parts[-1]
                news_id = int(news_id)
                cms_db.delete_news(news_id)
                return self.send_json({'success': True, 'deletedId': news_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/menus/'):
            try:
                menu_id = int(path.split('/')[-1])
                cms_db.delete_menu(menu_id)
                return self.send_json({'success': True, 'deletedId': menu_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/sliders/'):
            try:
                slider_id = int(path.split('/')[-1])
                cms_db.delete_slider(slider_id)
                return self.send_json({'success': True, 'deletedId': slider_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/showcase-sliders/') or path.startswith('/api/showcase/'):
            try:
                parts = [p for p in path.split('/') if p]
                slide_id = int(parts[-1])
                cms_db.delete_showcase_slider(slide_id)
                return self.send_json({'success': True, 'deletedId': slide_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/features/'):
            try:
                feat_id = int(path.split('/')[-1])
                cms_db.delete_trust_feature(feat_id)
                return self.send_json({'success': True, 'deletedId': feat_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/ingredients/'):
            try:
                ing_id = int(path.split('/')[-1])
                cms_db.delete_botanical_ingredient(ing_id)
                return self.send_json({'success': True, 'deletedId': ing_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/rituals/'):
            try:
                rit_id = int(path.split('/')[-1])
                cms_db.delete_beauty_ritual(rit_id)
                return self.send_json({'success': True, 'deletedId': rit_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/messages/'):
            try:
                msg_id = int(path.split('/')[-1])
                cms_db.delete_contact_message(msg_id)
                return self.send_json({'success': True, 'deletedId': msg_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        elif path.startswith('/api/reviews/') or path.startswith('/api/customer-reviews/'):
            try:
                parts = [p for p in path.split('/') if p]
                rev_id = int(parts[-1])
                cms_db.delete_review(rev_id)
                return self.send_json({'success': True, 'deletedId': rev_id})
            except Exception as e:
                return self.send_json({'error': str(e)}, status=400)

        self.send_json({'error': 'Endpoint not supported for DELETE'}, status=404)

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        clean_path = path.rstrip('/')
        if clean_path in ('/dashboard_admin', '/admin', '/dashboard_admin/index.html'):
            self.path = '/admin.html'
        elif clean_path in ('', '/'):
            self.path = '/index.html'
        return super().do_HEAD()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def run():
    import time
    socketserver.TCPServer.allow_reuse_address = True
    port_to_use = PORT
    try:
        httpd = socketserver.TCPServer(("", port_to_use), FullStackHandler)
    except OSError:
        port_to_use = 8080
        httpd = socketserver.TCPServer(("", port_to_use), FullStackHandler)

    print("=" * 70, flush=True)
    print("🌻 MISS SUNFLOWER FULL-STACK SERVER & SQLITE BACKEND", flush=True)
    print(f"👉 Public Website:         http://localhost:{port_to_use}/", flush=True)
    print(f"👉 Dashboard Admin:        http://localhost:{port_to_use}/dashboard_admin/", flush=True)
    print(f"👉 REST API Settings:      http://localhost:{port_to_use}/api/settings", flush=True)
    print(f"👉 REST API Products:      http://localhost:{port_to_use}/api/products", flush=True)
    print(f"👉 Database:               SQLite ({cms_db.DB_PATH})", flush=True)
    print("=" * 70, flush=True)
    
    while True:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(0.5)

if __name__ == "__main__":
    run()
