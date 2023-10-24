from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext




SECRET_KEY = "3efd0e1c156f8f295ba296929992809754707a85c67ae93f3a234b5f8f6bc25f"

# Cryptographic algorithm used to encode and decode JWTs ....in this case, "HS256" stands for HMAC-SHA256...
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30





# Creating a fake database
db = {
    "Amman": {
        "username": "Amman",
        "full_name": "Amman Chhetri",
        "email": "amman@gmail.com",
        "hashed_password": "$2b$12$0I9vtaQq13zc1umktJy4EeZYOYLXGjcPlzJM0pOcAcLlZzfO.UfOe",
        # disabled = True...signifies person was inactive for long time...
        "disabled": False
    }
}


# Here we are defining pydantic models...pydantic is a library that is used for data-validation and parsing...it allow us to
# define data models with data types and validation rules....

# In simple terms...we define models(user_defined class with Basemodel parameter)..in which we define how data should be 
# structured and what data types are expected for each attribute of this class..whenever we call this class instance.....the 
# name of the model is the name of the class.....
# pydantic will automatically validate the data against the model's structure and data type specifications.
# If the data is valid, Pydantic will create an instance of the model with the provided data....example ....

# class User(BaseModel):
#     username: str
#     email: str
#     age: int

# # Valid data
# valid_data = {
#     "username": "john_doe",
#     "email": "john@example.com",
#     "age": 30
# }

# # Create an instance of the User model
# user1 = User(**valid_data)

# Here the data is in correct format...If the data provided doesn't match the model's structure or contains data of the wrong 
# data types, Pydantic will raise validation errors. This helps ensure that the data you work with is consistent and adheres
# to the specified rules.....

# Whenever we say a  model inherits a pydantic model...it inherits the structure, attributes and the validation rules...here 
# structure means layout of data in the model...like like how the members(varaibles) of the class are arranged...
# attributes means...the member variables and functions we are defining in the class
# validation rules means....it contains the rules like example...data type constraints...or u can define ur custom rules....


# Normal `class` also works....but the pydantic class(models) have various advance features like....automatic data validation....
# error handling and many more.... 


# Here Token class inheriting from BaseModel...which means Token Class can access all the attributes and behaviours 
# (methods/functions) of BaseModel class.....
# Most used methods in pydantic BaseModel class is :
# dict(), json(), parse_obj(), schema(), copy(), etc...


# The primary difference between a normal class and a class defined using Pydantic is the added functionality and features that Pydantic brings to the latter. Here are some key distinctions:
# 1. Automatic Data Validation:
# Pydantic models include automatic data validation. When you define data types and constraints for attributes in a Pydantic model, it ensures that data adheres to those constraints. In contrast, with a normal class, you would need to implement data validation manually.

# 2.Data Parsing:
# Pydantic can automatically parse incoming data into the specified data types. For example, if you expect an integer but receive a string, Pydantic can attempt to parse it to an integer. In a normal class, you would need to handle data parsing yourself.

# 3. Serialization:
# Pydantic models provide built-in methods for converting instances to dictionaries or JSON strings. This is helpful for easily serializing data for responses in web applications or APIs. In a normal class, you would need to implement serialization methods manually.

# 4.Type Hints:
# Pydantic models use type hints to specify the data types of attributes. This improves code readability and allows for better type checking in modern IDEs. Normal classes can also use type hints, but Pydantic enforces them.

# 5. Error Handling:
# Pydantic raises validation errors with meaningful messages when data doesn't meet the defined constraints. This helps in catching and handling errors early in your application. In a normal class, you would need to implement error handling for data validation yourself.

# 6. Documentation:
# Pydantic models are self-documenting and provide clear structure and data type information. This can be beneficial for code documentation and understanding the data structure. Normal classes rely more on comments and documentation to convey data expectations.

# 7. Schema Generation:
# Pydantic can generate JSON Schemas for your data models, which is useful for documentation and data validation in API endpoints. In a normal class, you would need to document the schema separately.

# 8.Integration with Frameworks:
# Many web frameworks, such as FastAPI, work seamlessly with Pydantic models for handling request data, form validation, and generating API documentation.

# Watch this beautiful explaination by @Eric Roby - https://www.youtube.com/watch?v=fCsV3kCOeKc&ab_channel=EricRoby
class Token(BaseModel):
    # this are type hints...that is what values are expected for each attribute...like access_token should be str...token_type
    # should be str...
    access_token: str
    token_type: str


class TokenData(BaseModel):
    # here the username should be of type str or it should be None(referring absence of value)...but as we have also used 
    # '=None' ...which means...if nothing is provided we take default value as 'None'..
    username: str or None = None 
    

class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None
    

class UserInDB(User):
    hashed_password: str
    
    



# defining the configuration for password hashing...which uses `bcrypt` password hashing scheme....deprecated='auto` means...
# deprecated password hashing schemes should be handled automatically....whenever the password hashing scheme becomes deprecated
# or are no longer consider secure...it is important to transition existing hashed passwords to more secure schemes....setting
# 'auto` ....ensures that it happens automatically....
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# defining configuration for OAuth2 Bearer token...tokenUrl specifies the URL...where the client can request access token...
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



app = FastAPI()



# verify that the password enter by user...matches with the password stored in database...using configuration as defined above...
def verify_password(plain_password, hashed_password):    
    return pwd_context.verify(plain_password, hashed_password)



# function to hash a given password...
def get_password_hash(password):
    return pwd_context.hash(password)




# Getting user from the database...if it is present we return the user data ...otherwise return None...
def get_user(db, username: str):
    # If we check our database we have stored the name as a key and the user details as pair...so we will check if we have user
    # with the given name in database or not...if yes we return the details of user.... 
    if username in db:
        user_data = db[username]
        # This ** ensures the data passed inside the UserInDB are key value pairs...and not a ditinonary or JSON etc....
        return UserInDB(**user_data)
    
    

# Authenticating user
def authenticate_user(db, username: str, password: str):
    # Getting the details of the user..we trying to authenticate...
    user = get_user(db, username)
    
    # This check if user is present or not...if the user value is None(returned by get_user() )...then we return False...
    if not user:
        return False
    
    # If the hash of the password entered doesnot matches with the hashed password stored in database...
    if not verify_password(password, user.hashed_password):
        return False
    
    # Otherwise we return true..meaning `Successfull authentication`..
    return user




# Funtion to create access token...the data dictionary is the details(claim) we want from user to create the access token..
def create_access_token(data: dict, expires_delta: timedelta or None = None):
    # Making copy of data dict...
    to_encode = data.copy()
    # If expires_delta has been provided....
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # If it is not provided...we make our own timedelta of 15 minutes
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    
    # adding this key in our to_encode dict....
    to_encode.update({"exp": expire})
    
    # we then encode our dict to a JWT...using the SECRET_KEY and algorithm=ALGORITHM....
    # JWT comprises of three parts....in the order....header, payload and signature....
    # Header contains information about type of token and signing algorithm been used...
    # Payload contains the details like username, and other information you wish to include..
    # Signature is used to verify that the sender of the JWT is who says it is...and to ensure that the message wasn't changed 
    # along the way...Signature is created using header , payload and secret key using a particulat algorithm....
    # So suppose u provided a access token to a client...now client will attach this access token to its request body...
    # everytime it makes a request to the API...so the API first verify that the access token attached is valid or not with the
    # helpe of server...so for this it first extracts the header and payload from the token...and then with the help of its
    # SECRET_KEY ..it make a new token using this header and payload...and if this token matches with the access_token it 
    # recieved from the client....whcih means the access_token is valid ....otherwise not....
    # other checks like expiration_time etc..
    
    # refer this website for better understanding....https://jwt.io/
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




# this function will extract the user from the access token....here the parameter passed on the function get_current_user ie.
# `token`...depends upon the function oauth2_scheme....so whatever value is returned by the oauth2_scheme...is given to the
# parameter token...
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    try:        
        # decoding the access_token...
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Now after decoding the access_token ...the key that stores the username is "sub"...
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)      
    
    except JWTError:
        raise credential_exception
    
    
    
    # If all the try block was successfull and we didn't raised any exception we now execute below code...
    user = get_user(db, username= token_data.username)
    if user is None:
        raise credential_exception
    
    # Now this user has the key-value pairs .....as this user stores the value returned by get_user()...
    return user

    
    


# This function checks if the user is disabled or not....if the person is disabled we dont want them to login....and we raise
# the exception...
async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    
    # if the current_user.disabled is true...which means...user is disabled...and we don't want them to login...
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user




 
# Now defining a token root....if you remember we have defined a URL where the client must go to get the access_token....
# that is at oauth2_scheme...
# This route is what going to be called when we are `signing in`....so this below function gets executed...and generates a 
# access token....and this token can be used by the client for the requests he wants...till the token expires....

# This response_model means...that the respnonse from the endpoint should be automatically converted into JSON object based on 
# Token...
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_Unauthorized, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.username}, expires_delta= access_token_expires)
    
    # Now our response_model is Token...which means this return value will be converted into type Token object(that we defined
    # above)...which will be in JSON format...
    return {"access_token": access_token, "token_type": "bearer"}
    
    
    
    

@app.get("/users/me/", response_model= User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user




@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]





# #To generate the 32 bit random string ...
# openssl rand -hex 32 


# #To run this file 
# #main is this file name
# #app is the name of your application instance of Fast API..

# uvicorn main:app --reload


# #To use Swagger UI
# go to \docs.

# # pwd = get_password_hash("amman123")
# print(pwd)

    

    