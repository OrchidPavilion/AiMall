from django.core.exceptions import ValidationError
from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    level = models.PositiveSmallIntegerField(default=1)
    icon = models.CharField(max_length=255, blank=True, default="")
    sort = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort", "id"]

    def clean(self):
        if self.parent_id:
            if self.parent_id == self.id:
                raise ValidationError("父分类不能是自身")
            parent_level = self.parent.level if self.parent else 1
            self.level = parent_level + 1
        else:
            self.level = 1
        if self.level > 3:
            raise ValidationError("分类最多支持3级")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
