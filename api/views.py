from datetime import datetime

from django.contrib.staticfiles.views import serve
from django.db import models
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from .models import Expense
from .serializer import ExpenseSerializer, UserSerializer


# Create your views here.
@api_view(['GET'])
def get_hello(request):
    return Response('Hello world')


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expenses(request):
    expenses = request.user.expense_set.all()
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request, pk):
    try:
        expense = request.user.expense_set.get(pk=pk)
    except Expense.DoesNotExist:
        return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)

    expense.delete()
    return Response({'message': 'Expense deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense_by_category(request):
    category = request.query_params.get('category')
    if not category:
        return Response({'error': 'Category parameter is required'},
                        status=status.HTTP_400_BAD_REQUEST
                        )

    expenses = Expense.objects.filter(user=request.user, category=category)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expenses_by_date_interval(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    if not start_date or not end_date:
        return Response({'error': 'Both start_date and end_date are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if start_date > end_date:
            return Response({'error': 'start_date cannot be later than end_date'},
                            status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                        status=status.HTTP_400_BAD_REQUEST)

    expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_filtered_expenses(request):
    category = request.query_params.get('category')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if category and start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            if start_date > end_date:
                return Response({'error': 'start_date cannot be later than end_date'},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                            status=status.HTTP_400_BAD_REQUEST)

        expenses = Expense.objects.filter(user=request.user, category=category, date__range=[start_date, end_date])

    elif category:
        expenses = Expense.objects.filter(user=request.user, category=category)

    elif start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            if start_date > end_date:
                return Response({'error': 'start_date cannot be later than end_date'},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'},
                            status=status.HTTP_400_BAD_REQUEST)

        expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date])

    else:
        # If no filter is provided, return all expenses
        expenses = Expense.objects.filter(user=request.user)

    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense_percentage_by_category(request):
    expenses = Expense.objects.filter(user=request.user)

    if not expenses.exists():
        return Response(
            {"message": "No expenses found."},
            status=status.HTTP_404_NOT_FOUND
        )
    total_amount = expenses.aggregate(total=models.Sum('amount'))['total']

    category_totals = expenses.values('category').annotate(total=models.Sum('amount'))

    percentages = {
        category_total['category']: round((category_total['total'] / total_amount) * 100, 2)
        for category_total in category_totals
    }
    return Response(
        {
            "total_expense": total_amount,
            "category_percentages": percentages,
        },
        status=status.HTTP_200_OK
    )
