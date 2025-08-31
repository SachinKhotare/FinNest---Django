from django.db import models
from dashboard.models import Tenant

# ------------------------------
# RaiseIssue model
# ------------------------------
class RaiseIssue(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    OWNER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Acknowledged', 'Acknowledged'),
        ('Resolved by Owner', 'Resolved by Owner'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    urgency = models.CharField(max_length=20)
    estimated_resolution_date = models.DateField(null=True, blank=True)
    details = models.TextField(blank=True)
    image = models.ImageField(upload_to='issue_images/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    owner_status = models.CharField(max_length=30, choices=OWNER_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.title}"


# Vacate submit notice

class VacateNotice(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="vacate_notice")  
    name = models.CharField(max_length=255)
    flat_no = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)   # Auto-filled when submitted
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Vacate Notice - {self.name} ({self.flat_no})"
    


#payment

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)  # e.g. "January"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=200, unique=True)
    payment_id = models.CharField(max_length=200, null=True, blank=True)
    signature = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=50, default="PENDING")  # PENDING / SUCCESS / FAILED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.username} - {self.month} - {self.status}"
    

    
