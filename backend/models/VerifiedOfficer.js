const mongoose = require('mongoose');

const verifiedOfficerSchema = new mongoose.Schema({
    officerId: { type: String, required: true, unique: true },
    name: { type: String, required: true },
    designation: { type: String, required: true },
    state: { type: String, required: true },
    district: { type: String, required: true },
    sourceName: { type: String, default: 'Official FSSAI/FDA Database' },
    verificationStatus: { type: String, enum: ['VERIFIED', 'INACTIVE'], default: 'VERIFIED' }
}, { timestamps: true });

module.exports = mongoose.model('VerifiedOfficer', verifiedOfficerSchema);
