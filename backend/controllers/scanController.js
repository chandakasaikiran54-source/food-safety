const Scan = require('../models/Scan');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

exports.analyzeFood = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'Please upload an image' });
        }

        const imagePath = `/uploads/${req.file.filename}`;
        const absolutePath = path.join(__dirname, '..', req.file.path);

        // Call the AI Python Service
        let aiResult = {};
        try {
            // Note: in a real environment, we'd stream the file or send the URL.
            // For this mock, we just tell the AI service the filename or send a dummy request.
            // But let's build it so it actually sends a multipart form if needed, or just standard json.
            // We'll send the filename, and the AI service can load it if they are on same disk,
            // or we'd just send a simple POST to trigger the mock.
            const response = await axios.post(process.env.AI_SERVICE_URL, {
                filename: req.file.filename,
                filepath: absolutePath
            });
            aiResult = response.data;
        } catch (error) {
            console.error('AI Service Error:', error.message);
            return res.status(503).json({ success: false, message: 'AI Service unavailable. Please try again later.' });
        }

        // Save to Database
        let scanData = {
            userId: req.user._id,
            image: imagePath,
            isFood: aiResult.isFood
        };

        if (aiResult.isFood === false) {
            scanData.status = 'Not Food';
            scanData.message = (aiResult.data && aiResult.data.message) ? aiResult.data.message : 'Food Not Detected';
        } else {
            const data = aiResult.data || {};
            scanData.detectedFood = data.detectedFood || 'Unknown';
            scanData.category = data.category || 'Raw / Not Cooked Food';
            scanData.confidence = data.confidence || 0.0;
            scanData.score = data.score || 0;
            scanData.status = data.status || 'High Concern';
            scanData.visualIndicators = data.visualIndicators || [];
            scanData.recommendations = data.recommendations || [];
            scanData.limitations = data.limitations || 'Invisible or microscopic hazards — including bacteria, viruses, pesticide residues, chemical contaminants, veterinary drug residues, and toxins — cannot be confirmed through ordinary image analysis. A food image that appears normal does not prove that the food is free from contamination.';
        }

        const scan = await Scan.create(scanData);

        res.status(201).json({
            success: true,
            data: scan
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};

exports.getScans = async (req, res) => {
    try {
        const scans = await Scan.find({ userId: req.user._id }).sort({ createdAt: -1 });
        res.json({ success: true, data: scans });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};

exports.getScanById = async (req, res) => {
    try {
        const scan = await Scan.findOne({ _id: req.params.id, userId: req.user._id });
        if (!scan) {
            return res.status(404).json({ success: false, message: 'Scan not found' });
        }
        res.json({ success: true, data: scan });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};

exports.deleteScan = async (req, res) => {
    try {
        const scan = await Scan.findOne({ _id: req.params.id, userId: req.user._id });
        if (!scan) {
            return res.status(404).json({ success: false, message: 'Scan not found' });
        }
        await Scan.deleteOne({ _id: req.params.id, userId: req.user._id });
        res.json({ success: true, message: 'Scan removed' });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server Error' });
    }
};
