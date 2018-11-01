from django.db import models

from utils.ubiutils import next_eligible_datetime


class User(models.Model):
    userid = models.AutoField(db_column='userid', primary_key=True)
    name = models.CharField(db_column='name', max_length=50, db_index=True, null=False)
    free_points = models.IntegerField(db_column='free_points', null=False, default=0)
    free_points_eligible_dtm = models.DateTimeField(default=next_eligible_datetime)
    purchased_points = models.IntegerField(db_column='purchased_points', null=False, default=0)
    email = models.EmailField(db_column='email', max_length=254, db_index=True, null=False)
    is_active = models.BooleanField(db_column='is_active', default=True)
    created_dtm = models.DateTimeField(db_column='created_dtm', auto_now_add=True)

    class Meta:
        db_table = 'user'


class Item(models.Model):
    itemid = models.AutoField(db_column='itemid', primary_key=True)
    name = models.CharField(db_column='name', max_length=50)
    price = models.DecimalField(db_column='price', max_digits=6, decimal_places=2, null=False, default=0)
    created_dtm = models.DateTimeField(db_column='created_dtm', auto_now_add=True)
    type = models.CharField(db_column='type', max_length=30, null=False)
    is_available = models.BooleanField(db_column='is_available', default=True)
    points = models.IntegerField(db_column='points', null=False, default=0)

    class Meta:
        db_table = 'item'


class Transaction(models.Model):
    transactionid = models.AutoField(db_column='transactionid', primary_key=True)
    userid = models.ForeignKey(User, db_column='userid', on_delete=models.CASCADE)
    quantity = models.IntegerField(db_column='quantity', default=1)
    created_dtm = models.DateTimeField(db_column='created_dtm', auto_now_add=True)
    status = models.CharField(db_column='status', max_length=30, null=False)
    free_points_used = models.IntegerField(db_column='free_points_used', default=0)
    purchased_points_used = models.IntegerField(db_column='purchased_points_used', default=0)
    itemid = models.ForeignKey(Item, db_column='itemid', on_delete=models.CASCADE)

    class Meta:
        db_table = 'transaction'
