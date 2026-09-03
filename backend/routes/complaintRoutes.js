const express = require('express');
const router = express.Router();
const { submitComplaint } = require('../controllers/complaintController');
const { protect } = require('../middleware/authMiddleware');

router.post('/', protect, submitComplaint);

module.exports = router;
