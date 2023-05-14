from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance, ImageFilter
import os
import io
from pydub import AudioSegment
import pydub

# pydub.AudioSegment.converter = (
#     "C:/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
# )

app = Flask(__name__)

# View Route
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/image-processing")
def view_img_processing():
    return render_template('img-processing.html')

@app.route("/image-compression")
def view_img_compression():
    return render_template('img-compression.html')

@app.route("/audio-processing")
def view_audio_processing():
    return render_template('audio-processing.html')

@app.route("/audio-compression")
def view_audio_compression():
    return render_template('audio-compression.html')


# Function and Processing Route
def processing_image(image_file, filter_type, input_brightness, input_contrast, input_saturation):
    # Membaca gambar
    # with Image.open(image_file) as img:
    #     img.load()
    img = Image.open(image_file)

    # Brightness Process
    filter = ImageEnhance.Brightness(img)
    bright_img = filter.enhance(input_brightness)

    # Contrast Process
    filter2 = ImageEnhance.Brightness(bright_img)
    contrast_img = filter2.enhance(input_contrast)

    # Saturation Process
    filter3 = ImageEnhance.Color(contrast_img)
    color_img = filter3.enhance(input_saturation)
    
    # Conditional Image Filter
    if filter_type == 'blur':
        filtered_img = color_img.filter(ImageFilter.BLUR)
    elif filter_type == 'sharpen':
        filtered_img = color_img.filter(ImageFilter.SHARPEN)
    elif filter_type == 'edge_detection':
        filtered_img = color_img.filter(ImageFilter.FIND_EDGES)
    elif filter_type == 'smooth':
        filtered_img = color_img.filter(ImageFilter.SMOOTH)
    elif filter_type == 'greyscale':
        filtered_img = color_img.convert('L')
    
    return filtered_img
    
def compress_image(image_file, quality):
    # Membuka gambar dengan Pillow
    img = Image.open(image_file)

    # Simpan gambar sementara
    filename = image_file.filename
    file_path = f"static/images/{filename}"
    img.save(file_path)

    # Ubah mode gambar menjadi RGB
    img = img.convert('RGB')

     # Menghitung ukuran file sebelum dikompresi
    file_size_before = len(image_file.read()) + image_file.tell()

    # Kompresi gambar dengan Pillow
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=quality)
    compressed_image = buffer.getvalue()

    # Menghitung ukuran file setelah dikompresi
    file_size_after = len(compressed_image)

    print('size sebelum compress:', file_size_before)
    print('size setelah compress:', file_size_after)

    return compressed_image, file_size_before, file_size_after

def audio_processing(audio_file, start_time, end_time, low, mid, high):
    # Buka file Audio
    audio = AudioSegment.from_mp3(audio_file)

    # Memotong file Audio
    cut_audio = audio[int(start_time)*1000:int(end_time)*1000]

    # Melakukan Equalizer
    equalize_audio = cut_audio + int(low) - int(high)
    equalize_audio = equalize_audio.high_pass_filter(int(mid))

    return equalize_audio

@app.route("/filter", methods=["POST"])
def img_process():
    # Menerima data gambar dari form HTML
    file = request.files['image']
    img = Image.open(file)
    filename = file.filename
    mimetype = file.mimetype
    # Simpan gambar sementara
    file_path = f"static/images/{filename}"
    img.save(file_path)
    
    filter_type = request.form['filter']
    brightness = float(request.form['brightness'])
    contrast = float(request.form['contrast'])
    color = float(request.form['saturation'])
    
    # Memproses gambar
    processed_image = processing_image(file, filter_type, brightness, contrast, color)

    # Hapus file sementara
    # os.remove(file_path)

    # Simpan gambar hasil pemrosesan
    processed_image_path = f"static/images/processed_{filename}"
    processed_image.save(processed_image_path)

    image_filename = 'processed_'+file.filename

    return render_template('./result/result_image_processing.html', img = file_path,img_filtered = processed_image_path, mimetype = mimetype, image_filename = image_filename)
    # return send_file(file_path, mimetype)

@app.route("/compress", methods=["POST"])
def compress():
    # Menerima data gambar dari form HTML
    file = request.files['image']
    filename = file.filename

    # Kompresi gambar
    compressed_image, file_size_before, file_size_after = compress_image(file, quality=60)

    # Simpan gambar hasil kompresi
    compressed_image_path = f"static/images/compressed_{filename}"
    with open(compressed_image_path, "wb") as f:
        f.write(compressed_image)

    return render_template(
        './result/result_image_compression.html', 
        original_image_path=f"static/images/{filename}", 
        compressed_image_path=compressed_image_path, 
        file_size_before = file_size_before, 
        file_size_after = file_size_after
        )


@app.route('/audio-filtering', methods=['POST'])
def audio_processing_route():
    # Menerima audio dari HTML
    file = request.files['audio_file']
    # print('file adalah', file)
    filename = file.filename
    mimetype = file.mimetype
    file_path = f"static/audio/{filename}"
    file.save(file_path)

    # print('file path adalah', file_path)
    # print('audio adalah', audio)

    # Menerima nilai start dan end untuk cut audio
    start_time = int(request.form['start_time'])
    end_time = int(request.form['end_time'])

    # Mendapatkan nilai equalizer dari form
    low_gain = request.form.get("low_gain")
    mid_gain = request.form.get("mid_gain")
    high_gain = request.form.get("high_gain")

    # Memproses gambar
    processed_audio = audio_processing(file_path, start_time, end_time, low_gain, mid_gain, high_gain)

    # Simpan gambar hasil pemrosesan
    processed_audio_path = f"static/audio/processed_{filename}"
    # processed_audio.export(processed_audio_path, format='mp3')
    processed_audio.export(processed_audio_path)

    audio_filename = 'processed_'+file.filename

    # return render_template('./result/result_image_processing.html', img = file_path,img_filtered = processed_image_path, mimetype = mimetype, image_filename = image_filename)
    return render_template('./result/result_audio_processing.html', audio_file = file_path, processed_audio_file = processed_audio_path, audio_filename = audio_filename, mimetype=mimetype)

@app.route('/audio-compressing', methods=['POST'])
def audio_compressing_route():
    # Menerima audio dari HTML
    file = request.files['audio_file']
    filename = file.filename
    # file_path = f"static/audio/{filename}"
    # file.save(file_path)

    # Load audio file as AudioSegment object
    audio = AudioSegment.from_mp3(file)

    # Mendapatkan nilai bitrate dari form
    bitrate = request.form.get("bitrate")

    # Memproses audio
    compressed_audio_path = f"static/audio/compressed_{filename}"
    compressed_audio = audio.set_frame_rate(44100).set_channels(2).export(compressed_audio_path, format="mp3", bitrate=bitrate)

    # Simpan audio hasil kompresi
    # compressed_audio.save(compressed_audio_path)

    audio_filename = 'compressed_'+filename

    return render_template('./result/result_audio_compressing.html', audio_file = filename, compressed_audio_file = compressed_audio_path, audio_filename = audio_filename)


# Download Route
@app.route('/download/<filename>')
def download(filename):
    image_filename = filename
    return send_file(f'static/images/{image_filename}', as_attachment=True)

@app.route('/download-audio/<filename>')
def download_audio(filename):
    image_filename = filename
    return send_file(f'static/audio/{image_filename}', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)