const Complaint = require('../models/Complaint');

// @desc    Submit a food safety complaint
// @route   POST /api/complaints
// @access  Private
exports.submitComplaint = async (req, res, next) => {
    try {
        const { restaurantId, issueCategory, description } = req.body;

        if (!restaurantId || !issueCategory || !description) {
            return res.status(400).json({ success: false, message: 'Please provide all required fields.' });
        }

        // Generate a unique complaint ID (CMP-YYYY-XXXX)
        const year = new Date().getFullYear();
        const randomNum = Math.floor(1000 + Math.random() * 9000);
        const complaintId = `CMP-${year}-${randomNum}`;

        const complaint = await Complaint.create({
            complaintId,
            restaurantId,
            userId: req.user._id,
            issueCategory,
            description
        });

        res.status(201).json({
            success: true,
            data: complaint,
            message: 'Complaint submitted successfully.'
        });

    } catch (error) {
        console.error(error);
        next(error);
    }
};
