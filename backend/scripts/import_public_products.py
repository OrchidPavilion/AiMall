import json
import os
import sys
import time
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from apps.categories.models import ProductCategory
from apps.products.models import Product, ProductImage, ProductSku
from apps.customers.models import Customer
from apps.recommendations.services import build_recommendations_for_customer

SOURCE_URL = 'https://dummyjson.com/products?limit=36'
IMPORT_ROOT = '外部导入'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'


def http_json(url: str):
    req = urlrequest.Request(url, headers={'User-Agent': UA})
    with urlrequest.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def image_ok(url: str) -> bool:
    try:
        req = urlrequest.Request(url, method='HEAD', headers={'User-Agent': UA})
        with urlrequest.urlopen(req, timeout=4) as resp:
            return 200 <= resp.status < 400 and str(resp.headers.get('Content-Type', '')).startswith('image/')
    except Exception:
        try:
            req = urlrequest.Request(url, method='GET', headers={'User-Agent': UA})
            with urlrequest.urlopen(req, timeout=4) as resp:
                return 200 <= resp.status < 400 and str(resp.headers.get('Content-Type', '')).startswith('image/')
        except Exception:
            return False


def get_or_create_category_chain(category_slug: str):
    root, _ = ProductCategory.objects.get_or_create(name=IMPORT_ROOT, parent=None, defaults={'sort': 90, 'enabled': True})
    display_name = category_slug.replace('-', ' ').strip().title() or 'Imported'
    child, _ = ProductCategory.objects.get_or_create(name=display_name, parent=root, defaults={'sort': 0, 'enabled': True})
    return child


def import_one(item: dict):
    category = get_or_create_category_chain(item.get('category') or 'imported')
    title = (item.get('title') or '').strip()[:200]
    if not title:
        return False, 'empty title'

    candidate_images = []
    thumb = item.get('thumbnail')
    if thumb:
        candidate_images.append(thumb)
    for img in item.get('images') or []:
        if img not in candidate_images:
            candidate_images.append(img)

    valid_images = []
    for u in candidate_images[:4]:
        if not (isinstance(u, str) and u.startswith('http')):
            continue
        if image_ok(u):
            valid_images.append(u)
    if valid_images:
        # 补足图集时不再全部校验，减少导入耗时
        for u in candidate_images:
            if len(valid_images) >= 4:
                break
            if isinstance(u, str) and u.startswith('http') and u not in valid_images:
                valid_images.append(u)
    if not valid_images:
        return False, f'no valid image: {title}'

    brand = (item.get('brand') or '标准款').strip()
    sku_text = f"{brand} / {item.get('sku') or '默认规格'}"[:255]
    price_cents = int(round(float(item.get('price') or 0) * 100))
    stock = int(item.get('stock') or 0)
    rating = float(item.get('rating') or 0)
    review_count = len(item.get('reviews') or [])
    sales = max(int(review_count * 12 + rating * 18), 0)
    views = max(sales * 5 + stock * 3 + int(item.get('id', 0)), sales)

    product, created = Product.objects.get_or_create(
        name=title,
        defaults={
            'category': category,
            'subtitle': (brand or '')[:255],
            'main_image': valid_images[0],
            'default_spec_name': brand or '默认规格',
            'default_price': price_cents,
            'sales_count': sales,
            'view_count': views,
            'status': 'ON_SHELF',
            'sort': 0,
            'summary': (item.get('description') or '')[:2000],
            'detail_content': f"<p>{(item.get('description') or '').strip()}</p><p>来源：DummyJSON（公开示例商品数据）</p>",
        }
    )

    if not created:
        product.category = category
        product.subtitle = (brand or '')[:255]
        product.main_image = valid_images[0]
        product.default_spec_name = brand or '默认规格'
        product.default_price = price_cents
        product.sales_count = sales
        product.view_count = views
        product.status = 'ON_SHELF'
        product.summary = (item.get('description') or '')[:2000]
        product.detail_content = f"<p>{(item.get('description') or '').strip()}</p><p>来源：DummyJSON（公开示例商品数据）</p>"
        product.save()

    product.images.all().delete()
    for idx, img in enumerate(valid_images, start=1):
        ProductImage.objects.create(product=product, image_url=img, sort=idx)

    product.skus.all().delete()
    ProductSku.objects.create(
        product=product,
        sku_code=(item.get('sku') or '')[:100],
        spec_values={
            '品牌': brand,
            '规格': brand or '标准款',
            '重量(g)': item.get('weight') or 0,
        },
        spec_name_text=(brand or '标准款')[:255],
        price=price_cents,
        stock=max(stock, 0),
        image_url=valid_images[0],
        is_default=True,
        status=True,
    )

    return True, 'created' if created else 'updated'


def ensure_demo_customer_passwords():
    changed = 0
    for customer in Customer.objects.filter(password_hash=''):
        customer.set_password('123456')
        customer.save(update_fields=['password_hash', 'updated_at'])
        changed += 1
    return changed


def main():
    payload = http_json(SOURCE_URL)
    products = payload.get('products') or []
    ok = 0
    fail = 0
    for item in products:
        try:
            success_flag, msg = import_one(item)
            if success_flag:
                ok += 1
            else:
                fail += 1
        except Exception as e:
            fail += 1
            print('FAILED', item.get('title'), e)
        time.sleep(0.01)

    pw_changed = ensure_demo_customer_passwords()
    for c in Customer.objects.all()[:20]:
        build_recommendations_for_customer(c, limit=10, persist=True)

    print(f'import finished: success={ok}, failed={fail}, passwords_backfilled={pw_changed}')


if __name__ == '__main__':
    main()
