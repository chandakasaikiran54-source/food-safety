const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const { analyzeTomato, getTomatoAssessments, getTomatoAssessmentById } = require('../controllers/tomatoController');
const { protect } = require('../middleware/authMiddleware');

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, `tomato-${Date.now()}-${file.originalname}`);
    }
});

const upload = multer({
    storage,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
    fileFilter: function (req, file, cb) {
        const filetypes = /jpeg|jpg|png|webp/;
        const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = filetypes.test(file.mimetype);
        if (mimetype && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Please upload a JPG, PNG, or WEBP image.'), false);
        }
    }
});

const uploadMiddleware = (req, res, next) => {
    const uploadFields = upload.fields([
        { name: 'wholeImage', maxCount: 1 },
        { name: 'cutImage', maxCount: 1 }
    ]);
    
    uploadFields(req, res, function (err) {
        if (err instanceof multer.MulterError) {
            if (err.code === 'LIMIT_FILE_SIZE') {
                return res.status(400).json({ success: false, message: 'Image size must be less than 10 MB.' });
            }
            return res.status(400).json({ success: false, message: err.message });
        } else if (err) {
            return res.status(400).json({ success: false, message: err.message });
        }
        next();
    });
};

router.post('/analyze', protect, uploadMiddleware, analyzeTomato);
router.route('/').get(protect, getTomatoAssessments);
router.route('/:id').get(protect, getTomatoAssessmentById);

module.exports = router;
