from django.db import models
from accounts.models import CustomUser

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    aadhar_number = models.CharField(max_length=20)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    aadhar_photo = models.ImageField(upload_to='aadhar_photos/', null=True, blank=True)
    agreement_file = models.FileField(upload_to='agreements/', null=True, blank=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name


#add stock
class AddStock(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stocks')

    stock_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)       # Buy price per unit
    current_price = models.DecimalField(max_digits=10, decimal_places=2)   # Current market price per unit

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_investment(self):
        """Total amount spent when buying"""
        return self.quantity * self.buy_price

    @property
    def current_value(self):
        """Current market value"""
        return self.quantity * self.current_price

    @property
    def profit_loss(self):
        """Profit or Loss amount"""
        return self.current_value - self.total_investment

    def __str__(self):
        return f"{self.stock_name} ({self.user.username})"
    

#addSIP
class AddSIP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sips')

    sip_name = models.CharField(max_length=255)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    due_date = models.DateField()
   
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sip_name} ({self.user.username})"

#expenses model


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Expense', 'Expense'),
        ('Income', 'Income'),
        ('Transfer', 'Transfer'),
    ]

    CATEGORY_CHOICES = [
        # Common categories (you can filter based on type in views/forms if needed)
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Rent', 'Rent'),
        ('Entertainment', 'Entertainment'),
        ('Utilities', 'Utilities'),
        ('Transport', 'Transport'),
        ('Shopping', 'Shopping'),
        ('Salary', 'Salary'),
        ('Bonus', 'Bonus'),
        ('Investment', 'Investment'),
        ('Bank', 'Bank Transfer'),
        ('Wallet', 'Wallet Transfer'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # link transaction to a user
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type}: {self.category} - ₹{self.amount}"
