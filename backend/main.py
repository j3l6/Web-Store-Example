from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .products import Product, DigitalProduct
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

# set-up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCTS = {
    1: {"name": "Laptop", "price": 15000},
    2: {"name": "Smartphone", "price": 30000},
    3: {"name": "Mouse", "price": 500}
}

class DiscountRequest(BaseModel):
    product_id: int
    coupon: float = None

#Methods definition: POST and GET

@app.get("/products")
def get_products():
    return PRODUCTS

@app.post("/calculate-discount")
def calculate_discount(request: DiscountRequest):
    # search product
    product = PRODUCTS.get(request.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # if there is a coupon
    if request.coupon is not None:
        # Coupon validation
        if request.coupon < 1 or request.coupon > 70:
            raise HTTPException(
                status_code=400,
                detail="Discount coupon must be between 1% and 70%"
            )
        # calculate discounted price
        final_price = Product(product['name'], product['price']).get_discounted_price(request.coupon/100)
        return {
            "product_name": product['name'],
            "original_price": product['price'],
            "discount_rate": request.coupon,
            "final_price": final_price
        }
    else:
        # Calculate 20% discount
        final_price = DigitalProduct(product['name'], product['price']).get_discounted_price()
        return {
            "product_name": product['name'],
            "original_price": product['price'],
            "discount_rate": 20,
            "final_price": final_price
        }

# static files
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend')
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, 'static')), name="static")

# Single Page Aplication
@app.get("/", response_class=HTMLResponse)
async def spa():
    with open(os.path.join(frontend_path, 'index.html'), 'r') as file:
        return HTMLResponse(content=file.read())