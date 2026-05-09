from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

# folders
UPLOAD_FOLDER = "uploads"
ENCRYPTED_FOLDER = "encrypted"
DECRYPTED_FOLDER = "decrypted"
KEY_FOLDER = "keys"

# create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)
os.makedirs(KEY_FOLDER, exist_ok=True)


# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# ENCRYPT ROUTE
@app.route('/encrypt', methods=['POST'])
def encrypt_file():

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return "No File Selected!"

    # save uploaded file
    filepath = os.path.join(
        UPLOAD_FOLDER,
        uploaded_file.filename
    )

    uploaded_file.save(filepath)

    # generate UNIQUE key for this file
    key = Fernet.generate_key()

    # create fernet object
    fernet = Fernet(key)

    # key filename
    key_filename = uploaded_file.filename + ".key"

    # save key file
    key_path = os.path.join(
        KEY_FOLDER,
        key_filename
    )

    with open(key_path, 'wb') as key_file:
        key_file.write(key)

    # read original file
    with open(filepath, 'rb') as file:
        original = file.read()

    # encrypt file
    encrypted = fernet.encrypt(original)

    # encrypted filename
    encrypted_filename = uploaded_file.filename + ".enc"

    encrypted_path = os.path.join(
        ENCRYPTED_FOLDER,
        encrypted_filename
    )

    # save encrypted file
    with open(encrypted_path, 'wb') as enc_file:
        enc_file.write(encrypted)

    return render_template(
        "success.html",
        message="File Encrypted Successfully!"
    )


# DECRYPT ROUTE
@app.route('/decrypt', methods=['POST'])
def decrypt_file():

    encrypted_file = request.files['file']

    if encrypted_file.filename == '':
        return "No File Selected!"

    # save encrypted uploaded file
    encrypted_path = os.path.join(
        UPLOAD_FOLDER,
        encrypted_file.filename
    )

    encrypted_file.save(encrypted_path)

    # corresponding key filename
    key_filename = encrypted_file.filename.replace(".enc", ".key")

    key_path = os.path.join(
        KEY_FOLDER,
        key_filename
    )

    # check if key exists
    if not os.path.exists(key_path):
        return render_template(
            "success.html",
            message="Key File Not Found!"
        )

    # read key
    with open(key_path, 'rb') as key_file:
        key = key_file.read()

    # create fernet object
    fernet = Fernet(key)

    # read encrypted file
    with open(encrypted_path, 'rb') as enc_file:
        encrypted = enc_file.read()

    try:

        # decrypt
        decrypted = fernet.decrypt(encrypted)

        # restore original filename
        original_filename = encrypted_file.filename.replace(".enc", "")

        decrypted_path = os.path.join(
            DECRYPTED_FOLDER,
            original_filename
        )

        # save decrypted file
        with open(decrypted_path, 'wb') as dec_file:
            dec_file.write(decrypted)

        return render_template(
            "success.html",
            message="File Decrypted Successfully!"
        )

    except:
        return render_template(
            "success.html",
            message="Invalid File or Wrong Key!"
        )


# RUN APP
if __name__ == '__main__':
    app.run(debug=True)