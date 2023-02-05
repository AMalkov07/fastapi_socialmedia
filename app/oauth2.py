from jose import JWTError, jwt
from datetime import datetime, timedelta

# for authentication we are using a jwt token. The token will contain a header (metadata), a payload (we can chooes any payload), and a signature (the signature will be a hash of the header, the payload, and our secret password)
# Note: the token itself is not encrypted and anyone can see the header and payload (6:46 in vod for details)

# SECRET_KEY can be any string (prefferably long and randomely generated)
SECRET_KEY = "supersecretkey"

# the algorithm will be used to create our signature by hashing the header, payload, and secret key
ALGORITHM = "HS256"

# we need to privde an expiration time for the token so that users have to sometimes relog in
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# the data variable will contain the payload that we want the token to carry (in a dictionary format)
def create_access_token(data: dict):
    # we manipulate the data so we create a copy of it so that we can see the original if needed
    to_encode = data.copy()

    # for the expiration time, we have ot privide the exact time at which this token will expire (we do this by taking the current time and then adding the amount of minutes that we want to token to live b4 expiring)
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # we want the xpiration time to be part of the payload in our token so we add it to the to_encode dictionary
    to_encode.update({"exp": expire})
    
    # this function creates a jwt token, the first argument is the payload, the 2nd is the secret key, the 3rd is the algorithm we want to use
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token