from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Subcategory, Product, Chat, User, QuestionAnswer, Mailing

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Product)


class ChatAdmin(admin.ModelAdmin):
    readonly_fields = ["chat_comment"]

    @admin.display(description="Chat Comment")
    def chat_comment(self, instance):
        return format_html("<i> Do not forget to make the bot a chat admin</i>")


admin.site.register(Chat, ChatAdmin)
admin.site.register(User)
admin.site.register(QuestionAnswer)


class MailingAdmin(admin.ModelAdmin):
    readonly_fields = ["photo_comment"]

    @admin.display(description="Photo Comment")
    def photo_comment(self, instance):
        return format_html("<i>You don't have to upload a photo. You can send just a message without any photo</i>")


admin.site.register(Mailing, MailingAdmin)
