const User = require('../models/User');
const VerifiedOfficer = require('../models/VerifiedOfficer');

// @desc    Verify and upgrade user to officer
// @route   POST /api/officers/verify
// @access  Private
exports.verifyOfficer = async (req, res) => {
    try {
        const { officerId, state, district } = req.body;

        if (!officerId || !state || !district) {
            return res.status(400).json({ success: false, message: 'Please provide all required official verification details.' });
        }

        // Check against mock FSSAI database
        const officialRecord = await VerifiedOfficer.findOne({ officerId });

        if (!officialRecord) {
            return res.status(404).json({ success: false, message: '❌ OFFICER NOT VERIFIED: Official ID does not exist in the government registry.' });
        }

        if (officialRecord.state.toLowerCase() !== state.toLowerCase() || officialRecord.district.toLowerCase() !== district.toLowerCase()) {
            return res.status(400).json({ success: false, message: '⚠ DETAILS MISMATCH: Provided location does not match official records.' });
        }

        if (officialRecord.verificationStatus !== 'VERIFIED') {
            return res.status(403).json({ success: false, message: `⚠ OFFICER NOT CURRENTLY ACTIVE: Status is ${officialRecord.verificationStatus}.` });
        }

        // Upgrade the logged-in user to Officer
        const user = await User.findById(req.user._id);
        user.role = 'officer';
        await user.save();

        res.json({
            success: true,
            message: '✓ OFFICIALLY VERIFIED FOOD SAFETY OFFICER',
            data: {
                role: user.role,
                officerData: officialRecord
            }
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error during official verification.' });
    }
};
