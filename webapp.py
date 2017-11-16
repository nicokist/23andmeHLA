#!/usr/bin/env python3
import sys
from flask import Flask, request
from flask_uploads import UploadSet, IMAGES, configure_uploads
app = Flask(__name__)


app.config['UPLOADED_PHOTOS_DEST'] = '/var/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        rec = Photo(filename=filename, user=g.user.id)
        rec.store()
        flash("Photo saved.")
        return redirect(url_for('show', id=rec.id))
    return render_template('upload.html')

@app.route('/photo/<id>')
def show(id):
    photo = Photo.load(id)
    if photo is None:
        abort(404)
    url = photos.url(photo.filename)
    return render_template('show.html', url=url, photo=photo)



@app.route('/')
def hello_world():
    return """
<html>
<body>
<p>{{ url_for('upload') }}</p>

<form method=POST enctype=multipart/form-data action="upload">
    <input type=file name=photo id=file>
    <input type="submit">
</form>

<script>
document.getElementById("file").onchange = function() {
    document.getElementById("form").submit();
}
</script>

</html>
</body>
    """


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

