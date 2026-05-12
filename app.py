from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import base64
import hashlib
import io
import os

app = Flask(__name__)


# GENERATE KEY FROM PASSWORD
def generate_key(password):

    # convert password into 32-byte key
    key = hashlib.sha256(password.encode()).digest()

    # convert into Fernet-compatible key
    return base64.urlsafe_b64encode(key)


# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# ENCRYPT ROUTE
@app.route('/encrypt', methods=['POST'])
def encrypt_file():

    uploaded_file = request.files['file']
    password = request.form['password']

    if uploaded_file.filename == '':
        return "No File Selected!"

    if password == '':
        return "Password Required!"

    # read original file
    original = uploaded_file.read()

    # generate key from password
    key = generate_key(password)

    # create fernet object
    fernet = Fernet(key)

    # encrypt file
    encrypted = fernet.encrypt(original)

    # encrypted filename
    encrypted_filename = uploaded_file.filename + ".enc"

    # return encrypted file
    return send_file(
        io.BytesIO(encrypted),
        as_attachment=True,
        download_name=encrypted_filename
    )


# DECRYPT ROUTE
@app.route('/decrypt', methods=['POST'])
def decrypt_file():

    encrypted_file = request.files['file']
    password = request.form['password']

    if encrypted_file.filename == '':
        return "No File Selected!"

    if password == '':
        return "Password Required!"

    try:

        # read encrypted file
        encrypted_data = encrypted_file.read()

        # generate key from password
        key = generate_key(password)

        # create fernet object
        fernet = Fernet(key)

        # decrypt
        decrypted = fernet.decrypt(encrypted_data)

        # restore original filename
        original_filename = encrypted_file.filename.replace(".enc", "")

        # return decrypted file
        return send_file(
            io.BytesIO(decrypted),
            as_attachment=True,
            download_name=original_filename
        )

    except:
        return "Wrong Password or Invalid File!"


# RUN APP
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )