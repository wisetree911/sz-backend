from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.api.deps import get_user_service
from app.services.users import UserService
from app.schemas.user import UserCreate
from app.schemas.auth import Token, RegisterIn, UserPublic
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")



def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), service: UserService = Depends(get_user_service)):
    cred_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = await service.get_by_email(email=email)
    if not user:
        raise cred_exc
    return user

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterIn, service: UserService = Depends(get_user_service)) -> UserPublic:
    existing = await service.get_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = await service.create(
        UserCreate(
            name=payload.name,
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
    )
    return UserPublic(id=user.id, name=user.name, email=user.email)

@auth_router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), service: UserService = Depends(get_user_service)):
    user = await service.get_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="access troubles")

    token = create_access_token(sub=user.email)
    return Token(access_token=token)

@auth_router.get("/me", response_model=UserPublic)
async def me(current_user=Depends(get_current_user)):
    return UserPublic(id=current_user.id, name=current_user.name, email=current_user.email)