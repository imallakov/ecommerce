from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "categories"


class Subcategory(models.Model):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "subcategories"


class Product(models.Model):
    name = models.CharField(max_length=128)
    photo = models.ImageField(upload_to='products/')
    description = models.TextField()
    price = models.PositiveIntegerField(default=1)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "products"


class Chat(models.Model):
    name = models.CharField(max_length=128)
    id = models.BigIntegerField(unique=True, primary_key=True)
    username = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "chats"


class User(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    username = models.CharField(max_length=32)
    is_subscription_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} ({self.username})"

    class Meta:
        db_table = "users"


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')

    def __repr__(self):
        return f"CartItem(product={self.product.name}, quantity={self.quantity})"

    class Meta:
        db_table = "cart_items"


class QuestionAnswer(models.Model):
    question = models.TextField()
    answer = models.TextField(null=True)

    def __str__(self):
        return f'Q: {self.question}'

    class Meta:
        db_table = "question_answers"
        verbose_name = "FAQ"


class Mailing(models.Model):
    photo = models.ImageField(upload_to='mailings/', null=True, blank=True)
    message = models.TextField()

    def __str__(self):
        return f'Message: {self.message}'

    class Meta:
        db_table = "mailings"
