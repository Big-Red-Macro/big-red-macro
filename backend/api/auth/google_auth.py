import os
import logging
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    """
    Accept a Google credential (ID token) from the frontend,
    verify it, and return JWT access + refresh tokens.
    Also returns the user's name and email for display.
    """
    credential = request.data.get("credential")
    if not credential:
        return Response(
            {"detail": "Google credential is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID is not configured.")
        return Response(
            {"detail": "Google sign-in is not configured on the server."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError as e:
        logger.warning(f"Google token verification failed: {e}")
        return Response(
            {"detail": "Invalid Google token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    email = idinfo.get("email", "")
    first_name = idinfo.get("given_name", "")
    last_name = idinfo.get("family_name", "")
    picture = idinfo.get("picture", "")

    # Use email as Django username (truncated to 150 chars)
    username = email[:150]

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        },
    )

    if not created:
        # Update name in case it changed
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])

    # Issue JWTs
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "picture": picture,
            },
        },
        status=status.HTTP_200_OK,
    )
