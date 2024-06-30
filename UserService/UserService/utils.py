from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['name'] = user.name
    refresh['email'] = user.email
    return {
        # 'refresh': str(refresh),
        'access': str(refresh.access_token)
    }