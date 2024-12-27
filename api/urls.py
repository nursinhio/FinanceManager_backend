from django.urls import path, include
from .views import *

urlpatterns = [
    path('hello/', get_hello, name='get_hello'),
    path('register/', register_user, name='register'),
    path('login/', include('dj_rest_auth.urls')),
    path('expenses/', list_expenses, name='list_expenses'),
    path('expenses/create/', create_expense, name='create_expense'),
    path('expenses/<int:pk>/delete/', delete_expense, name='delete_expense'),
    path('expenses/interval/', get_expenses_by_date_interval, name='get_expenses_by_date_interval'),
    path('expenses/category/', get_expense_by_category, name='get_expense_by_category'),
    path('expenses/filter', get_filtered_expenses, name='get_filtered_expenses'),
    path('expenses/category/percentage/', get_expense_percentage_by_category, name='get_expense_percentage_by_category')
]
