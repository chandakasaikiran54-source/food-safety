const mongoose = require('mongoose');

const restaurantSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: true,
            trim: true
        },
        location: {
            type: String,
            required: true,
            trim: true
        },
        latestInspectionStatus: {
            type: String,
            default: 'Not Visited'
        },
        latestInspectionDate: {
            type: Date
        }
    },
    {
        timestamps: true
    }
);

module.exports = mongoose.model('Restaurant', restaurantSchema);
