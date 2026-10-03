from flask import render_template, jsonify, request


class ImageController:
    def index(self) -> str:
        return render_template('images/index.html')

    def analyze(self):
        """Handle image analysis request.
        
        Currently returns a stub response. Future implementation
        will load the ML model and return actual predictions.
        """
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        # TODO: Load model, preprocess image, run inference
        # image_file = request.files['image']
        # model = load_model('path/to/model.h5')
        # prediction = model.predict(preprocessed_image)
        
        return jsonify({'message': 'Imagen Recibida'}), 200
