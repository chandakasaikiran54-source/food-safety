const express = require('express');
const router = express.Router();
const { searchRestaurant, getRestaurantById, submitInspection } = require('../controllers/restaurantController');
const { protect } = require('../middleware/authMiddleware');

router.get('/search', protect, searchRestaurant);
router.post('/inspect', protect, submitInspection);
router.get('/:id', protect, getRestaurantById);

module.exports = router;
