from rest_framework import generics,permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser,FileUploadParser
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CMS_UsersSerializer, ChangePasswordSerializer,RegisterAdminSerializer,UpdateUserSerializer,ResetPasswordEmailRequestSerializer,SetNewPasswordSerializer, PaymentEmailRequestSerializer, SendCompletionEmailSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import Util
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
CMS_Users = get_user_model()
import environ

env = environ.Env()
environ.Env.read_env()
class UserProfileAPI(generics.RetrieveAPIView):
    serializer_class = CMS_UsersSerializer
    permissions_class= [permissions.IsAuthenticated,]
    
    def get_object(self):
        if(self.request.user):
            return self.request.user
        
class UpdateUserProfileAPI(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permissions_class= [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser,FormParser,FileUploadParser]
    
    def get_object(self):
        if(self.request.user):
            return self.request.user
    

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permissions_class= [permissions.IsAuthenticated,]
    
    def get_object(self):
        if(self.request.user):
            return self.request.user
        
class RegisterAdminAPI(generics.GenericAPIView):
    serializer_class = RegisterAdminSerializer
    permissions_classes =[permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser,FormParser,FileUploadParser]

    def post(self,request,format=None,*args,**kwargs,):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()
        return Response({"user":CMS_UsersSerializer(user,context=self.get_serializer_context()).data,"status":status.HTTP_201_CREATED})

class BlacklistTokenUpdateView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        email = request.data.get('email', '')
        if CMS_Users.objects.filter(email=email).exists():
            user = CMS_Users.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            frontendurl = env('FRONTEND_URL')
            reset_url = f'{frontendurl}/setpassword/{uidb64}/{token}'
            email_body = f'Dear {user.username},\n Use link below to reset your password  \n' + \
                reset_url
            data = {'email_body': email_body, 'to_email': email,
                    'email_subject': 'Reset your Classy account passsword'}
            Util.send_email(data)
            return Response({'success': 'We have sent you a link to reset your password. ' + reset_url }, status=status.HTTP_200_OK)
        else:
            return Response({'not found': 'No such user exits with given email address'}, status=status.HTTP_404_NOT_FOUND)
        
class RequestPaymentEmail(generics.GenericAPIView):
    serializer_class = PaymentEmailRequestSerializer

    def post(self, request):
        email = request.data.get('email', '')
        quantity = request.data.get('quantity', 0)
        result = request.data.get('result', 0)
        if CMS_Users.objects.filter(email=email).exists():
            user = CMS_Users.objects.get(email=email)
            # Giả định rằng giá mỗi lớp là 10 đơn vị tiền tệ
            amount = int(quantity) * 10
            # payment_url = f'https://payment.example.com/?amount={amount}'
            email_body = f'Dear {user.username},\n This is the invoice for your purchase of {quantity} classes. \n Total payment required is ${result} \n\n Please complete your payment by transferring money to our account below \n Account number : 1013025886 \n Bank name: Vietcombank \n Account owner name: Duong Dong Duong \n\n Thank you for choosing Classy as your class management platform. Have a nice day.   '
            Util.send_payment_email({
    'to_email': email,  # email của người nhận từ request
    'email_subject': f'{user.username}, your order had been placed successfully',
    'email_body': email_body,  # Nội dung email bạn muốn gửi
})
            return Response({'success': f'Payment instructions have been sent to {email}.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No user exists with the provided email address'}, status=status.HTTP_404_NOT_FOUND)
        
    


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = CMS_Users.objects.get(id=id)
            if PasswordResetTokenGenerator().check_token(user, token):
                return Response({'success': True, 'message': 'Valid token'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': True, 'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)
class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        try:
            uidb64 = request.data.get('uidb64','')
            id = smart_str(urlsafe_base64_decode(uidb64))
            email = CMS_Users.objects.filter(id=id).values('email')
            user_email = list(email)[0].get('email')
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            email_body = f'Password Reset Successfull,\n Your password has been sucessfully changed. \n' 
            data = {'email_body': email_body, 'to_email': user_email,
                        'email_subject': 'Your Account: Reset passsword success.'}
            Util.send_email(data)
            return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': True, 'message': 'Password reset failure'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class SendCompletionEmail(APIView):
    serializer_class = SendCompletionEmailSerializer
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        credit = request.data.get('credit')

        # Giả định bạn đã có một hàm setup để gửi email
        # Bạn cần điền thông tin thích hợp vào đây
        Util.send_payment_email({
            'to_email': email,
            'email_subject': 'We have added the classes to your account',
            'email_body': f'We have received your ${credit} payment. The class has been added to your account. Thank you for using Classy services.',
        })

        return Response({'message': 'Email sent successfully'}, status=status.HTTP_200_OK)