const RawFoodAssessment = require('../models/RawFoodAssessment');
const CustomerAssessment = require('../models/CustomerAssessment');
const FinalAssessment = require('../models/FinalAssessment');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');

exports.analyzeRawFood = async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'Please upload an image' });
        }

        const imagePath = `/uploads/${req.file.filename}`;
        const absolutePath = path.join(__dirname, '..', req.file.path);

        // Call the AI Python Service for Raw Food
        let aiResult = {};
        const aiServiceUrl = process.env.AI_SERVICE_URL ? `${process.env.AI_SERVICE_URL.replace('/analyze', '')}/raw-analyze` : 'http://127.0.0.1:8000/raw-analyze';
        
        console.log(`[AI-Raw] Sending image to AI service: ${aiServiceUrl}`);
        console.log(`[AI-Raw] Image path: ${absolutePath}`);
        
        const formData = new FormData();
        formData.append('image', fs.createReadStream(absolutePath));
        formData.append('filename', req.file.filename);
        
        try {
            const response = await axios.post(aiServiceUrl, formData, {
                headers: formData.getHeaders(),
                timeout: 10000 // 10s timeout
            });
            console.log(`[AI-Raw] AI service response: ${response.status}`);
            aiResult = response.data;
        } catch (error) {
            if (error.response) {
                console.error(`[AI-Raw] Connection error: API returned status ${error.response.status}`);
                if (error.response.status === 400 && error.response.data && error.response.data.message) {
                    return res.status(400).json({ success: false, message: error.response.data.message });
                }
            } else {
                console.error(`[AI-Raw] Connection error:`, error.message);
            }
            
            return res.status(503).json({ success: false, message: 'AI Service unavailable. Please try again later.' });
        }

        // Save to Database
        let assessmentData = {
            userId: req.user._id,
            imageUrl: imagePath,
            foodName: aiResult.foodName || 'Unknown',
            foodConfidence: aiResult.foodConfidence || 0.0,
            qualityStatus: aiResult.qualityStatus || 'INSUFFICIENT EVIDENCE',
            qualityConfidence: aiResult.qualityConfidence || 0.0,
            detectedVisualIndicators: aiResult.detectedVisualIndicators || [],
            microbialAssessment: aiResult.microbialAssessment || { status: 'NOT_DETERMINABLE_FROM_RGB', confidence: null },
            explanation: aiResult.explanation || '',
            limitations: aiResult.limitations || 'Visual AI assessment cannot confirm microbial, chemical, pesticide, or complete food safety.',
            assessmentType: aiResult.assessmentType || 'VISUAL_AI_ASSESSMENT',
            modelVersion: aiResult.modelVersion || 'Unknown',
            visualQualityScore: aiResult.visualQualityScore || null,
            defectSeverity: aiResult.defectSeverity || null,
            defectBoxes: aiResult.defectBoxes || []
        };

        const assessment = await RawFoodAssessment.create(assessmentData);

        res.status(201).json({
            success: true,
            data: {
                ...assessment.toObject(),
                aiResultData: aiResult // Send back the full AI payload if needed by frontend
            }
        });
    } catch (error) {
        console.error(error);
        next(error);
    }
};

exports.getRawFoodAssessments = async (req, res, next) => {
    try {
        const assessments = await RawFoodAssessment.find({ userId: req.user._id }).sort({ createdAt: -1 });
        res.json({ success: true, data: assessments });
    } catch (error) {
        next(error);
    }
};

exports.getRawFoodAssessmentById = async (req, res, next) => {
    try {
        const assessment = await RawFoodAssessment.findOne({ _id: req.params.id, userId: req.user._id });
        if (!assessment) {
            return res.status(404).json({ success: false, message: 'Assessment not found' });
        }
        res.json({ success: true, data: assessment });
    } catch (error) {
        next(error);
    }
};

exports.deleteRawFoodAssessment = async (req, res, next) => {
    try {
        const assessment = await RawFoodAssessment.findOne({ _id: req.params.id, userId: req.user._id });
        if (!assessment) {
            return res.status(404).json({ success: false, message: 'Assessment not found' });
        }
        await RawFoodAssessment.deleteOne({ _id: req.params.id, userId: req.user._id });
        res.json({ success: true, message: 'Assessment removed' });
    } catch (error) {
        next(error);
    }
};

exports.submitCustomerAssessment = async (req, res, next) => {
    try {
        const { foodQualityRating, tasteRating, qualityComment, tasteComment } = req.body;
        const rawFoodAssessmentId = req.params.id;

        const aiAssessment = await RawFoodAssessment.findOne({ _id: rawFoodAssessmentId, userId: req.user._id });
        if (!aiAssessment) {
            return res.status(404).json({ success: false, message: 'Original AI assessment not found' });
        }

        const customerAssessment = await CustomerAssessment.create({
            userId: req.user._id,
            rawFoodAssessmentId,
            foodQualityRating,
            tasteRating,
            qualityComment,
            tasteComment
        });

        // Calculate Final Assessment
        const aiQualityScore = aiAssessment.visualQualityScore || 3.0; // Default if not found
        
        let defectScore = 0;
        if (aiAssessment.defectSeverity === 'High') defectScore = -1.0;
        else if (aiAssessment.defectSeverity === 'Medium') defectScore = -0.5;
        else if (aiAssessment.defectSeverity === 'Low') defectScore = -0.2;

        // Weights: 40% Customer, 40% AI, 20% Defect Penalty
        // Max base score is 5 (40% of 5 + 40% of 5 + 20% of 5 = 2 + 2 + 1)
        // We'll treat defect penalty as a direct subtraction from the combined base score.
        // Formula: (Customer * 0.5) + (AI * 0.5) + DefectPenalty
        // Wait, prompt says: 40% customer, 40% AI, 20% Defect Assessment.
        // Let's map DefectSeverity to a score: None=5, Low=4, Medium=2.5, High=1
        let defectScoreVal = 5.0;
        if (aiAssessment.defectSeverity === 'High') defectScoreVal = 1.0;
        else if (aiAssessment.defectSeverity === 'Medium') defectScoreVal = 2.5;
        else if (aiAssessment.defectSeverity === 'Low') defectScoreVal = 4.0;

        let finalQualityScore = (foodQualityRating * 0.4) + (aiQualityScore * 0.4) + (defectScoreVal * 0.2);
        
        // Cap between 1 and 5
        finalQualityScore = Math.max(1, Math.min(5, finalQualityScore));

        // Generate Comparison Text
        const diff = foodQualityRating - aiQualityScore;
        let comparisonText = '';
        if (diff > 1) {
            comparisonText = 'Customer perception is significantly higher than the visual AI assessment.';
        } else if (diff > 0) {
            comparisonText = 'Customer perception is slightly higher than the visual AI assessment.';
        } else if (diff < -1) {
            comparisonText = 'Customer perception is significantly lower than the visual AI assessment. Visible quality concerns were detected by the AI.';
        } else if (diff < 0) {
            comparisonText = 'Customer perception is slightly lower than the visual AI assessment.';
        } else {
            comparisonText = 'Customer and AI assessments are in agreement.';
        }

        const finalAssessment = await FinalAssessment.create({
            userId: req.user._id,
            rawFoodAssessmentId,
            customerQualityScore: foodQualityRating,
            aiQualityScore,
            defectScore: defectScoreVal,
            finalQualityScore,
            tasteRating,
            comparisonText
        });

        res.status(201).json({
            success: true,
            data: {
                customerAssessment,
                finalAssessment
            }
        });

    } catch (error) {
        console.error(error);
        next(error);
    }
};
