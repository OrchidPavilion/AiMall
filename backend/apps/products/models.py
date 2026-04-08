from django.db import models


class Product(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "草稿"),
        ("ON_SHELF", "上架"),
        ("OFF_SHELF", "下架"),
    ]

    category = models.ForeignKey("categories.ProductCategory", on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True, default="")
    main_image = models.CharField(max_length=500, blank=True, default="")
    default_spec_name = models.CharField(max_length=100, blank=True, default="")
    default_price = models.IntegerField(default=0)
    sales_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ON_SHELF")
    sort = models.IntegerField(default=0)
    summary = models.TextField(blank=True, default="")
    detail_content = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-sort", "-id"]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.CharField(max_length=500)
    sort = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort", "id"]


class ProductSku(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="skus")
    sku_code = models.CharField(max_length=100, blank=True, default="")
    spec_values = models.JSONField(default=dict, blank=True)
    spec_name_text = models.CharField(max_length=255, blank=True, default="")
    price = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    image_url = models.CharField(max_length=500, blank=True, default="")
    is_default = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "id"]
