const mongoose = require('mongoose');

const microbialAssessmentSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User'
    },
    foodName: {
        type: String,
        default: 'Biryani'
    },
    microscopicImage: {
        type: String,
        required: true
    },
    imageQuality: {
        type: String, // "acceptable" or "insufficient"
        required: true
    },
    bacterialResult: {
        type: String, // "bacteria_detected", "no_bacteria_detected", "inconclusive", "image_quality_insufficient", "model_not_available"
        required: true
    },
    confidence: {
        type: Number,
        default: 0.0
    },
    detectionRegions: {
        type: Array,
        default: []
    },
    modelVersion: {
        type: String,
        default: 'Not Validated'
    },
    // Lab Verification Ground Truth
    labVerified: {
        type: Boolean,
        default: false
    },
    labResult: {
        sampleId: String,
        laboratory: String,
        testMethod: String,
        result: String, // "Positive", "Negative"
        testDate: Date
    }
}, { timestamps: true });

module.exports = mongoose.model('MicrobialAssessment', microbialAssessmentSchema);
