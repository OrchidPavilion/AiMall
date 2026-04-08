import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from apps.categories.models import ProductCategory
from apps.products.models import Product, ProductSku, ProductImage
from apps.customers.models import Customer
from apps.behaviors.models import CustomerBehavior
from apps.recommendations.services import build_recommendations_for_customer


def create_category(name, parent=None, sort=0):
    obj, _ = ProductCategory.objects.get_or_create(name=name, parent=parent, defaults={'sort': sort, 'enabled': True})
    return obj


def create_product(category, name, spec_name, price_yuan, image_seed):
    p, _ = Product.objects.get_or_create(
        name=name,
        defaults={
            'category': category,
            'main_image': f'https://via.placeholder.com/480x360?text={image_seed}',
            'default_spec_name': spec_name,
            'default_price': int(price_yuan * 100),
            'sales_count': 100 + image_seed * 3,
            'view_count': 300 + image_seed * 11,
            'status': 'ON_SHELF',
            'summary': f'{name} 商品简介',
            'detail_content': f'<p>{name} 商品详情（演示数据）</p>',
        },
    )
    if not p.skus.exists():
        sku = ProductSku.objects.create(
            product=p,
            spec_values={'规格': spec_name},
            spec_name_text=spec_name,
            price=int(price_yuan * 100),
            stock=999,
            is_default=True,
        )
        ProductImage.objects.create(product=p, image_url=p.main_image, sort=1)
        ProductImage.objects.create(product=p, image_url=f'https://via.placeholder.com/480x360?text={image_seed}-2', sort=2)
    return p


def main():
    digital = create_category('数码', sort=1)
    home = create_category('家居', sort=2)
    sports = create_category('运动', sort=3)

    headphone = create_category('耳机', parent=digital, sort=1)
    keyboard = create_category('键盘', parent=digital, sort=2)
    cup = create_category('杯具', parent=home, sort=1)
    training = create_category('训练', parent=sports, sort=1)

    bt_headphone = create_category('蓝牙耳机', parent=headphone, sort=1)
    wired_headphone = create_category('有线耳机', parent=headphone, sort=2)
    mech_keyboard = create_category('机械键盘', parent=keyboard, sort=1)
    thermos = create_category('保温杯', parent=cup, sort=1)
    yoga = create_category('瑜伽垫', parent=training, sort=1)

    products = [
        create_product(bt_headphone, '蓝牙耳机 Pro', '黑色', 299, 1),
        create_product(wired_headphone, 'HiFi 有线耳机', '银色', 199, 2),
        create_product(mech_keyboard, '机械键盘 87键', '青轴', 399, 3),
        create_product(thermos, '316不锈钢保温杯', '500ml', 89, 4),
        create_product(thermos, '运动水杯', '600ml', 49, 5),
        create_product(yoga, '防滑瑜伽垫', '标准款', 129, 6),
    ]

    for i in range(7, 31):
        cat = [bt_headphone, mech_keyboard, thermos, yoga][i % 4]
        create_product(cat, f'演示商品{i}', ['标准款', '黑色', '高配版'][i % 3], 29 + i * 3, i)

    c1, _ = Customer.objects.get_or_create(phone='13800000001', defaults={'name': '张三', 'age': 28, 'hobby': '数码产品', 'address': '上海市浦东新区'})
    c2, _ = Customer.objects.get_or_create(phone='13800000002', defaults={'name': '李四', 'age': 31, 'hobby': '运动户外', 'address': '杭州市西湖区'})

    if not c1.behaviors.exists():
        CustomerBehavior.objects.create(customer=c1, behavior_type='SEARCH', target_type='KEYWORD', target_name='蓝牙耳机', source_page='HOME')
        CustomerBehavior.objects.create(customer=c1, behavior_type='CLICK_CATEGORY', target_type='CATEGORY', target_id=bt_headphone.id, target_name='数码/耳机/蓝牙耳机', source_page='HOME')
        CustomerBehavior.objects.create(customer=c1, behavior_type='VIEW_PRODUCT', target_type='PRODUCT', target_id=products[0].id, target_name=products[0].name, source_page='PRODUCT_LIST')
        CustomerBehavior.objects.create(customer=c1, behavior_type='ADD_TO_CART', target_type='PRODUCT', target_id=products[0].id, target_name=products[0].name, source_page='PRODUCT_DETAIL')
    if not c2.behaviors.exists():
        CustomerBehavior.objects.create(customer=c2, behavior_type='SEARCH', target_type='KEYWORD', target_name='瑜伽垫', source_page='HOME')
        CustomerBehavior.objects.create(customer=c2, behavior_type='CLICK_CATEGORY', target_type='CATEGORY', target_id=yoga.id, target_name='运动/训练/瑜伽垫', source_page='HOME')
        CustomerBehavior.objects.create(customer=c2, behavior_type='VIEW_PRODUCT', target_type='PRODUCT', target_id=products[5].id, target_name=products[5].name, source_page='PRODUCT_LIST')

    for c in Customer.objects.all():
        build_recommendations_for_customer(c, limit=10, persist=True)

    print('seed complete')


if __name__ == '__main__':
    main()
