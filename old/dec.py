from cryptography.fernet import Fernet

# opening the key
with open('filekey.key', 'rb') as filekey:
    key = filekey.read()

# using the key
fernet = Fernet(key)

# opening the encrypted file
with open('maths.encrypted', 'rb') as enc_file:
    encrypted = enc_file.read()

# decrypting the file
decrypted = fernet.decrypt(encrypted)

# opening the file in write mode
with open('maths.decrypted.pdf', 'wb') as dec_file:
    dec_file.write(decrypted)

print("File decrypted successfully!")