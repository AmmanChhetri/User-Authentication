# User-Authentication
Authenticating Users quickly with the help of FAST-API and Token Authentication


# IMPORTANT !!
- I have created a fake database with data of only 1 user...you can integrate a database to store the values of multiple Users.
- Also I have used Swagger UI of FAST-API....for a better understanding and Demonstration.
- You can take the username and password  from the user while signing him/her up in frontend....and if the username and password match with the username & password stored in the database....the User will be provided the access Token.
- Then for each request user needs to attach this access token to get a response.



# Video Demonstration - 
1. I have used the OpenSSL to generate the SECRET_KEY
2. Observe I haven't stored the hashed password for the user with username = "Amman"...that's why it doesn't matter what password you use to authorize it won't authenticate...
3. Then suppose I am manually storing the password for the time being....let's say the password is "amman123"...then our database will store the hash value of this password...so I have hashed this password using the specific algorithm.
4. Then if I use this password while logging in ...it will authenticate....and we will be given the access Token.
5. Then after this I demonstrated the other things you can do with this code.




😊⭐
