const mongoose = require('mongoose');

const labResultSchema = new mongoose.Schema({
    sampleId: { type: String, required: true },
    analysisId: { type: mongoose.Schema.Types.ObjectId, ref: 'Scan' },
    testType: { type: String, required: true },
    measuredValue: { type: String },
    referenceLimit: { type: String },
    result: { type: String },
    laboratory: { type: String },
    verificationStatus: { type: String, default: 'PENDING' },
    reportReference: { type: String },
    testDate: { type: Date }
}, { timestamps: true });

module.exports = mongoose.model('LabResult', labResultSchema);
