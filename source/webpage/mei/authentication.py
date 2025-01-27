from django.contrib.auth.backends import BaseBackend, UserModel
from django.contrib.auth.models import User


class QQBackend(BaseBackend):
    def authenticate(self, request, username=None, code=None):
        try:
            user = User.objects.get(username=username)
        except UserModel.DoesNotExist:
            # 如果用户不存在，创建一个新的用户
            user = User.objects.create_user(username=username)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
