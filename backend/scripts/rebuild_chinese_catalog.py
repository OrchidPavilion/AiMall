import json
import os
import random
import sys
from pathlib import Path
from urllib import request as urlrequest
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import transaction

from apps.behaviors.models import CustomerBehavior
from apps.carts.models import CartItem
from apps.categories.models import ProductCategory
from apps.customers.models import Customer
from apps.products.models import Product, ProductImage, ProductSku
from apps.recommendations.models import UserRecommendation
from apps.recommendations.services import build_recommendations_for_customer

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"

R = random.Random(20260223)
LEAF_IMAGE_CACHE = {}


def http_json(url: str):
    req = urlrequest.Request(url, headers={"User-Agent": UA})
    with urlrequest.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def image_ok(url: str) -> bool:
    try:
        req = urlrequest.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urlrequest.urlopen(req, timeout=3) as resp:
            ct = str(resp.headers.get("Content-Type", ""))
            return 200 <= resp.status < 400 and ct.startswith("image/")
    except Exception:
        try:
            req = urlrequest.Request(url, method="GET", headers={"User-Agent": UA})
            with urlrequest.urlopen(req, timeout=3) as resp:
                ct = str(resp.headers.get("Content-Type", ""))
                return 200 <= resp.status < 400 and ct.startswith("image/")
        except Exception:
            return False


def commons_search_images(query: str, limit: int = 10):
    params = (
        "action=query"
        "&format=json"
        "&generator=search"
        "&gsrnamespace=6"
        f"&gsrlimit={limit}"
        f"&gsrsearch={quote_plus(query)}"
        "&prop=imageinfo"
        "&iiprop=url|mime"
        "&iiurlwidth=960"
        "&origin=*"
    )
    url = f"{COMMONS_API}?{params}"
    data = http_json(url)
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for page in pages.values():
        infos = page.get("imageinfo") or []
        if not infos:
            continue
        info = infos[0]
        mime = str(info.get("mime") or "")
        if not mime.startswith("image/"):
            continue
        if "svg" in mime.lower():
            continue
        u = info.get("thumburl") or info.get("url")
        if isinstance(u, str) and u.startswith("http"):
            out.append(u)
    return out


def create_category_path(l1: str, l2: str, l3: str):
    root, _ = ProductCategory.objects.get_or_create(name=l1, parent=None, defaults={"sort": 0, "enabled": True})
    c2, _ = ProductCategory.objects.get_or_create(name=l2, parent=root, defaults={"sort": 0, "enabled": True})
    c3, _ = ProductCategory.objects.get_or_create(name=l3, parent=c2, defaults={"sort": 0, "enabled": True})
    return c3


LEAF_IMAGE_KEYWORDS = {
    "综合训练器": ["gym machine", "multi gym machine", "strength training machine"],
    "跑步机": ["treadmill exercise", "gym treadmill", "running machine exercise"],
    "健身车": ["exercise bike", "stationary bike gym", "fitness bike"],
    "哑铃": ["dumbbell", "dumbbell gym", "weight training dumbbell"],
    "壶铃": ["kettlebell", "kettlebell fitness", "kettlebell training"],
    "杠铃片": ["barbell weight plate", "weight plate gym", "barbell plate"],
    "弹力带": ["resistance band exercise", "fitness resistance band", "exercise band"],
    "瑜伽垫": ["yoga mat", "fitness mat", "exercise mat"],
    "筋膜枪": ["massage gun", "percussion massage device", "massage gun therapy"],
    "运动上衣": ["sports jersey shirt", "athletic shirt", "sportswear top"],
    "运动短裤": ["sports shorts", "athletic shorts", "training shorts"],
    "压缩紧身裤": ["compression leggings sports", "athletic leggings", "sports tights"],
    "笔记本电脑": ["laptop computer", "notebook computer", "laptop open"],
    "显示器": ["computer monitor", "lcd monitor desk", "pc monitor"],
    "显卡": ["graphics card pcb", "video card computer", "GPU card"],
    "CPU": ["CPU processor chip", "computer processor package", "microprocessor"],
    "内存": ["computer RAM memory module", "DIMM memory", "RAM stick"],
    "主板": ["computer motherboard", "pc motherboard", "motherboard electronic"],
    "电源": ["computer power supply unit", "PSU computer", "desktop power supply"],
    "机箱": ["computer case desktop", "pc tower case", "desktop computer chassis"],
    "拓展坞": ["laptop docking station", "USB-C dock", "computer dock"],
    "支架": ["monitor arm stand", "laptop stand desk", "computer stand"],
    "鼠标": ["computer mouse", "wireless mouse computer", "gaming mouse"],
    "键盘": ["computer keyboard", "mechanical keyboard", "pc keyboard"],
}


def leaf_image_pool(leaf: str) -> list[str]:
    if leaf in LEAF_IMAGE_CACHE:
        return LEAF_IMAGE_CACHE[leaf]
    queries = LEAF_IMAGE_KEYWORDS.get(leaf, [leaf])
    urls = []
    seen = set()
    for q in queries:
        for u in commons_search_images(q, limit=18):
            if u in seen:
                continue
            seen.add(u)
            urls.append(u)
            if len(urls) >= 3:
                break
        if len(urls) >= 3:
            break
    if not urls:
        fitness_leafs = {"综合训练器", "跑步机", "健身车", "哑铃", "壶铃", "杠铃片", "弹力带", "瑜伽垫", "筋膜枪", "运动上衣", "运动短裤", "压缩紧身裤"}
        fallback_queries = ["fitness equipment", "gym equipment"] if leaf in fitness_leafs else ["computer hardware", "computer peripheral"]
        for q in fallback_queries:
            for u in commons_search_images(q, limit=18):
                if u in seen:
                    continue
                seen.add(u)
                urls.append(u)
                if len(urls) >= 3:
                    break
            if len(urls) >= 3:
                break
    if not urls:
        raise RuntimeError(f"未找到可用图片: {leaf}")
    while len(urls) < 3:
        urls.append(urls[-1])
    LEAF_IMAGE_CACHE[leaf] = urls[:3]
    return urls


FITNESS_TREE = {
    "健身运动": {
        "健身器械": ["综合训练器", "跑步机", "健身车"],
        "力量训练": ["哑铃", "壶铃", "杠铃片"],
        "拉伸康复": ["弹力带", "瑜伽垫", "筋膜枪"],
        "运动服饰": ["运动上衣", "运动短裤", "压缩紧身裤"],
    }
}

TECH_TREE = {
    "数码科技": {
        "电脑整机": ["笔记本电脑"],
        "显示设备": ["显示器"],
        "电脑硬件": ["显卡", "CPU", "内存", "主板", "电源", "机箱"],
        "连接扩展": ["拓展坞", "支架"],
        "外设办公": ["鼠标", "键盘"],
    }
}

BRANDS = {
    "综合训练器": ["锐动", "强虎机能", "星跃"],
    "跑步机": ["奔峰", "迈驰", "极步"],
    "健身车": ["飞轮动力", "骑感", "速燃"],
    "哑铃": ["铁域", "力派", "悍练"],
    "壶铃": ["铁域", "黑虎机能", "稳核"],
    "杠铃片": ["力派", "稳核", "硬核健身"],
    "弹力带": ["舒练", "柔能", "燃动"],
    "瑜伽垫": ["舒练", "宁韧", "静衡"],
    "筋膜枪": ["松驰", "极脉", "深击"],
    "运动上衣": ["跃动", "风行", "疾速"],
    "运动短裤": ["跃动", "风行", "战训"],
    "压缩紧身裤": ["战训", "贴合", "爆发"],
    "笔记本电脑": ["星曜", "灵刃", "创想"],
    "显卡": ["影驰星", "霆锋", "极算"],
    "显示器": ["视界", "极幕", "清域"],
    "CPU": ["锐算", "核擎", "飞核"],
    "内存": ["速芯", "光速存", "雷霆条"],
    "主板": ["战斧", "钛虎机板", "极境板"],
    "电源": ["稳供", "金核源", "黑金电源"],
    "机箱": ["星舰箱", "锋塔", "静域机箱"],
    "拓展坞": ["扩联", "多接口", "桌面拓展"],
    "鼠标": ["迅影", "疾点", "静音灵控"],
    "键盘": ["敲击者", "灵键", "光轴"],
    "支架": ["升降架", "桌面臂", "稳固托架"],
}


def category_specs(leaf: str, idx: int):
    # 全部中文字段和值，便于前后端展示统一
    if leaf in {"哑铃", "壶铃"}:
        weight = [10, 15, 20][idx % 3]
        return {"重量": f"{weight}kg", "材质": "包胶铸铁", "适用场景": "家庭力量训练"}, f"{weight}kg 单只"
    if leaf == "杠铃片":
        weight = [5, 10, 15][idx % 3]
        return {"重量": f"{weight}kg", "孔径": "50mm", "材质": "橡胶包边"}, f"{weight}kg 杠铃片"
    if leaf == "弹力带":
        pull = ["15-35磅", "25-65磅", "35-85磅"][idx % 3]
        return {"阻力范围": pull, "材质": "天然乳胶", "长度": "208cm"}, f"{pull}"
    if leaf == "瑜伽垫":
        thick = ["6mm", "8mm", "10mm"][idx % 3]
        return {"厚度": thick, "材质": "TPE环保材质", "尺寸": "183x61cm"}, f"{thick}"
    if leaf == "筋膜枪":
        rpm = ["1800-2600转/分", "1600-3000转/分", "2000-3200转/分"][idx % 3]
        return {"档位": "6档", "转速范围": rpm, "续航": "4-6小时"}, "6档续航版"
    if leaf in {"综合训练器", "跑步机", "健身车"}:
        spec_map = {
            "综合训练器": ({"承重": "150kg", "功能": "推胸/高位下拉/卷腹", "占地": "190x120cm"}, "家用综合款"),
            "跑步机": ({"跑带宽度": "48cm", "峰值马力": "3.5HP", "折叠": "支持"}, "折叠静音款"),
            "健身车": ({"阻力系统": "磁控16档", "飞轮": "8kg", "承重": "130kg"}, "磁控燃脂款"),
        }
        return spec_map[leaf]
    if leaf in {"运动上衣", "运动短裤", "压缩紧身裤"}:
        size = ["M/L", "L/XL", "XL/2XL"][idx % 3]
        return {"尺码": size, "面料": "速干弹力面料", "适用": "训练/跑步"}, size
    if leaf == "笔记本电脑":
        cpu = ["酷睿i7", "锐龙7", "酷睿Ultra 7"][idx % 3]
        return {"处理器": cpu, "内存": "16GB", "硬盘": "1TB SSD", "屏幕": "16英寸 2.5K"}, f"{cpu} / 16GB / 1TB"
    if leaf == "显卡":
        chip = ["高性能图形芯片 12GB", "高性能图形芯片 16GB", "高性能图形芯片 8GB"][idx % 3]
        return {"显存": chip.split()[-1], "散热": "三风扇", "接口": "HDMI/DP"}, chip
    if leaf == "显示器":
        size = ["27英寸 2K 180Hz", "32英寸 4K 144Hz", "24英寸 1080P 165Hz"][idx % 3]
        return {"尺寸": size.split()[0], "分辨率": size.split()[1], "刷新率": size.split()[2], "面板": "IPS"}, size
    if leaf == "CPU":
        core = ["8核16线程", "12核20线程", "16核24线程"][idx % 3]
        return {"核心线程": core, "主频": "4.5GHz+", "工艺": "先进制程"}, core
    if leaf == "内存":
        spec = ["DDR5 32GB 6000MHz", "DDR5 64GB 5600MHz", "DDR4 32GB 3600MHz"][idx % 3]
        return {"容量": spec.split()[1], "频率": spec.split()[2], "代际": spec.split()[0]}, spec
    if leaf == "主板":
        chipset = ["高性能芯片组ATX", "主流芯片组M-ATX", "电竞芯片组ATX"][idx % 3]
        return {"板型": chipset.split()[-1], "内存插槽": "4条", "扩展": "PCIe / M.2"}, chipset
    if leaf == "电源":
        p = ["650W 金牌", "750W 金牌全模组", "850W 金牌全模组"][idx % 3]
        return {"额定功率": p.split()[0], "认证": "80Plus金牌", "模组": "全模组" if "全模组" in p else "非模组"}, p
    if leaf == "机箱":
        style = ["中塔侧透", "海景房侧透", "静音中塔"][idx % 3]
        return {"机箱类型": style, "风扇位": "前3后1上2", "兼容主板": "ATX/M-ATX"}, style
    if leaf == "拓展坞":
        ports = ["8合1", "10合1", "12合1"][idx % 3]
        return {"接口组合": ports, "输出": "HDMI 4K", "传输": "USB3.2"}, ports
    if leaf == "鼠标":
        dpi = ["26000DPI", "12000DPI", "静音办公款"][idx % 3]
        return {"连接": "2.4G/蓝牙", "传感器": dpi, "按键寿命": "5000万次"}, dpi
    if leaf == "键盘":
        key = ["机械键盘 红轴", "机械键盘 茶轴", "无线薄膜键盘"][idx % 3]
        return {"布局": "98键", "连接": "有线/蓝牙", "背光": "支持"}, key
    if leaf == "支架":
        kind = ["显示器支架", "笔记本支架", "双屏支架"][idx % 3]
        return {"材质": "铝合金", "承重": "2-9kg", "调节": "升降/俯仰/旋转"}, kind
    return {"规格": "标准款"}, "标准款"


def base_price(leaf: str, idx: int) -> int:
    prices = {
        "综合训练器": [499900, 699900, 899900],
        "跑步机": [239900, 329900, 459900],
        "健身车": [129900, 189900, 259900],
        "哑铃": [19900, 29900, 45900],
        "壶铃": [12900, 19900, 26900],
        "杠铃片": [9900, 15900, 22900],
        "弹力带": [5900, 8900, 12900],
        "瑜伽垫": [6900, 9900, 13900],
        "筋膜枪": [15900, 25900, 39900],
        "运动上衣": [12900, 16900, 22900],
        "运动短裤": [11900, 14900, 19900],
        "压缩紧身裤": [14900, 18900, 24900],
        "笔记本电脑": [559900, 699900, 899900],
        "显卡": [259900, 399900, 599900],
        "显示器": [109900, 199900, 299900],
        "CPU": [149900, 229900, 349900],
        "内存": [49900, 89900, 129900],
        "主板": [89900, 129900, 189900],
        "电源": [39900, 59900, 89900],
        "机箱": [29900, 49900, 79900],
        "拓展坞": [16900, 25900, 35900],
        "鼠标": [9900, 19900, 39900],
        "键盘": [15900, 29900, 49900],
        "支架": [12900, 19900, 29900],
    }
    return prices.get(leaf, [9900, 12900, 15900])[idx % 3]


def product_name(leaf: str, idx: int) -> str:
    brand = BRANDS.get(leaf, ["艾购"])[idx % len(BRANDS.get(leaf, ["艾购"]))]
    suffix = ["标准版", "升级版", "旗舰版", "专业版"][idx % 4]
    return f"{brand}{leaf} {suffix}"


def subtitle_text(l1: str, l2: str, leaf: str) -> str:
    return f"{l1} / {l2} / {leaf}"


def detail_html(name: str, spec_values: dict) -> str:
    lines = "".join([f"<li>{k}：{v}</li>" for k, v in spec_values.items()])
    return (
        f"<h3>{name}</h3>"
        "<p>中文商品资料（线上图片资源已校验可访问），用于 AiMall 演示与功能验收。</p>"
        f"<ul>{lines}</ul>"
        "<p>支持购物车、推荐、浏览与管理后台编辑。</p>"
    )


def iter_leafs():
    for tree in [FITNESS_TREE, TECH_TREE]:
        for l1, l2_map in tree.items():
            for l2, l3_list in l2_map.items():
                for leaf in l3_list:
                    yield l1, l2, leaf


def purge_old_catalog():
    CartItem.objects.all().delete()
    UserRecommendation.objects.all().delete()
    CustomerBehavior.objects.all().delete()
    Product.objects.all().delete()
    for level in (3, 2, 1):
        ProductCategory.objects.filter(level=level).delete()


def build_catalog():
    created = 0
    for l1, l2, leaf in iter_leafs():
        category = create_category_path(l1, l2, leaf)
        leaf_pool = leaf_image_pool(leaf)
        count = 3 if leaf not in {"笔记本电脑", "显卡", "显示器", "CPU"} else 4
        for i in range(count):
            imgs = []
            for _ in range(3):
                imgs.append(leaf_pool[(i + len(imgs)) % len(leaf_pool)])
            spec_values, spec_text = category_specs(leaf, i)
            name = product_name(leaf, i)
            price = base_price(leaf, i)
            sales = R.randint(80, 2000) if l1 == "数码科技" else R.randint(60, 1200)
            views = sales * R.randint(4, 11) + R.randint(10, 300)
            stock = R.randint(12, 240)
            p = Product.objects.create(
                category=category,
                name=name,
                subtitle=subtitle_text(l1, l2, leaf),
                main_image=imgs[0],
                default_spec_name=spec_text,
                default_price=price,
                sales_count=sales,
                view_count=views,
                status="ON_SHELF",
                sort=R.randint(0, 20),
                summary=f"{name}，适合{l2}场景，支持前后台完整演示流程。",
                detail_content=detail_html(name, spec_values),
            )
            for n, url in enumerate(imgs, start=1):
                ProductImage.objects.create(product=p, image_url=url, sort=n)
            ProductSku.objects.create(
                product=p,
                sku_code=f"CN-{leaf}-{i+1}",
                spec_values=spec_values,
                spec_name_text=spec_text,
                price=price,
                stock=stock,
                image_url=imgs[0],
                is_default=True,
                status=True,
            )
            created += 1
    return created


def cleanup_no_image():
    deleted = 0
    for p in Product.objects.all():
        has_main = bool((p.main_image or "").strip())
        has_gallery = p.images.exists()
        if not has_main or not has_gallery:
            p.delete()
            deleted += 1
    return deleted


def rebuild_recommendations():
    for c in Customer.objects.all()[:50]:
        build_recommendations_for_customer(c, limit=12, persist=True)


@transaction.atomic
def main():
    print("按分类从 Wikimedia Commons 获取图片...")
    print("清空旧商品/分类/购物车/行为/推荐...")
    purge_old_catalog()
    print("重建中文商品目录...")
    created = build_catalog()
    removed = cleanup_no_image()
    rebuild_recommendations()
    print(f"完成：创建商品={created}，删除无图商品={removed}，最终商品数={Product.objects.count()}，分类数={ProductCategory.objects.count()}")


if __name__ == "__main__":
    main()
