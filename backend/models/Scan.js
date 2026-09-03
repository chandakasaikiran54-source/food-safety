const mongoose = require('mongoose');

const scanSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User'
    },
    image: {
        type: String,
        required: true
    },
    isFood: {
        type: Boolean,
        default: true
    },
    message: {
        type: String
    },
    detectedFood: {
        type: String
    },
    category: {
        type: String
    },
    confidence: {
        type: Number
    },
    score: {
        type: Number
    },
    freshness: {
        type: String
    },
    visibleMold: {
        type: String
    },
    visibleDiscoloration: {
        type: String
    },
    visibleContamination: {
        type: String
    },
    visualHygieneRisk: {
        type: String
    },
    analysisType: {
        type: String,
        default: 'RGB'
    },
    reconstructedSpectralReference: {
        type: String
    },
    measuredSpectralReference: {
        type: String
    },
    sensorResults: {
        type: mongoose.Schema.Types.Mixed
    },
    multimodalResult: {
        type: String
    },
    modelVersion: {
        type: String,
        default: 'MobileNetV3-Food-v1'
    },
    recommendations: {
        type: [String],
        default: []
    },
    limitations: {
        type: String
    }
}, { timestamps: true });

module.exports = mongoose.model('Scan', scanSchema);
