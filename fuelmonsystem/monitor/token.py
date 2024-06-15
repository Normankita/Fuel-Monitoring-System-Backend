from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

user = get_user_model()

def get_user_token(user: user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)