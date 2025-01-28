from rest_framework import serializers
from .models import Event, Registration, User

class EventSerializer(serializers.ModelSerializer):
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_is_registered(self, obj):
        # Get the user from the context (passed from the view)
        user = self.context.get('user')
        
        # If no user is provided, return False
        if not user:
            return False
        
        # Check if the user has a registration for this event
        return Registration.objects.filter(user=user, event=obj).exists()

class RegistrationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    city = serializers.CharField(source='user.city', read_only=True)
    state = serializers.CharField(source='user.state', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'user_name', 
            'email', 
            'city', 
            'state', 
            'phone', 
            'no_of_adults', 
            'no_of_children', 
            'additional_adults', 
            'additional_kids', 
            'registration_date',
            'payment_status'
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
