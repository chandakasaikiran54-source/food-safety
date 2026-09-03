const Restaurant = require('../models/Restaurant');
const Inspection = require('../models/Inspection');

// @desc    Search restaurant by name and location
// @route   GET /api/restaurants/search
// @access  Private
exports.searchRestaurant = async (req, res) => {
    try {
        const { name, location } = req.query;
        if (!name || !location) {
            return res.status(400).json({ success: false, message: 'Please provide both name and location' });
        }
        
        // Case insensitive search
        const restaurant = await Restaurant.findOne({
            name: { $regex: new RegExp(`^${name}$`, 'i') },
            location: { $regex: new RegExp(`^${location}$`, 'i') }
        });

        if (!restaurant) {
            return res.status(404).json({ success: false, message: 'Restaurant not found' });
        }

        res.json({ success: true, data: restaurant });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};

// @desc    Get restaurant by ID with inspections
// @route   GET /api/restaurants/:id
// @access  Private
exports.getRestaurantById = async (req, res) => {
    try {
        const restaurant = await Restaurant.findById(req.params.id);
        if (!restaurant) {
            return res.status(404).json({ success: false, message: 'Restaurant not found' });
        }
        
        const inspections = await Inspection.find({ restaurantId: restaurant._id })
            .populate('officerId', 'name email')
            .sort({ date: -1 });

        res.json({ success: true, data: { restaurant, inspections } });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};

// @desc    Submit an inspection (Officer only)
// @route   POST /api/restaurants/inspect
// @access  Private (Officer)
exports.submitInspection = async (req, res) => {
    try {
        // Ensure user is an officer
        if (req.user.role !== 'officer') {
            return res.status(403).json({ success: false, message: 'Not authorized as an officer' });
        }

        const {
            restaurantName,
            restaurantLocation,
            foodStatus,
            hygieneRating,
            rawMaterialStatus,
            kitchenCleanliness,
            overallRating,
            remarks,
            date,
            nextInspectionDate
        } = req.body;

        if (!restaurantName || !restaurantLocation || !foodStatus || !hygieneRating || !rawMaterialStatus || !kitchenCleanliness || !overallRating || !date) {
            return res.status(400).json({ success: false, message: 'Please provide all required fields' });
        }

        // Find or create restaurant
        let restaurant = await Restaurant.findOne({
            name: { $regex: new RegExp(`^${restaurantName}$`, 'i') },
            location: { $regex: new RegExp(`^${restaurantLocation}$`, 'i') }
        });

        if (!restaurant) {
            restaurant = await Restaurant.create({
                name: restaurantName,
                location: restaurantLocation,
                latestInspectionStatus: foodStatus,
                latestInspectionDate: date
            });
        } else {
            restaurant.latestInspectionStatus = foodStatus;
            restaurant.latestInspectionDate = date;
            await restaurant.save();
        }

        const inspection = await Inspection.create({
            restaurantId: restaurant._id,
            officerId: req.user._id,
            date,
            foodStatus,
            hygieneRating,
            rawMaterialStatus,
            kitchenCleanliness,
            overallRating,
            remarks,
            nextInspectionDate
        });

        res.status(201).json({ success: true, data: inspection });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};
