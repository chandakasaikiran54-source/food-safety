const express = require('express');
const router = express.Router();
const { verifyOfficer, getDashboardStats } = require('../controllers/officerController');
const { protect } = require('../middleware/authMiddleware');

router.post('/verify', protect, verifyOfficer);
router.get('/dashboard-stats', protect, getDashboardStats);

module.exports = router;
