# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user_id', 'permission_id'),)

class Users(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=255, default='Customer')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False  
        db_table = 'users'
        
class Banners(models.Model):
    banner_url = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'banners'


class CartItems(models.Model):
    cart = models.ForeignKey('Carts', models.CASCADE)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cart_items'


class Carts(models.Model):
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'carts'


class Categories(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'categories'


class Contacts(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    sent_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'contacts'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class MainCustomer(models.Model):
    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    user_id = models.IntegerField(unique=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'main_customer'


class OrderAddresses(models.Model):
    order = models.ForeignKey('Orders', models.CASCADE)
    country = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    ward = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'order_addresses'


class OrderItems(models.Model):
    order = models.ForeignKey('Orders', models.CASCADE)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_items'


class Orders(models.Model):
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE
    )
    payment_method = models.ForeignKey('PaymentMethod', models.DO_NOTHING)
    promo = models.ForeignKey('Promotions', models.DO_NOTHING)
    receiver_name = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=18, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    final_amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=11)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'orders'


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'payment_method'


class ProductImages(models.Model):

    product = models.ForeignKey('Products', on_delete=models.CASCADE)    
    image_url = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'product_images'


class Products(models.Model):
    category = models.ForeignKey(Categories, models.DO_NOTHING)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    stock = models.IntegerField()
    sold = models.IntegerField()
    weight_grams = models.IntegerField()
    created_at = models.DateTimeField()
    price = models.DecimalField(max_digits=18, decimal_places=2)
    state = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'products'


class ProductsReview(models.Model):
    product = models.ForeignKey(Products, models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rating = models.IntegerField()
    comment = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'products_review'


class Promotions(models.Model):
    code = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=18, decimal_places=2)
    start_date = models.DateField() 
    end_date = models.DateField()

    class Meta:
        managed = True
        db_table = 'promotions'


class UserAddresses(models.Model):
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE
    )
    country = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    ward = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'user_addresses'



