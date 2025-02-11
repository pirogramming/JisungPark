from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.timezone import now


class UserManager(BaseUserManager):
    def create_user(self, email, phonenumber, username, password):
        if not email:
            raise ValueError("이메일 주소가 필요합니다.")
        if not phonenumber:
            raise ValueError("전화번호가 필요합니다.")

        user = self.model(
            email=self.normalize_email(email),
            phonenumber=phonenumber,
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phonenumber, username, password):
        user = self.create_user(
            email=email,
            phonenumber=phonenumber,
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True  # 관리자 페이지 접근 가능
        user.is_superuser = True  # 모든 권한 부여
        user.save(using=self._db)
        return user

    def delete_user(self, user_id):
        try:
            user = self.get(id=user_id)  # ID로 사용자 조회
            user.delete()  # 삭제
            return True
        except self.model.DoesNotExist:
            return False  # 사용자가 존재하지 않음



class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="이메일",
        max_length=255,
        unique=True,
    )
    phonenumber = models.CharField(max_length=15)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # 관리자 페이지 접근 가능
    is_admin = models.BooleanField(default=False)  # 관리자 계정
    is_superuser = models.BooleanField(default=False)  # 모든 권한 부여
    created_at = models.DateTimeField(default=now) 
    last_login = models.DateTimeField(blank=True, null=True)
    
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phonenumber"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
      return True

    def has_module_perms(self, app_label):
        return True
      
    # @property
    # def is_staff(self):
    #     return self.is_admin