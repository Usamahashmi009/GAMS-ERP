from django.contrib import admin
from .models import *
from .forms import *


class StockCreateAdmin(admin.ModelAdmin):
   list_display = [ 'item_name', 'quantity']
   form = StockCreateForm
   # list_filter = ['category']
   # search_fields = ['category', 'item_name']


class CompanycreateAdmin(admin.ModelAdmin):
   list_display = ['name']
   form = AddItemCompanyForm

class VendorcreateAdmin(admin.ModelAdmin):
   list_display= ['name']
   form = AddVenderForm

class AddCashAdmin(admin.ModelAdmin):
   list_display= ['cash']
   form = AddCashForm





admin.site.register(Company,CompanycreateAdmin)
admin.site.register(Stock, StockCreateAdmin)
admin.site.register(Category)
admin.site.register(Vender,VendorcreateAdmin)
admin.site.register(ActionHistory,)
admin.site.register(AddCash,)
admin.site.register(Itemsmodel)
admin.site.register(Sale)