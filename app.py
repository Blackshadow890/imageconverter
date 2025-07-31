from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from PIL import Image
import os
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret"  # session বা flash এর জন্য দরকার
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # ম্যাক্স 8MB আপলোড (পরিবর্তন করতে পারেন)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return '.' in filename and ext in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_image():
    file = request.files.get('image')
    conversion_type = request.form.get('conversion_type')

    if not file or not conversion_type:
        flash("ফাইল বা conversion type মিসিং ।")
        return redirect(url_for('index'))

    if file.filename == '' or not allowed_file(file.filename):
        flash("অবৈধ ফাইল টাইপ। অনুমোদিত: png, jpg, jpeg, webp, bmp")
        return redirect(url_for('index'))

    try:
        img = Image.open(file)
    except Exception:
        flash("ইমেজ ওপেন করতে সমস্যা হয়েছে।")
        return redirect(url_for('index'))

    # কোন ফরম্যাট থেকে যাই না কেন, RGB তে রূপান্তর করলে compatibility বেশি থাকে (বিশেষ করে JPEG এর জন্য)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    output = BytesIO()
    original_name = secure_filename(file.filename.rsplit('.', 1)[0])
    filename = f"{original_name}_converted"

    if conversion_type == 'png_to_jpg':
        img.save(output, format='JPEG', quality=90)
        output.seek(0)
        return send_file(output,
                         as_attachment=True,
                         download_name=f"{filename}.jpg",
                         mimetype='image/jpeg')

    elif conversion_type == 'jpg_to_png' or conversion_type == 'bmp_to_png':
        img.save(output, format='PNG')
        output.seek(0)
        return send_file(output,
                         as_attachment=True,
                         download_name=f"{filename}.png",
                         mimetype='image/png')

    elif conversion_type == 'webp_to_jpg':
        img.save(output, format='JPEG', quality=90)
        output.seek(0)
        return send_file(output,
                         as_attachment=True,
                         download_name=f"{filename}.jpg",
                         mimetype='image/jpeg')

    elif conversion_type == 'jpg_to_pdf':
        # Pillow PDF conversion expects RGB
        img.save(output, format='PDF')
        output.seek(0)
        return send_file(output,
                         as_attachment=True,
                         download_name=f"{filename}.pdf",
                         mimetype='application/pdf')

    else:
        flash("Conversion type supported নয়।")
        return redirect(url_for('index'))

# Error handler for too large uploads
@app.errorhandler(413)
def too_large(e):
    return "ফাইল খুব বড়। সীমা ৮MB.", 413

if __name__ == '__main__':
    app.run(debug=True)
