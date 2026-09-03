const mongoose = require('mongoose');

const complaintSchema = new mongoose.Schema({
    complaintId: { type: String, required: true, unique: true },
    restaurantId: { type: mongoose.Schema.Types.ObjectId, ref: 'Restaurant', required: true },
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    issueCategory: { type: String, required: true },
    description: { type: String, required: true },
    status: { type: String, enum: ['SUBMITTED', 'UNDER REVIEW', 'ASSIGNED', 'INSPECTION REQUIRED', 'RESOLVED', 'CLOSED'], default: 'SUBMITTED' }
}, { timestamps: true });

module.exports = mongoose.model('Complaint', complaintSchema);
