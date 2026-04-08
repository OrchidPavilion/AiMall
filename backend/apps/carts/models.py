from django.db import models


class CartItem(models.Model):
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="cart_items")
    sku = models.ForeignKey("products.ProductSku", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    checked = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("customer", "sku")]
        ordering = ["-updated_at", "-id"]
