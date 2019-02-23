from django.contrib import admin
from goods.models import Goods, SKU, SKUImage
from celery_tasks.html.tasks import generate_static_list_search_html, generate_static_sku_detail_html


class GoodsAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_list_search_html.delay()


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)

    def delete_model(self, request, obj):
        obj.is_launched = False
        obj.save()
        generate_static_sku_detail_html.delay(obj.id)


class ImageAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        print(obj.image.url)
        generate_static_sku_detail_html.delay(obj.sku.id)


# Register your models here.
admin.site.register(Goods, GoodsAdmin)
admin.site.register(SKU, SKUAdmin)
admin.site.register(SKUImage, ImageAdmin)
