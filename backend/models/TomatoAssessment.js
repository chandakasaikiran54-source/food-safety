const mongoose = require('mongoose');

const tomatoAssessmentSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User'
    },
    foodName: {
        type: String,
        default: 'Tomato'
    },
    wholeImage: {
        type: String,
        required: true
    },
    cutImage: {
        type: String,
        required: true
    },
    // Customer Input
    customerFoodQuality: {
        type: String,
        required: true
    },
    customerTaste: {
        type: String,
        required: true
    },
    customerColour: {
        type: String,
        required: true
    },
    customerTexture: {
        type: String,
        required: true
    },
    customerComment: {
        type: String,
        default: ''
    },
    // Colour Matching
    aiDetectedColour: {
        type: String,
        default: 'Unknown'
    },
    colourMatch: {
        type: String,
        default: 'Unknown'
    },
    // AI Analysis (Aggregated from whole + cut)
    aiScore: {
        type: Number,
        required: true
    },
    aiHygieneStatus: {
        type: String,
        required: true
    },
    detectedIssues: {
        type: [String],
        default: []
    },
    wholeIssues: {
        type: [String],
        default: []
    },
    cutIssues: {
        type: [String],
        default: []
    },
    aiConfidence: {
        type: Number,
        default: 0.0
    },
    // Final Calculated Scores
    customerScore: {
        type: Number,
        required: true
    },
    finalScore: {
        type: Number,
        required: true
    },
    finalHygieneStatus: {
        type: String,
        required: true
    },
    qualityLevel: {
        type: String,
        required: true
    },
    // Detailed AI breakdown for UI
    aiBreakdown: {
        outerAppearance: { type: Number, default: 0 },
        internalAppearance: { type: Number, default: 0 },
        freshnessIndicators: { type: Number, default: 0 },
        visibleCleanliness: { type: Number, default: 0 }
    },
    // Future Sensor/Lab Integration
    hasLabData: {
        type: Boolean,
        default: false
    },
    labData: {
        testName: String,
        result: String,
        source: String,
        date: Date
    },
    modelVersion: {
        type: String,
        default: 'ML-CV-Tomato-v1.0'
    },
    // Plant Disease Recognition Result
    diseaseAssessment: {
        isCompatible: Boolean,
        message: String,
        resnet18: {
            predicted_class: String,
            confidence: Number
        },
        mobilenetv3: {
            predicted_class: String,
            confidence: Number
        }
    }
}, { timestamps: true });

module.exports = mongoose.model('TomatoAssessment', tomatoAssessmentSchema);
