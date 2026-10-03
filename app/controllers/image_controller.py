from flask import render_template

class ImageController:
    def index(self) -> str:
        return render_template('images/index.html')
