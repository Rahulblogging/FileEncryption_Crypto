from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import io
import zipfile
import os

app = Flask(__name__)


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

    # read original file
    original = uploaded_file.read()

    # generate unique key
    key = Fernet.generate_key()

    # create fernet object
    fernet = Fernet(key)

    # encrypt file
    encrypted = fernet.encrypt(original)

    # filenames
    encrypted_filename = uploaded_file.filename + ".enc"
    key_filename = uploaded_file.filename + ".key"

    # create ZIP in memory
    memory_file = io.BytesIO()

    with zipfile.ZipFile(
        memory_file,
        'w',
        zipfile.ZIP_DEFLATED
    ) as zf:

        zf.writestr(encrypted_filename, encrypted)
        zf.writestr(key_filename, key)

    memory_file.seek(0)

    # return zip download
    return send_file(
        memory_file,
        as_attachment=True,
        download_name='encrypted_files.zip',
        mimetype='application/zip'
    )


# DECRYPT ROUTE
@app.route('/decrypt', methods=['POST'])
def decrypt_file():

    uploaded_zip = request.files['file']

    if uploaded_zip.filename == '':
        return "No ZIP File Selected!"

    try:

        # read uploaded zip in memory
        zip_data = io.BytesIO(uploaded_zip.read())

        with zipfile.ZipFile(zip_data, 'r') as zf:

            encrypted_filename = None
            key_filename = None

            # find files
            for file in zf.namelist():

                if file.endswith('.enc'):
                    encrypted_filename = file

                elif file.endswith('.key'):
                    key_filename = file

            if not encrypted_filename or not key_filename:
                return "ZIP must contain .enc and .key files!"

            # read encrypted file
            encrypted_data = zf.read(encrypted_filename)

            # read key file
            key = zf.read(key_filename)

        # create fernet object
        fernet = Fernet(key)

        # decrypt
        decrypted = fernet.decrypt(encrypted_data)

        # restore original filename
        original_filename = encrypted_filename.replace(".enc", "")

        # return decrypted file
        return send_file(
            io.BytesIO(decrypted),
            as_attachment=True,
            download_name=original_filename
        )

    except:
        return "Invalid ZIP File!"


# RUN APP
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host='0.0.0.0',
        port=port
    )