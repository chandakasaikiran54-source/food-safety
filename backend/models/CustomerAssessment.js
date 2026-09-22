const mongoose = require('mongoose');

const customerAssessmentSchema = new mongoose.Schema({
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
    foodQualityRating: {
        type: Number,
        required: true,
        min: 1,
        max: 5
    },
    tasteRating: {
        type: Number,
        required: true,
        min: 1,
        max: 5
    },
    qualityComment: {
        type: String,
        default: ''
    },
    tasteComment: {
        type: String,
        default: ''
    }
}, { timestamps: true });

module.exports = mongoose.model('CustomerAssessment', customerAssessmentSchema);
