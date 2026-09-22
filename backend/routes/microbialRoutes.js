const express = require('express');
const router = express.Router();
const { analyzeMicrobial, getMicrobialResult, getMicrobialStats } = require('../controllers/microbialController');
const { protect } = require('../middleware/authMiddleware');
const multer = require('multer');
const path = require('path');

const storage = multer.diskStorage({
  destination(req, file, cb) {
    cb(null, 'uploads/');
  },
  filename(req, file, cb) {
    cb(
      null,
      `${Date.now()}-${file.originalname}`
    );
  },
});

const upload = multer({
  storage,
  fileFilter: function (req, file, cb) {
    const filetypes = /jpg|jpeg|png/;
    const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = filetypes.test(file.mimetype);

    if (extname && mimetype) {
      return cb(null, true);
    } else {
      cb('Images only!');
    }
  },
});

router.post('/analyze', protect, upload.single('microscopicImage'), analyzeMicrobial);
router.get('/stats', protect, getMicrobialStats);
router.get('/:id', protect, getMicrobialResult);

module.exports = router;
