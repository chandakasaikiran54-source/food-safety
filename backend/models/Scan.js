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
    status: {
        type: String
    },
    visualIndicators: {
        type: [String],
        default: []
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
