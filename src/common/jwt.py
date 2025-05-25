import jwt
import time


from src.custom_types.jwt import Token

class JWT:
    def __init__(self, secret: str):
        self.secret = secret
        self.duration = 60 * 60
        self.algorithm = 'HS256'

    def encode(self, username: str) -> str:
        payload = {
            'username': username,
            'exp': int(time.time()) + self.duration
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode(self, token: str) -> Token:
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])


# if __name__ == "__main__":
#     sample_jwt = JWT("random")

#     encoded_token = sample_jwt.encode("testuser")
#     print(f"Encoded Token: {encoded_token}")

#     decoded_payload = sample_jwt.decode(encoded_token)
#     print(f"Decoded Payload: {decoded_payload}")

#     # Set duration to 2 and wait for 5 seconds to ensure the token is valid
#     time.sleep(5)
#     expired_decoded_payload = sample_jwt.decode(encoded_token)
#     print(f"Expired Decoded Payload: {expired_decoded_payload}")