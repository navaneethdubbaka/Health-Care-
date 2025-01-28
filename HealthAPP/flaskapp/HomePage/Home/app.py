from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    bp = db.Column(db.String(20), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    temperature = data.get('temperature')
    weight = data.get('weight')
    bp = data.get('bp')
    date = datetime.utcnow().date()

    # Save to database
    health_data = HealthData(date=date, temperature=temperature, weight=weight, bp=bp)
    db.session.add(health_data)
    db.session.commit()

    return jsonify({'message': 'Data submitted successfully'})

@app.route('/graph-data', methods=['GET'])
def graph_data():
    records = HealthData.query.order_by(HealthData.date).all()

    if not records:
        return jsonify({'error': 'No data available'}), 404
    
    data = {
        'dates': [record.date.strftime('%Y-%m-%d') for record in records],
        'temperature': [record.temperature for record in records],
        'weight': [record.weight for record in records],
        'bp': [record.bp for record in records],
    }
    return jsonify(data)

@app.route('/delete-data', methods=['DELETE'])
def delete_data():
    try:
        # Delete all records from the HealthData table
        HealthData.query.delete()
        db.session.commit()
        return jsonify({'message': 'All data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
