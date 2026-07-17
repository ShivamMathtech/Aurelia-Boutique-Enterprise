from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import Category, Coupon, Product, ProductVariant, SiteSetting, User, UserRole

PRODUCTS = [
    {
        "title": "Rosewood Embroidered Anarkali",
        "slug": "rosewood-embroidered-anarkali",
        "brand": "Aurelia Atelier",
        "sku": "AA-AN-1001",
        "category": "ethnic-wear",
        "description": "A floor-length rosewood Anarkali finished with delicate thread embroidery, a soft flare and an elegant matching dupatta.",
        "fabric": "Silk blend",
        "fit": "Flared",
        "care": "Dry clean only",
        "occasion": "Festive & Wedding",
        "price": 4299,
        "compare": 5999,
        "image": "https://images.unsplash.com/photo-1583391733956-6c78276477e2?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=1000&q=85",
        "weight": 850,
        "featured": True,
        "bestseller": True,
        "colors": ["Rosewood", "Wine"],
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "title": "Ivory Chikankari Kurta Set",
        "slug": "ivory-chikankari-kurta-set",
        "brand": "Noor Studio",
        "sku": "NS-KS-2002",
        "category": "kurta-sets",
        "description": "An airy ivory kurta set featuring tonal chikankari-inspired embroidery, straight trousers and a light organza dupatta.",
        "fabric": "Cotton viscose",
        "fit": "Straight",
        "care": "Gentle hand wash",
        "occasion": "Day Events",
        "price": 2899,
        "compare": 3799,
        "image": "https://images.unsplash.com/photo-1610189012906-4c0aa9b9781e?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1597983073493-88cd35cf93b0?auto=format&fit=crop&w=1000&q=85",
        "weight": 620,
        "featured": True,
        "bestseller": True,
        "colors": ["Ivory", "Powder Blue"],
        "sizes": ["XS", "S", "M", "L", "XL"],
    },
    {
        "title": "Midnight Satin Wrap Dress",
        "slug": "midnight-satin-wrap-dress",
        "brand": "Aurelia Edit",
        "sku": "AE-DR-3003",
        "category": "western-dresses",
        "description": "A fluid satin midi dress with a flattering wrap construction, soft drape and refined evening silhouette.",
        "fabric": "Premium satin",
        "fit": "Wrap fit",
        "care": "Dry clean recommended",
        "occasion": "Evening & Party",
        "price": 3499,
        "compare": 4499,
        "image": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=1000&q=85",
        "weight": 480,
        "featured": True,
        "bestseller": False,
        "colors": ["Midnight", "Emerald"],
        "sizes": ["XS", "S", "M", "L"],
    },
    {
        "title": "Sage Linen Co-ord Set",
        "slug": "sage-linen-coord-set",
        "brand": "Mysa Collective",
        "sku": "MC-CO-4004",
        "category": "co-ord-sets",
        "description": "A relaxed sage co-ord featuring a tailored sleeveless top and wide-leg trousers for polished everyday dressing.",
        "fabric": "Linen blend",
        "fit": "Relaxed",
        "care": "Cold machine wash",
        "occasion": "Work & Brunch",
        "price": 2599,
        "compare": 3299,
        "image": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1594633313593-bab3825d0caf?auto=format&fit=crop&w=1000&q=85",
        "weight": 540,
        "featured": True,
        "bestseller": True,
        "colors": ["Sage", "Sand"],
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "title": "Crimson Banarasi Saree",
        "slug": "crimson-banarasi-saree",
        "brand": "Kashi Loom",
        "sku": "KL-SA-5005",
        "category": "sarees",
        "description": "A ceremonial crimson Banarasi-inspired saree woven with antique-gold motifs and a statement traditional border.",
        "fabric": "Art silk",
        "fit": "Free size",
        "care": "Dry clean only",
        "occasion": "Wedding & Ceremony",
        "price": 5199,
        "compare": 6999,
        "image": "https://images.unsplash.com/photo-1610030469668-93510a792e58?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1610189028605-5b1c7c3e1394?auto=format&fit=crop&w=1000&q=85",
        "weight": 900,
        "featured": True,
        "bestseller": True,
        "colors": ["Crimson", "Royal Blue"],
        "sizes": ["Free Size"],
    },
    {
        "title": "Blush Organza Occasion Gown",
        "slug": "blush-organza-occasion-gown",
        "brand": "Maison Tara",
        "sku": "MT-GW-6006",
        "category": "occasion-wear",
        "description": "A romantic blush gown with layered organza, a structured bodice and subtle hand-finished floral detailing.",
        "fabric": "Organza",
        "fit": "Fitted bodice",
        "care": "Professional dry clean",
        "occasion": "Reception & Celebration",
        "price": 6799,
        "compare": 8499,
        "image": "https://images.unsplash.com/photo-1594552072238-b8a33785b261?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?auto=format&fit=crop&w=1000&q=85",
        "weight": 1050,
        "featured": False,
        "bestseller": False,
        "colors": ["Blush", "Lilac"],
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "title": "Indigo Block Print Midi Dress",
        "slug": "indigo-block-print-midi-dress",
        "brand": "Mitti & Muse",
        "sku": "MM-DR-7007",
        "category": "western-dresses",
        "description": "A breathable indigo midi dress with artisan-inspired block print, tiered skirt and practical side pockets.",
        "fabric": "100% cotton",
        "fit": "Comfort fit",
        "care": "Separate cold wash",
        "occasion": "Everyday",
        "price": 1999,
        "compare": 2599,
        "image": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=1000&q=85",
        "weight": 420,
        "featured": False,
        "bestseller": True,
        "colors": ["Indigo", "Rust"],
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
    },
    {
        "title": "Black Velvet Evening Dress",
        "slug": "black-velvet-evening-dress",
        "brand": "Aurelia Edit",
        "sku": "AE-DR-8008",
        "category": "occasion-wear",
        "description": "A sculpted black velvet dress with a square neckline and refined midi length for timeless evening styling.",
        "fabric": "Stretch velvet",
        "fit": "Body contour",
        "care": "Dry clean only",
        "occasion": "Cocktail & Evening",
        "price": 3899,
        "compare": 4999,
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=1000&q=88",
        "gallery": "https://images.unsplash.com/photo-1539008835657-9e8e9680c956?auto=format&fit=crop&w=1000&q=85",
        "weight": 560,
        "featured": False,
        "bestseller": False,
        "colors": ["Black", "Burgundy"],
        "sizes": ["XS", "S", "M", "L"],
    },
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.scalar(select(User).where(User.email == settings.admin_email.lower())):
            db.add(
                User(
                    name="Aurelia Boutique Administrator",
                    email=settings.admin_email.lower(),
                    password_hash=hash_password(settings.admin_password),
                    role=UserRole.admin,
                )
            )

        categories: dict[str, Category] = {}
        rows = [
            ("Ethnic Wear", "ethnic-wear", "Statement silhouettes for festivals and celebrations", "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=900&q=85"),
            ("Kurta Sets", "kurta-sets", "Refined coordinated sets for effortless dressing", "https://images.unsplash.com/photo-1583391733975-d65e145bc7ad?auto=format&fit=crop&w=900&q=85"),
            ("Western Dresses", "western-dresses", "Contemporary dresses from day to evening", "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=900&q=85"),
            ("Co-ord Sets", "co-ord-sets", "Modern matching sets for work and weekends", "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=85"),
            ("Sarees", "sarees", "Timeless drapes with modern curation", "https://images.unsplash.com/photo-1610030469668-93510a792e58?auto=format&fit=crop&w=900&q=85"),
            ("Occasion Wear", "occasion-wear", "Elegant pieces for memorable celebrations", "https://images.unsplash.com/photo-1594552072238-b8a33785b261?auto=format&fit=crop&w=900&q=85"),
        ]
        for name, slug, description, image_url in rows:
            item = db.scalar(select(Category).where(Category.slug == slug))
            if not item:
                item = Category(name=name, slug=slug, description=description, image_url=image_url)
                db.add(item)
                db.flush()
            categories[slug] = item

        for index, row in enumerate(PRODUCTS):
            if db.scalar(select(Product).where(Product.slug == row["slug"])):
                continue
            product = Product(
                title=row["title"],
                slug=row["slug"],
                brand=row["brand"],
                sku=row["sku"],
                description=row["description"],
                fabric=row["fabric"],
                fit=row["fit"],
                care_instructions=row["care"],
                occasion=row["occasion"],
                price=row["price"],
                compare_at_price=row["compare"],
                stock=0,
                image_url=row["image"],
                gallery_urls=row["gallery"],
                vendor="Aurelia Boutique Verified",
                weight_grams=row["weight"],
                featured=row["featured"],
                bestseller=row["bestseller"],
                category_id=categories[row["category"]].id,
            )
            db.add(product)
            db.flush()
            variants = []
            for color_index, color in enumerate(row["colors"]):
                for size_index, size in enumerate(row["sizes"]):
                    stock = 5 + ((index + color_index + size_index) % 8)
                    variants.append(
                        ProductVariant(
                            product_id=product.id,
                            sku=f"{row['sku']}-C{color_index + 1}-{size.replace(' ', '')}",
                            size=size,
                            color=color,
                            stock=stock,
                            additional_price=0,
                        )
                    )
            product.stock = sum(item.stock for item in variants)
            db.add_all(variants)

        if not db.scalar(select(Coupon).where(Coupon.code == "WELCOME15")):
            db.add(Coupon(code="WELCOME15", discount_percent=15, minimum_order=1999, max_discount=1000))
        defaults = {
            "announcement": "Complimentary shipping above ₹1,499 · Easy 7-day size exchange",
            "hero_title": "Dresses designed for your most beautiful moments.",
            "hero_subtitle": "Discover thoughtfully curated Indian and contemporary silhouettes with verified quality, inclusive sizing and secure delivery.",
            "support_email": "care@aureliaboutique.com",
            "instagram_url": "https://instagram.com/",
            "return_policy": "Easy 7-day size exchange on eligible, unworn garments.",
        }
        for key, value in defaults.items():
            if not db.get(SiteSetting, key):
                db.add(SiteSetting(key=key, value=value))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
