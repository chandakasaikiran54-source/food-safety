const mongoose = require('mongoose');

const rawFoodAssessmentSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User'
    },
    foodName: {
        type: String,
        required: true,
        default: 'Unknown'
    },
    foodConfidence: {
        type: Number,
        required: true,
        default: 0.0
    },
    qualityStatus: {
        type: String,
        required: true,
        default: 'INSUFFICIENT EVIDENCE'
    },
    qualityConfidence: {
        type: Number,
        required: true,
        default: 0.0
    },
    detectedVisualIndicators: {
        type: [String],
        default: []
    },
    microbialAssessment: {
        status: { type: String, default: 'NOT_DETERMINABLE_FROM_RGB' },
        confidence: { type: Number, default: null }
    },
    explanation: {
        type: String,
        default: ''
    },
    limitations: {
        type: String,
        default: ''
    },
    imageUrl: {
        type: String,
        required: true
    },
    modelVersion: {
        type: String,
        default: 'Mock-Raw-Food-v1.0'
    },
    assessmentType: {
        type: String,
        default: 'VISUAL_AI_ASSESSMENT'
    },
    visualQualityScore: {
        type: Number
    },
    defectSeverity: {
        type: String
    },
    defectBoxes: {
        type: Array,
        default: []
    }
}, { timestamps: true });

module.exports = mongoose.model('RawFoodAssessment', rawFoodAssessmentSchema);
