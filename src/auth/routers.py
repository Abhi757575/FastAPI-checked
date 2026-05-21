from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from src import config
from src.auth.schemas import UserCreateModel
from src.db.main import get_session
from .service import UserService
from src.db.main import get_session
from typing import List
from datetime import datetime
from src.auth.schemas import PasswordResetConfirmModel, PasswordResetRequestModel
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserModel, UserLoginModel, UserBooksModel
from .utils import create_access_token, decode_token, generate_password_hash, verify_password, create_url_safe_token, decode_url_safe_token
from .schemas import UserLoginModel, EmailModel, UserCreateModel
from src.config import Config
from datetime import timedelta
from fastapi.responses import JSONResponse
from src.db.redis import add_jti_to_blocklist
from typing import Any, List
from src.db.models import User
from src.mail import mail, create_message
from src.errors import UserAlreadyExistsException, UserNotFoundException
from src.celery_tasks import send_email, send_mail


REFRESH_TOKEN_EXPIRY = 2

auth_Router = APIRouter()
user_Service = UserService()
role_Checker = RoleChecker(['admin', 'user'])


@auth_Router.post('/send_mail')
async def send_mail(email: EmailModel):
    emails = email.addresses

    html = "<H1>Hello, Welcome to the app</H1>"
    subject = "Welcome to the app"

    send_email.delay(emails, subject, body=html)

    return {
        "message" : "Mail Sent Successfully"
    }

@auth_Router.post(
        "/signup",
        response_model=UserModel,
        status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreateModel, 
                              bg_tasks: BackgroundTasks,
                              session: AsyncSession = Depends(get_session)):
    email = user_data.email

    user_exists = await user_Service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExistsException()
    
    new_user = await user_Service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.Domain}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1> Verify your Email </h1>
    <p> Please click the link below to verify your email address and activate your account:
    <a href="{link}">Verify Email</a>
    </p>
    """
    emails = [email]
    subject = "Verify Your Email Address"


    send_mail.delay(emails, subject, body=html_message)


    '''message = create_message(
        recipients=[email],
        subject="Verify Your Email Address",
        body=html_message
    )
    #await mail.send_message(message)
    bg_tasks.add_task(mail.send_message, message)
    '''

    return {
        "message" : "User Created Successfully. Please check your email to verify your account.",
        "user" : new_user
    }


@auth_Router.get('/verify/{token}')
async def verify_user_account(token:str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    
    user_email = token_data.get("email")

    if user_email:
        user = await user_Service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundException()   

        await user_Service.get_user_by_email(user_email,session)

        return JSONResponse(
            content={
                "message" : "Account verified successfully"
            },
            status_code=status.HTTP_200_OK
        )  
    
    return JSONResponse(
        content={
            "message" : "Error Occurred During Account Verification"
        },
        status_code=status.HTTP_5_00_INTERNAL_SERVER_ERROR
    )
    


@auth_Router.post("/login")
async def login_user(login_data:UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_Service.get_user(email, session)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user is not None:
        is_password_valid = verify_password(password, user.password_hash)

        if is_password_valid:
            access_token = create_access_token(
                data={
                  "user_uid" : str(user.uid), "role": user.role
               }
            )

            refresh_token = create_access_token(
               data={
                  "user_uid" : str(user.uid)
               },
               refresh = True,
               expiry = timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    "message":"Login Successfull",
                    "access_token" : access_token,
                    "refresh_token" : refresh_token,
                    "user" : {
                        "email" : user.email,
                        "uid" : str(user.uid),

                    }
                }
            )

        raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Invalid Email Or Password"
        )
    

@auth_Router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer)):
    expiry_timestamp = token_details['exp']
    #print(expiry_timestamp)

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data = token_details['user']
        )

        return JSONResponse(content={
            "access_token": new_access_token
        })
    
    raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

@auth_Router.get('/me', response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user), _bool=Depends(role_Checker)):
    return user



@auth_Router.get('/logout')
async def revoke_token(token_details: dict=Depends(AccessTokenBearer())):
    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message" : " Logged Out Successfully"
        },
        status_code= status.HTTP_200_OK
    )


@auth_Router.post('/password-reset-request')
async def password_reset_request(email_model: PasswordResetRequestModel):
    email = email_model.email

    token = create_url_safe_token({"email":email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Password Reset Request</h1>
    <p>Please click the link below to reset your password:</p>
    <a href="{link}">Reset Password</a>
    """

    subject = "Password Reset Request"

    send_mail.delay(
        [email],
        subject,
        html_message
    )
    return JSONResponse(
        content={
            "message": "Please Check your email for instructions to reset your password"
        },
        status_Code= status.HTTP_200_OK
    )

@auth_Router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token:str,
    passwords : PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session)
):
    new_password = passwords.new_password
    confirm_new_password = passwords.confirm_new_password

    if new_password != confirm_new_password:
        raise HTTPException(
            detail = "Passwords do not match",
            status_code = status.HTTP_400_BAD_REQUEST
        )
    
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_Service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFoundException()
        
        passwd_hash = generate_password_hash(new_password)
        await user_Service.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={ "message": "Password reset successful"},
            status_code=status.HTTP_200_OK
        )
    
    return JSONResponse(
        content = { "message": "Error occurred during password reset"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

    )