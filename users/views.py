from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from .models import User, Event, Registration
from .serializers import EventSerializer, RegistrationSerializer, UserSerializer
from .utils import send_welcome_email


class GoogleSignInView(APIView):
    def post(self, request):
        token = request.data.get('token')
        print("token>>>", token)
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            email = idinfo.get('email')
            name = idinfo.get('name')

            print("idnfo>>>", idinfo)

            # Find or create the user
            try:
                user = User.objects.get(email=email)
                created = False
            except User.DoesNotExist:
                # Create user with email as username
                user = User.objects.create_user(
                    email=email, 
                    username=email,  # Use email as username
                    name=name
                )
                created = True
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "new_user": created
                }
            })
        except ValueError as e:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the Google token first
            token = request.data.get('token')
            if not token:
                return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            token_email = idinfo.get('email')

            # Check if the token email matches the requested email
            if token_email != email:
                return Response({"error": "Token email does not match provided email"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Get the user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update user fields
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        return Event.objects.all().order_by('-start_date', '-start_time')

    def get_serializer_context(self):
        # Pass the current user to the serializer context
        context = super().get_serializer_context()
        
        user = None
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            email = self.request.query_params.get('email')
            if email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None
        
        context['user'] = user
        return context

    def list(self, request, *args, **kwargs):
        # If no user is authenticated, proceed with default list
        if not request.user.is_authenticated:
            return super().list(request, *args, **kwargs)
        
        # Get the queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Serialize with user context
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        # Extract email and other registration details from request
        email = request.data.get('email')
        event_id = request.data.get('event_id')
        no_of_adults = request.data.get('no_of_adults', 0)
        no_of_children_9_13 = request.data.get('no_of_children_9_13', 0)
        no_of_children_3_8 = request.data.get('no_of_children_3_8', 0)
        additional_adults = request.data.get('additional_adults', '')
        additional_kids_9_13 = request.data.get('additional_kids_9_13', '')
        additional_kids_3_8 = request.data.get('additional_kids_3_8', '')
        selected_package = request.data.get('selected_package', '')
        payment_status = request.data.get('payment_status', False)

        # Validate required fields
        if not email or not event_id:
            return Response({
                "error": "Email and event_id are required fields"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "error": f"No user found with email {email}"
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            # Find the event
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                "error": f"No event found with id {event_id}"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if user is already registered for this event
        existing_registration = Registration.objects.filter(user=user, event=event).first()
        if existing_registration:
            return Response({
                "error": "User is already registered for this event"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create registration
        registration = Registration.objects.create(
            user=user,
            event=event,
            no_of_adults=no_of_adults,
            no_of_children_9_13=no_of_children_9_13,
            no_of_children_3_8=no_of_children_3_8,
            additional_adults=additional_adults,
            additional_kids_9_13=additional_kids_9_13,
            additional_kids_3_8=additional_kids_3_8,
            selected_package=selected_package,
            payment_status=payment_status
        )

        # Send welcome email
        try:
            send_welcome_email(user.email, user.name, event.name)
        except Exception as e:
            # Log the error but don't prevent registration from completing
            print(f"Error sending welcome email: {str(e)}")

        # Serialize and return the registration
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
