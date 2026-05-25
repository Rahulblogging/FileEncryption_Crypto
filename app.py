from flask import Flask, render_template, request, send_file, redirect
from cryptography.fernet import Fernet

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import base64
import io
import os

app = Flask(__name__)


# GENERATE KEY USING PBKDF2 + SALT
def generate_key(password, salt):

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(
        kdf.derive(password.encode())
    )

    return key


# HOME PAGE
@app.route('/')
def home():

    message = request.args.get("message")
    status = request.args.get("status")

    return render_template(
        'index.html',
        message=message,
        status=status
    )


# ENCRYPT ROUTE
@app.route('/encrypt', methods=['POST'])
def encrypt_file():

    uploaded_file = request.files['file']
    password = request.form['password']

    if uploaded_file.filename == '':
        return redirect('/?message=No File Selected!&status=error')

    if password == '':
        return redirect('/?message=Password Required!&status=error')

    # READ ORIGINAL FILE
    original = uploaded_file.read()

    # GENERATE RANDOM SALT
    salt = os.urandom(16)

    # GENERATE SECURE KEY
    key = generate_key(password, salt)

    # CREATE FERNET OBJECT
    fernet = Fernet(key)

    # ENCRYPT FILE
    encrypted = fernet.encrypt(original)

    # STORE SALT WITH ENCRYPTED DATA
    encrypted = salt + encrypted

    # ENCRYPTED FILENAME
    encrypted_filename = uploaded_file.filename + ".secure"

    # RETURN ENCRYPTED FILE
    return send_file(
        io.BytesIO(encrypted),
        as_attachment=True,
        download_name=encrypted_filename,
        mimetype='application/octet-stream'
    )


# DECRYPT ROUTE
@app.route('/decrypt', methods=['POST'])
def decrypt_file():

    encrypted_file = request.files['file']
    password = request.form['password']

    if encrypted_file.filename == '':
        return redirect('/?message=No File Selected!&status=error')

    if password == '':
        return redirect('/?message=Password Required!&status=error')

    try:

        # READ ENCRYPTED FILE
        encrypted_data = encrypted_file.read()

        # EXTRACT SALT
        salt = encrypted_data[:16]

        # EXTRACT ENCRYPTED CONTENT
        encrypted_content = encrypted_data[16:]

        # GENERATE SAME KEY
        key = generate_key(password, salt)

        # CREATE FERNET OBJECT
        fernet = Fernet(key)

        # DECRYPT
        decrypted = fernet.decrypt(encrypted_content)

        # RESTORE ORIGINAL FILENAME
        original_filename = encrypted_file.filename.replace(".secure", "")

        # RETURN DECRYPTED FILE
        return send_file(
            io.BytesIO(decrypted),
            as_attachment=True,
            download_name=original_filename,
            mimetype='application/octet-stream'
        )

    except:

        return redirect(
            '/?message=Wrong Password or Invalid File!&status=error'
        )


# RUN APP
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host='0.0.0.0',
        port=port
    )