const mongoose = require('mongoose');

const sensorDataSchema = new mongoose.Schema({
    sensorId: { type: String, required: true },
    analysisId: { type: mongoose.Schema.Types.ObjectId, ref: 'Scan' },
    sensorType: { type: String, required: true },
    wavelengthRange: { type: String },
    measurementsReference: { type: String },
    metadata: { type: mongoose.Schema.Types.Mixed }
}, { timestamps: true });

module.exports = mongoose.model('SensorData', sensorDataSchema);
