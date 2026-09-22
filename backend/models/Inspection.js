const mongoose = require('mongoose');

const inspectionSchema = new mongoose.Schema(
    {
        restaurantId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            ref: 'Restaurant'
        },
        officerId: {
            type: mongoose.Schema.Types.ObjectId,
            required: true,
            ref: 'User'
        },
        date: {
            type: Date,
            required: true
        },
        foodStatus: {
            type: String,
            required: true
        },
        hygieneRating: {
            type: Number,
            required: true
        },
        rawMaterialStatus: {
            type: String,
            required: true
        },
        kitchenCleanliness: {
            type: String,
            required: true
        },
        overallRating: {
            type: Number,
            required: true
        },
        remarks: {
            type: String
        },
        nextInspectionDate: {
            type: Date
        },
        foodStorageCondition: {
            type: String,
            required: true
        },
        wasteManagement: {
            type: String,
            required: true
        },
        pestControl: {
            type: String,
            required: true
        },
        staffHygiene: {
            type: String,
            required: true
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model('Inspection', inspectionSchema);
