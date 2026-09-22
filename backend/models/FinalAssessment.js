const mongoose = require('mongoose');

const finalAssessmentSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'User'
    },
    rawFoodAssessmentId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'RawFoodAssessment'
    },
    customerQualityScore: {
        type: Number,
        required: true
    },
    aiQualityScore: {
        type: Number,
        required: true
    },
    defectScore: {
        type: Number,
        required: true
    },
    finalQualityScore: {
        type: Number,
        required: true
    },
    tasteRating: {
        type: Number,
        required: true
    },
    comparisonText: {
        type: String,
        required: true
    },
    confidence: {
        type: Number,
        default: 1.0
    },
    calculationVersion: {
        type: String,
        default: 'v1.0'
    }
}, { timestamps: true });

module.exports = mongoose.model('FinalAssessment', finalAssessmentSchema);
