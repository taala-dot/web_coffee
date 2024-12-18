from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ProductSerializer, RegisterSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Card, Product, UserProfile,Cart,CartItem,ProductPurchase
from django.views import View
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from rest_framework.views import APIView
from .models import Entity
from .serializers import EntitySerializer
from .pagination import CustomPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class EntityListView(APIView):
    def get(self, request):
        entities = Entity.objects.all()
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(entities, request)
        serializer = EntitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PurchaseProductView(View):
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)

        if product.stock < 1:
            return JsonResponse({'success': False, 'message': 'Продукт закончился на складе.'}, status=400)

        product.stock -= 1
        product.save()

        return JsonResponse({'success': True, 'message': 'Продукт успешно куплен.'})


class RegisterCardView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if hasattr(request.user, 'card'):
            return Response({"error": "You already have a registered card."}, status=400)

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
        paginator = CustomPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            code = ''.join(random.choices(string.digits, k=6))
            profile.verification_code = code
            profile.save()
            try:
                sent_count = send_mail(
                    'Email verification',
                    f'Your verification code is: {code}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )

            except Exception as e:
                print("Ошибка при отправке письма:", e)
                return Response({"error": "Failed to send verification email."}, status=500)
            print("Generated verification code:", code)

            if sent_count == 1:
                return Response({"message": "User registered successfully. Please verify your email."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to send verification email."}, status=500)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')

        if not email or not verification_code:
            return Response({"error": "Email and verification code are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return Response({"error": "Invalid email or user not found"}, status=status.HTTP_400_BAD_REQUEST)

        if profile.verification_code == verification_code:
            user.is_active = True
            user.save()
            profile.is_verified = True
            profile.verification_code = None
            profile.save()

            return Response({"message": "Your email has been confirmed, you can now log in."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return Response({"message": f"{product.name} added to cart."}, status=200)
@api_view(['POST'])
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        cart_item.delete()

    return Response({"message": f"{product.name} removed from cart."}, status=200)
@api_view(['GET'])
def view_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = [{"product": item.product.name, "quantity": item.quantity, "price": item.product.price} for item in cart.items.all()]
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())

    return Response({"items": items, "total_price": total_price}, status=200)


@api_view(['POST'])
def purchase_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    card = get_object_or_404(Card, user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart.items.all())

    if card.balance < total_price:
        return Response({"error": "Not enough balance on your card."}, status=400)

    for item in cart.items.all():
        if item.product.stock < item.quantity:
            return Response({"error": f"Not enough stock for {item.product.name}."}, status=400)

    # Покупка и создание записей
    for item in cart.items.all():
        item.product.stock -= item.quantity
        item.product.save()
        ProductPurchase.objects.create(user=request.user, product=item.product)

    card.deduct(total_price)
    cart.items.all().delete()  # Очистить корзину после покупки

    return Response({"message": "Cart purchased successfully!"}, status=200)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
