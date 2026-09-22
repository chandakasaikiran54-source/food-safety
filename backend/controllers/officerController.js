const User = require('../models/User');
const VerifiedOfficer = require('../models/VerifiedOfficer');
const Inspection = require('../models/Inspection');

// @desc    Verify and upgrade user to officer
// @route   POST /api/officers/verify
// @access  Private
exports.verifyOfficer = async (req, res, next) => {
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
        user.officerId = officialRecord.officerId;
        await user.save();

        res.json({
            success: true,
            message: '✓ Verified against latest available official government database (Demo)',
            data: {
                role: user.role,
                officerData: officialRecord
            }
        });

    } catch (error) {
        console.error(error);
        next(error);
    }
};

// @desc    Get dashboard stats for officer
// @route   GET /api/officers/dashboard-stats
// @access  Private (Officer)
exports.getDashboardStats = async (req, res, next) => {
    try {
        if (req.user.role !== 'officer' && req.user.role !== 'admin') {
            return res.status(403).json({ success: false, message: 'Access denied.' });
        }

        const inspections = await Inspection.find({ officerId: req.user._id });

        const now = new Date();
        now.setHours(0, 0, 0, 0);

        let upcoming = 0;
        let dueToday = 0;
        let overdue = 0;

        inspections.forEach(insp => {
            if (insp.nextInspectionDate) {
                const dueDate = new Date(insp.nextInspectionDate);
                dueDate.setHours(0, 0, 0, 0);

                if (dueDate > now) upcoming++;
                else if (dueDate.getTime() === now.getTime()) dueToday++;
                else overdue++;
            }
        });

        res.json({
            success: true,
            data: {
                totalInspections: inspections.length,
                upcoming,
                dueToday,
                overdue,
                recentInspections: inspections.sort((a, b) => b.createdAt - a.createdAt).slice(0, 5)
            }
        });
    } catch (error) {
        next(error);
    }
};
