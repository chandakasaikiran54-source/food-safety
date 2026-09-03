const mongoose = require('mongoose');

const modelEvaluationSchema = new mongoose.Schema({
    modelVersion: { type: String, required: true },
    analysisId: { type: mongoose.Schema.Types.ObjectId, ref: 'Scan' },
    prediction: { type: String },
    actualResult: { type: String },
    error: { type: Number },
    evaluationDate: { type: Date, default: Date.now }
}, { timestamps: true });

module.exports = mongoose.model('ModelEvaluation', modelEvaluationSchema);
