const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const MicrobialAssessment = require('../models/MicrobialAssessment');

// Helper to call Python AI Service
const callMicrobialAIService = async (imagePath, filename) => {
    try {
        const form = new FormData();
        form.append('image', fs.createReadStream(imagePath), filename);

        const response = await axios.post('http://127.0.0.1:8000/microbial-analyze', form, {
            headers: {
                ...form.getHeaders()
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error calling Python Microbial AI service:', error.message);
        throw new Error('Microbial AI Service unavailable. Please try again later.');
    }
};

exports.analyzeMicrobial = async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'Please upload a microscopic image.' });
        }

        const imageFile = req.file;
        const imagePath = `/uploads/${imageFile.filename}`;
        const absolutePath = path.join(__dirname, '..', imageFile.path);

        // 1. Call AI Service for Microbial Analysis
        const aiResult = await callMicrobialAIService(absolutePath, imageFile.filename);
        
        // 2. Save to DB
        const assessment = await MicrobialAssessment.create({
            userId: req.user._id,
            microscopicImage: imagePath,
            foodType: 'Biryani', // Food focus
            imageQuality: aiResult.image_quality || 'insufficient',
            bacterialResult: aiResult.result || 'inconclusive',
            confidence: aiResult.confidence || 0.0,
            detectionRegions: aiResult.detection_regions || [],
            modelVersion: aiResult.model_version || 'Not Validated',
            labVerified: false
        });

        res.status(201).json({
            success: true,
            data: assessment
        });

    } catch (error) {
        next(error);
    }
};

exports.getMicrobialResult = async (req, res, next) => {
    try {
        const assessment = await MicrobialAssessment.findById(req.params.id);
        
        if (!assessment) {
            return res.status(404).json({ success: false, message: 'Microbial assessment not found' });
        }

        // Verify user owns this assessment or is an officer
        if (assessment.userId.toString() !== req.user._id.toString() && req.user.role !== 'officer' && req.user.role !== 'admin') {
            return res.status(403).json({ success: false, message: 'Not authorized to view this assessment' });
        }

        res.status(200).json({
            success: true,
            data: assessment
        });
    } catch (error) {
        next(error);
    }
};

// Admin/Research endpoint for Dashboard
exports.getMicrobialStats = async (req, res, next) => {
    try {
        // Only admins/officers
        if (req.user.role !== 'officer' && req.user.role !== 'admin') {
            return res.status(403).json({ success: false, message: 'Not authorized' });
        }

        const totalSamples = await MicrobialAssessment.countDocuments();
        const aiPositive = await MicrobialAssessment.countDocuments({ bacterialResult: 'bacteria_detected' });
        const aiNegative = await MicrobialAssessment.countDocuments({ bacterialResult: 'no_bacteria_detected' });
        const aiInconclusive = await MicrobialAssessment.countDocuments({ bacterialResult: { $in: ['inconclusive', 'model_not_available', 'image_quality_insufficient'] } });
        
        const labVerifiedCount = await MicrobialAssessment.countDocuments({ labVerified: true });
        const labPositive = await MicrobialAssessment.countDocuments({ labVerified: true, 'labResult.result': 'Positive' });
        const labNegative = await MicrobialAssessment.countDocuments({ labVerified: true, 'labResult.result': 'Negative' });

        res.status(200).json({
            success: true,
            data: {
                totalSamples,
                aiPositive,
                aiNegative,
                aiInconclusive,
                labVerifiedCount,
                labPositive,
                labNegative
            }
        });
    } catch (error) {
        next(error);
    }
};
