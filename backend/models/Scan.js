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
    status: {
        type: String
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
    visualAssessmentStatus: {
        type: String
    },
    hygieneConfidence: {
        type: Number
    },
    visibleIssues: {
        type: [String],
        default: []
    },
    cookingStatus: {
        type: String
    },
    cookingConfidence: {
        type: Number
    },
    visibleCookingIndicators: {
        type: [String],
        default: []
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
    },
    mealItems: {
        type: [mongoose.Schema.Types.Mixed],
        default: []
    },
    howToEatGuide: {
        type: [mongoose.Schema.Types.Mixed],
        default: []
    },
    mealSuggestion: {
        type: String
    },
    // New Tomato Fields
    qualityScore: {
        type: Number
    },
    defectScore: {
        type: Number
    },
    microbialSafetyRisk: {
        type: String
    },
    qualityLevel: {
        type: String
    },
    reason: {
        type: String
    },
    customerAssessment: {
        quality: { type: String, default: null },
        taste: { type: String, default: null },
        comment: { type: String, default: null }
    },
    finalQualityScore: {
        type: Number
    },
    assessmentDifference: {
        type: String
    },
    howToEat: {
        type: [String],
        default: []
    }
}, { timestamps: true });

module.exports = mongoose.model('Scan', scanSchema);
