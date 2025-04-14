from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from .constants import CATEGORIES,STATUS_CHOICES


class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    image_url = models.URLField(blank=True, null=True,verbose_name='URL изображение')
    category = models.CharField(choices=CATEGORIES, verbose_name='Категория', max_length=20)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES,verbose_name='Состояние товара')
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False, verbose_name='В архиве')

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

class ExchangeProposal(models.Model):
    ad_sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Предложение #{self.id}: {self.ad_sender.title} -> {self.ad_receiver.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.status == 'accepted':
            self.ad_sender.is_archived = True
            self.ad_receiver.is_archived = True
            self.ad_sender.save()
            self.ad_receiver.save()
        super().save(*args, **kwargs)




