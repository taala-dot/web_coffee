from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .models import Card, Product
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.models import User
import random
import string


class PurchaseProductView(View):
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)

        if product.stock < 1:
            return JsonResponse({'success': False, 'message': 'Продукт закончился на складе.'}, status=400)

        # Обрабатываем покупку продукта
        product.stock -= 1
        product.save()

        return JsonResponse({'success': True, 'message': 'Продукт успешно куплен.'})


class RegisterCardView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if hasattr(request.user, 'card'):
            return Response({"error": "You already have a registered card."}, status=400)

        # Создание карты
        card = Card(user=request.user)
        card.generate_card_details()
        card.save()

        return Response({
            "message": "Card registered successfully!",
            "card_number": card.card_number,
            "card_password": card.card_password
        }, status=201)


class LinkCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'card'):
            return Response({"error": "You already have a linked card."}, status=status.HTTP_400_BAD_REQUEST)

        card_number = request.data.get("card_number")
        card_password = request.data.get("card_password")

        if not card_number or not card_password:
            return Response({"error": "Card number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        card = Card.objects.create(user=request.user, card_number=card_number, card_password=card_password)
        card.save()

        return Response({"message": "Card linked successfully!"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def purchase_product(request, product_id):
    try:
        card = Card.objects.get(user=request.user)

        if not card.card_number:
            return Response({'error': 'You must link a card to your account before making a purchase.'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=product_id)

        if card.deduct(product.price):
            return Response({'message': f'Product {product.name} purchased successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Not enough balance on your card.'}, status=status.HTTP_400_BAD_REQUEST)

    except Card.DoesNotExist:
        return Response({'error': 'Card not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)


class ProductListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        password_confirm = request.data.get("password_confirm")

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        if password != password_confirm:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        return Response({"message": "User registered successfully. Please verify your email."}, status=status.HTTP_201_CREATED)


class ConfirmEmailView(APIView):
    def post(self, request):
        verification_code = request.data.get("verification_code")
        user_id = request.session.get('user_id')

        if not verification_code or not user_id:
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        if verification_code == request.session.get('verification_code'):
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            return Response({"message": "Your email has been confirmed, you can now log in."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

