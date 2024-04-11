from django.contrib import admin
from .models import Category, Subcategory, Product, Chat, User, questionanswer

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)
admin.site.register(Chat)
admin.site.register(User)
admin.site.register(questionanswer)
