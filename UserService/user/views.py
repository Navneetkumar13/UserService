from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . models import User
from UserService.enums import ErrorResponseStatus
import datetime
from django.utils import timezone
from follow.models import FollowMap
from cryptography.fernet import Fernet
from UserService.utils import generate_tokens
from rest_framework.permissions import IsAuthenticated, AllowAny


'''
API Type: POST
Description: To Create User with the given payload
'''
class CreateUserAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            name = request.data.get('name', None)
            email = request.data.get('email', None)
            
            if email is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': 400, 'message': 'Please provide valid email id'}, status=status.HTTP_400_BAD_REQUEST)
            email = str(email).lower()
            email_q = User.objects.filter(email=email).first()
            if email_q is not None:
                return Response({'response': ErrorResponseStatus.USER_ALREADY_EXISTS.value, 'code': 400, 'message': 'User with email-id already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            country_code = request.data.get('country_code', None)
            phone_number = request.data.get('phone_number', None)

            password = request.data.get('password', None)
            if password is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': 400, 'message': 'Please provide valid password'}, status=status.HTTP_400_BAD_REQUEST)
                

            # Creating unique username by using unix timestamp
            now = timezone.now()
            current_timestamp = datetime.datetime.timestamp(now)
            username = str(name).replace(' ','_') + '-' + str(current_timestamp).replace('.', '')

            key = Fernet.generate_key()
            fernet = Fernet(key)
            encPassword = fernet.encrypt(password.encode())

            user_obj = User(
                name=name,
                email=str(email).lower(),
                country_code=country_code,
                phone_number=phone_number,
                username=username,
                password = encPassword,
                key = key,
                created_at=now,
                updated_at=now,
            )

            user_obj.save()
            response = {
                "name": user_obj.name,
                "username": user_obj.username,
                "country_code": user_obj.country_code,
                "phone_number": user_obj.phone_number,
                "email": user_obj.email,
                "created_at": user_obj.created_at,
                "updated_at": user_obj.updated_at
            }
            return Response({"response":'Success','code':'201','message':'User Created Successfully','data':response}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


'''
API Type: POST
Description: To Login using email and password
'''
class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email', None)
            if email is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': '400', 'message': 'Please provide valid email id'}, status=status.HTTP_400_BAD_REQUEST)
            
            password = request.data.get('password',None)
            if password is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': '400', 'message': 'Please provide valid password'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(email=email)
            if user is not None:
                fernet = Fernet(bytes(user.key))
                decMessage = fernet.decrypt(bytes(user.password)).decode()
                if decMessage == password:
                    token = generate_tokens(user)
                    return Response({'response':'Success','code':'200','token': token}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'response': ErrorResponseStatus.USER_NOT_FOUND.value, 'code': 404, 'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value ,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



'''
API Type: DELETE
Description: To delete User with the provided unique email
'''
class DeleteUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = User.objects.get(email=request.GET.get('email', ''))
            if user is not None:
                user.delete()
                return Response({'response':'Success','code':'200','message': 'User Deleted Successfully'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'response': ErrorResponseStatus.USER_NOT_FOUND.value, 'code': 404, 'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            #print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value ,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

'''
API Type: GET
Description: To get User with the provided unique username
'''
class GetUserByUsernameAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            username = request.GET.get('username',None)
            if username is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': 400, 'message': 'Please provide valid username'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_obj = User.objects.filter(username=username).first()

            followers_list = []
            followers_q = FollowMap.objects.filter(following = username)
            for follower in followers_q:
                user_check_q = User.objects.filter(username = follower.followee).first()
                if user_check_q is not None:
                    follower_data = {
                        'username':user_check_q.username,
                        'name': user_check_q.name
                    }
                    followers_list.append(follower_data)

            followings_list = []
            followings_q = FollowMap.objects.filter(followee = username)
            for followee in followings_q:
                user_check_q = User.objects.filter(username = followee.following).first()
                if user_check_q is not None:
                    followee_data = {
                        'username':user_check_q.username,
                        'name': user_check_q.name
                    }
                    followings_list.append(followee_data)

            response = {
                "name": user_obj.name,
                "username": user_obj.username,
                "country_code": user_obj.country_code,
                "phone_number": user_obj.phone_number,
                "email": user_obj.email,
                "followers": followers_list,
                "following": followings_list,
                "created_at": user_obj.created_at,
                "updated_at": user_obj.updated_at
            }
            return Response({"response":'Success','code':'200','data':response}, status=status.HTTP_200_OK)
        except Exception as e:
            #print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value ,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

'''
API Type: GET
Description: To get User/Users with the provided name
'''
class GetUserByNameAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            name = request.GET.get('name',None)
            if name is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': 400, 'message': 'Please provide valid name'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_obj = User.objects.filter(name__icontains=name)
            users_list = []
            for user in user_obj:

                followers_list = []
                followers_q = FollowMap.objects.filter(following = user.username)
                for follower in followers_q:
                    user_check_q = User.objects.filter(username = follower.followee).first()
                    if user_check_q is not None:
                        follower_data = {
                            'username':user_check_q.username,
                            'name': user_check_q.name
                        }
                        followers_list.append(follower_data)

                followings_list = []
                followings_q = FollowMap.objects.filter(followee = user.username)
                for followee in followings_q:
                    user_check_q = User.objects.filter(username = followee.following).first()
                    if user_check_q is not None:
                        followee_data = {
                            'username':user_check_q.username,
                            'name': user_check_q.name
                        }
                        followings_list.append(followee_data)

                data = {
                    "name": user.name,
                    "username": user.username,
                    "country_code": user.country_code,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "followers": followers_list,
                    "following": followings_list,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                users_list.append(data)
            return Response({"response":'Success','code':'200','data':users_list}, status=status.HTTP_200_OK)
        except Exception as e:
            #print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value ,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: PUT
Description: To update User with the provided unique username
'''
class UpdateUserAPI(APIView):
    permission_classes = [AllowAny]

    def put(self, request, username):
        try:
            if username is None:
                return Response({'response': ErrorResponseStatus.INVALID_FIELD.value, 'code': 400, 'message': 'Please provide valid username'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_obj = User.objects.filter(username=username).first()
            if user_obj is None:
                return Response({'response': ErrorResponseStatus.USER_NOT_FOUND.value, 'code': 400, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
            name = request.data.get('name',None)
            if name is not None:
                user_obj.name = name
            
            country_code = request.data.get('country_code',None)
            if country_code is not None:
                user_obj.country_code = country_code

            phone_number = request.data.get('phone_number',None)
            if phone_number is not None:
                user_obj.phone_number = phone_number

            user_obj.updated_at = timezone.now()
            user_obj.save()

            follow_user = request.data.get('follow_user', None)
            if follow_user is not None:
                follow_check_q = FollowMap.objects.filter(followee = username, following = follow_user).first()
                if follow_check_q is not None:
                    follow_check_q.delete()
                else:
                    follow_obj = FollowMap(
                        followee = username,
                        following = follow_user
                    )
                    follow_obj.save()

            following_list = []
            following_q = FollowMap.objects.filter(followee = username)
            for following_obj in following_q:
                user_check_q = User.objects.filter(username = following_obj.following).first()
                if user_check_q is not None:
                    following_list.append({"username":user_check_q.username, "name":user_check_q.name})

            data = {
                "name": user_obj.name,
                "username": user_obj.username,
                "country_code": user_obj.country_code,
                "phone_number": user_obj.phone_number,
                "email": user_obj.email,
                "following": following_list,
                "created_at": user_obj.created_at,
                "updated_at": user_obj.updated_at
            }

            return Response({"response":'Success','code':'201','message':'User Updated Successfully','data':data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value ,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

'''
API Type: GET
Description: To get all users list
'''
class GetUsersListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            users = User.objects.all()
            users_list = []
            for user in users:

                followers_list = []
                followers_q = FollowMap.objects.filter(following = user.username)
                for follower in followers_q:
                    user_check_q = User.objects.filter(username = follower.followee).first()
                    if user_check_q is not None:
                        follower_data = {
                            'name':user_check_q.username,
                            'username': user_check_q.name
                        }
                        followers_list.append(follower_data)

                followings_list = []
                followings_q = FollowMap.objects.filter(followee = user.username)
                for followee in followings_q:
                    user_check_q = User.objects.filter(username = followee.following).first()
                    if user_check_q is not None:
                        followee_data = {
                            'name':user_check_q.username,
                            'username': user_check_q.name
                        }
                        followings_list.append(followee_data)

                data = {
                    "name": user.name,
                    "username": user.username,
                    "country_code": user.country_code,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "followers": followers_list,
                    "following": followings_list,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                users_list.append(data)

            return Response({"response":'Success','code':'201','data':users_list}, status=status.HTTP_200_OK)
        except Exception as e:
            #print("Exception: ",e)
            return Response({"response":ErrorResponseStatus.INTERNAL_SERVER_ERROR.value ,'code':'500','message':'Error Occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
