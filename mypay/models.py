from django.db import models

# Create your models here.


class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ('topup', 'Top Up MyPay'),
        ('jasa', 'Bayar Jasa'),
        ('transfer', 'Transfer MyPay'),
        ('withdrawal', 'Withdrawal'),
    ]

    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount}"
