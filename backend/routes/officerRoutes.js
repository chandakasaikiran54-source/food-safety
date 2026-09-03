const express = require('express');
const router = express.Router();
const { verifyOfficer } = require('../controllers/officerController');
const { protect } = require('../middleware/authMiddleware');

router.post('/verify', protect, verifyOfficer);

module.exports = router;
