from app.models import Product
from app.schemas import ProductOut


def serialize_product(product: Product) -> ProductOut:
    ratings = [review.rating for review in product.reviews]
    data = ProductOut.model_validate(product)
    data.average_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    data.review_count = len(ratings)
    data.stock = sum(variant.stock for variant in product.variants if variant.is_active)
    return data
