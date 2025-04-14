from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView


from .forms import ProductForm
from .models import ExchangeProposal
from .constants import STATUS_CHOICES

User = get_user_model()

from django.db import models
from django.views.generic import ListView
from .models import Ad
from .constants import CATEGORIES

class Products(ListView):
    model = Ad
    template_name = 'ads/index.html'
    context_object_name = 'products'
    paginate_by = 5

    def get_queryset(self):
        queryset = Ad.objects.filter(is_archived=False).order_by('-created_at')  # Исключаем архивные объявления

        # Поиск по ключевым словам (без учета регистра)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(title__icontains=query) | models.Q(description__icontains=query)
            )

        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Фильтрация по состоянию товара
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = CATEGORIES

        context['query_params'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'condition': self.request.GET.get('condition', ''),
        }

        return context

class AddProduct(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = ProductForm
    template_name = 'ads/create_ad.html'
    success_url = reverse_lazy('products')

    def form_valid(self, form):
        # Привязываем текущего пользователя к объявлению
        form.instance.user = self.request.user
        messages.success(self.request, 'Объявление успешно создано!')
        return super().form_valid(form)


class ProductDetail(DetailView):
    model = Ad
    template_name = 'ads/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        return get_object_or_404(Ad, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_ads'] = Ad.objects.filter(user=self.request.user, is_archived=False)
        return context

class UpdateProduct(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = ProductForm
    template_name = 'ads/create_ad.html'
    success_url = reverse_lazy('products')

    # Настройка перенаправления неавторизованных пользователей
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied("Вы не можете редактировать это объявление.")
        return obj


class DeleteProduct(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/create_ad.html'
    success_url = reverse_lazy('products')

    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied("Вы не можете удалить это объявление.")
        return obj


class ProposalList(ListView):
    model = ExchangeProposal
    template_name = 'ads/exchange_proposal.html'
    context_object_name = 'proposals'
    paginate_by = 5

    def get_queryset(self):
        queryset = ExchangeProposal.objects.filter(
            models.Q(ad_sender__user=self.request.user) | models.Q(ad_receiver__user=self.request.user)
        ).order_by('-created_at')

        # Фильтрация по отправителю (пользователю)
        sender_user_id = self.request.GET.get('sender_user_id')
        if sender_user_id:
            try:
                sender_user_id = int(sender_user_id)
                queryset = queryset.filter(ad_sender__user__id=sender_user_id)
            except ValueError:
                pass

        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status in dict(STATUS_CHOICES):  # Проверяем, что статус допустим
            queryset = queryset.filter(status=status)

        # Отладочный вывод
        print("GET parameters:", self.request.GET)
        print("Filtered queryset:", queryset.query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['users'] = User.objects.filter(
            ad__sent_proposals__ad_receiver__user=self.request.user
        ).distinct()

        context['query_params'] = {
            'sender_user_id': self.request.GET.get('sender_user_id', ''),
            'status': self.request.GET.get('status', ''),
        }

        return context

class CreateExchangeProposal(View):
    def post(self, request):
        ad_sender_id = request.POST.get('ad_sender_id')
        ad_receiver_id = request.POST.get('ad_receiver_id')
        comment = request.POST.get('comment')

        ad_sender = get_object_or_404(Ad, id=ad_sender_id, user=request.user)
        ad_receiver = get_object_or_404(Ad, id=ad_receiver_id)

        # Создание предложения обмена
        ExchangeProposal.objects.create(
            ad_sender=ad_sender,
            ad_receiver=ad_receiver,
            comment=comment,
            status='pending'
        )

        messages.success(request, "Предложение успешно отправлено!")

        return redirect('exchange_proposal')

class UpdateExchangeProposal(View):
    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, id=pk)
        action = request.POST.get('action')

        if proposal.ad_receiver.user != request.user:
            raise PermissionDenied("Вы не можете изменить это предложение.")

        if action == 'accept':
            proposal.status = 'accepted'
            proposal.ad_sender.is_archived = True
            proposal.ad_receiver.is_archived = True
            proposal.ad_sender.save()
            proposal.ad_receiver.save()
        elif action == 'reject':
            proposal.status = 'rejected'

        proposal.save()
        messages.success(request, "Статус предложения успешно обновлен!")
        return redirect('exchange_proposal')

class ArchiveView(ListView):
    model = Ad
    template_name = 'ads/archive.html'
    context_object_name = 'archived_products'
    paginate_by = 5

    def get_queryset(self):
        return Ad.objects.filter(user=self.request.user, is_archived=True).order_by('-created_at')


def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_400(request, exception):
    return render(request, 'errors/400.html', status=400)