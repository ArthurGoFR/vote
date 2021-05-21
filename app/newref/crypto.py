from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def test(ref):

    cipher = PKCS1_OAEP.new(RSA.importKey(ref.public_key.read()))
    

    # key = RSA.generate(2048)
    # private_key = key.export_key()
    # print(private_key.decode())

    # ref.public_key = key.publickey().export_key().decode()
    # ref.save()

    # cipher = PKCS1_OAEP.new(RSA.importKey(ref.public_key))
    # ciphertext = cipher.encrypt(data_enc)

    # # print(ciphertext)

    # cipher = PKCS1_OAEP.new(RSA.importKey(private_key))
    # message = cipher.decrypt(ciphertext)

    # print(message.decode())

    # private_key="-----BEGIN RSA PRIVATE KEY-----
    # cipher = PKCS1_OAEP.new(RSA.importKey(private_key.encode("utf-8")))
