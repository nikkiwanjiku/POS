from fastapi import FastAPI

from pos.routers.auth import router as auth_router
from pos.routers.category_router import router as category_router
from pos.routers.product_router import router as product_router
from pos.routers.supplier_router import router as supplier_router
from pos.routers.customer_router import router as customer_router
from pos.routers.user_router import router as user_router
from pos.routers.sale_router import router as sale_router
from pos.routers.sale_item_router import router as sale_item_router
from pos.routers.payment_router import router as payment_router
from pos.routers.receipt_router import router as receipt_router


app = FastAPI(
    title="POS API",
    version="1"
)

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(supplier_router)
app.include_router(customer_router)
app.include_router(user_router)
app.include_router(sale_router)
app.include_router(sale_item_router)
app.include_router(payment_router)
app.include_router(receipt_router)

@app.get("/")
def root():
    return {
        "message": "API is working successfully",
    }
