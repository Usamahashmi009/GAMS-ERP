from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Vender(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Expense(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.name

class Itemsmodel(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class ReplacementItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Adjust the relationship as needed
    item_name = models.ForeignKey(Itemsmodel, on_delete=models.CASCADE)  # Adjust the relationship as needed
    price = models.IntegerField()
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.category} - {self.item_name}"

class Stock(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True)
    item_name = models.ForeignKey(Itemsmodel, on_delete=models.CASCADE, blank=True)
    quantity = models.IntegerField(default='0', blank=True, null=True)
    rate = models.IntegerField(default='0', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    vender = models.ForeignKey(Vender, on_delete=models.SET_NULL, null=True)
    receive_quantity = models.IntegerField(default='0', blank=True, null=True)
    receive_by = models.CharField(max_length=50, blank=True, null=True)
    addcash = models.IntegerField(default='0', blank=True, null=True)
    issue_quantity = models.IntegerField(default='0', blank=True, null=True)
    issue_by = models.CharField(max_length=50, blank=True, null=True)
    issue_to = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    reorder_level = models.IntegerField(default='0', blank=True, null=True)
    lastupdate = models.DateTimeField(auto_now_add=False, auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    Expense_category = models.ForeignKey(Expense, on_delete=models.CASCADE,null=True, blank=True)
    batch_number = models.CharField(max_length=10, blank=True, null=True)
    
    @property
    def subtotal(self):
        return self.quantity * self.rate

    def __str__(self):
        return str(self.item_name)
    

class Account_payableModel (models.Model):
    account_payable = models.IntegerField(default='0', blank=True, null=True)
    vender = models.ForeignKey(Vender, on_delete=models.SET_NULL, null=True)


class Product(models.Model):
    Product = models.IntegerField(default=0)

class Sale(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    
    sale_quantity = models.IntegerField()
    sale_date = models.DateTimeField(auto_now_add=True)
    rate= models.IntegerField()
    received_by = models.CharField(max_length=50, blank=True, null=True)
    Date_time = models.DateTimeField(auto_now_add=False, auto_now=True)
    account_recieveable = models.IntegerField(default='0', blank=True, null=True)

    def __str__(self):
        return self.stock

class DefectiveItem(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Adjust the relationship as needed
    item_name = models.ForeignKey(Itemsmodel, on_delete=models.CASCADE)  # Adjust the relationship as needed
    price = models.IntegerField()
    quantity = models.PositiveIntegerField()
    batch_number = models.CharField(max_length=10)
    def __str__(self):
        return f"{self.category} - {self.item_name}"

class Expenses(models.Model):
    Exp = models.ForeignKey(Expense, on_delete=models.CASCADE)   
    amount= models.IntegerField()
    def __str__(self):
        return self.Exp

class ActionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    cash = models.ForeignKey(Stock, on_delete=models.CASCADE, blank=True,null=True)
    sale_cash = models.IntegerField(default=0, blank=True, null=True)
    cash_hand = models.IntegerField(default=0, blank=True, null=True)
    def __str__(self):
        return f'{self.user.username} - {self.action_type} - {self.timestamp}'

class AddCash(models.Model):
    cash = models.IntegerField(default=0, blank=True, null=True)
    def __str__(self):
        return str(self.cash)

class CostOfGoodsSold(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item_name = models.ForeignKey(Itemsmodel, on_delete=models.CASCADE)
    sale_quantity = models.IntegerField()
    stock_rate = models.IntegerField()
    total_values = models.IntegerField()
    def __str__(self):
        return f"{self.category} - {self.item_name} - {self.sale_quantity}"

class StockReturn(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    return_quantity = models.PositiveIntegerField()
    return_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Return of {self.return_quantity} {self.stock.item_name}(s) on {self.return_date}"

class COGSModel(models.Model):
    cogs_sum = models.DecimalField(max_digits=100, decimal_places=0, default=0) # Adjust max_digits and decimal_places as needed
    def __str__(self):
        return f"COGSModel - {self.cogs_sum}"

class OwnerEquity(models.Model):
    capital = models.IntegerField()
    def __str__(self):
        return str(self.capital)

class SalesReturn(models.Model):
    batch_number = models.ForeignKey(Stock, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Import Category from your models
    item_name = models.ForeignKey(Itemsmodel, on_delete=models.CASCADE)  # Import Itemsmodel from your models
    price = models.IntegerField()
    quantity = models.IntegerField()
