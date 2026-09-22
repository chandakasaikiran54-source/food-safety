const TomatoAssessment = require('../models/TomatoAssessment');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');

// Helper to call the AI service
const callAIService = async (filePath, filename) => {
    let aiResult = null;
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/analyze';
    
    console.log(`[Tomato AI] Sending image to AI service: ${aiServiceUrl}`);
    
    const formData = new FormData();
    formData.append('image', fs.createReadStream(filePath));
    formData.append('filename', filename);
    
    try {
        const response = await axios.post(aiServiceUrl, formData, {
            headers: formData.getHeaders(),
            timeout: 10000
        });
        aiResult = response.data;
    } catch (error) {
        if (error.response) {
            console.error(`[Tomato AI] API error status: ${error.response.status}`, error.response.data);
            const err = new Error(error.response.data.message || 'AI service error');
            err.status = error.response.status;
            throw err;
        } else {
            console.error(`[Tomato AI] Connection error:`, error.message);
            const err = new Error('AI Service unavailable. Please try again later.');
            err.status = 503;
            throw err;
        }
    }
    
    return aiResult;
};

const callAIDiseaseService = async (filePath, filename) => {
    let aiResult = null;
    const aiServiceUrl = process.env.AI_DISEASE_URL || 'http://127.0.0.1:8000/api/disease/analyze';
    
    console.log(`[Tomato AI] Sending image to AI disease service: ${aiServiceUrl}`);
    
    const formData = new FormData();
    formData.append('image', fs.createReadStream(filePath));
    formData.append('filename', filename);
    
    try {
        const response = await axios.post(aiServiceUrl, formData, {
            headers: formData.getHeaders(),
            timeout: 20000
        });
        aiResult = response.data;
    } catch (error) {
        if (error.response) {
            console.error(`[Tomato AI] Disease API error:`, error.response.data);
            aiResult = { success: false, is_compatible: false, message: error.response.data.message || 'Disease AI error' };
        } else {
            console.error(`[Tomato AI] Disease API connection error:`, error.message);
            aiResult = { success: false, is_compatible: false, message: 'Disease AI unavailable' };
        }
    }
    
    return aiResult;
};

exports.analyzeTomato = async (req, res, next) => {
    try {
        if (!req.files || !req.files.wholeImage) {
            return res.status(400).json({ success: false, message: 'Whole tomato image is required.' });
        }

        const { customerColour, customerTexture, customerComment, customerFoodQuality, customerTaste } = req.body;

        if (!customerColour || !customerTexture || !customerFoodQuality || !customerTaste) {
            return res.status(400).json({ success: false, message: 'Customer colour, texture, food quality, and taste observations are required.' });
        }

        const wholeFile = req.files.wholeImage[0];
        const cutFile = req.files.cutImage ? req.files.cutImage[0] : null;

        const wholeImagePath = `/uploads/${wholeFile.filename}`;
        const cutImagePath = cutFile ? `/uploads/${cutFile.filename}` : null;

        const absoluteWholePath = path.join(__dirname, '..', wholeFile.path);
        const absoluteCutPath = cutFile ? path.join(__dirname, '..', cutFile.path) : null;

        // 1. Call AI Service for Whole Tomato and Disease recognition concurrently
        const [wholeAiResult, diseaseResult] = await Promise.all([
            callAIService(absoluteWholePath, wholeFile.filename),
            callAIDiseaseService(absoluteWholePath, wholeFile.filename)
        ]);
        
        if (!wholeAiResult.isFood) {
             return res.status(400).json({ success: false, message: 'Whole image: ' + wholeAiResult.data.message });
        }
        
        let diseaseAssessment = {
            isCompatible: false,
            message: "Unable to process disease assessment.",
            resnet18: null,
            mobilenetv3: null
        };
        
        if (diseaseResult && diseaseResult.success) {
            diseaseAssessment = {
                isCompatible: diseaseResult.is_compatible,
                message: diseaseResult.message || "",
                resnet18: diseaseResult.resnet18,
                mobilenetv3: diseaseResult.mobilenetv3
            };
        } else if (diseaseResult) {
            diseaseAssessment.message = diseaseResult.message;
        }

        // 2. Call AI Service for Cut Tomato
        let cutAiResult = null;
        if (cutFile) {
            cutAiResult = await callAIService(absoluteCutPath, cutFile.filename);
            if (!cutAiResult.isFood) {
                 return res.status(400).json({ success: false, message: 'Cut image: ' + cutAiResult.data.message });
            }
        }

        // 3. Aggregate AI Results (OUTPUT 1)
        const wholeData = wholeAiResult.data;
        const cutData = cutAiResult ? cutAiResult.data : null;

        // Average AI score
        const aiScore = cutData ? (wholeData.qualityScore + cutData.qualityScore) / 2 : wholeData.qualityScore;
        const aiConfidence = cutData ? (wholeData.foodConfidence + cutData.foodConfidence) / 2 : wholeData.foodConfidence;
        
        // Combine issues
        const wholeIssues = wholeData.visibleIssues || [];
        const cutIssues = cutData ? (cutData.visibleIssues || []) : [];
        const combinedIssues = [...new Set([...wholeIssues, ...cutIssues])];
        
        // Determine Hygiene Status based on both
        let aiHygieneStatus = 'INSUFFICIENT EVIDENCE';
        if (wholeData.visualAssessmentStatus.includes('Risk') || (cutData && cutData.visualAssessmentStatus.includes('Risk'))) {
            aiHygieneStatus = 'NOT HYGIENIC';
        } else if (wholeData.visualAssessmentStatus.includes('No Visible') && (!cutData || cutData.visualAssessmentStatus.includes('No Visible'))) {
            aiHygieneStatus = 'HYGIENIC';
        }

        // Colour matching
        const aiDetectedColour = wholeData.detectedColour || 'Unknown';
        let colourMatch = 'DIFFERENT';
        if (customerColour === aiDetectedColour || 
            (customerColour === 'Bright Red' && aiDetectedColour === 'Red') ||
            (customerColour === 'Red' && aiDetectedColour === 'Bright Red') ||
            (customerColour === 'Red' && aiDetectedColour === 'Light Red') ||
            (customerColour === 'Light Red' && aiDetectedColour === 'Red')) {
            colourMatch = 'MATCH';
        }

        // 4. Calculate Customer Score (OUTPUT 2)
        const ratingMap = {
            'Excellent': 100,
            'Good': 80,
            'Average': 60,
            'Poor': 40,
            'Very Poor': 20
        };
        
        const foodQualityScore = ratingMap[customerFoodQuality] || 60;
        const tasteScore = ratingMap[customerTaste] || 60;
        
        const customerScore = (foodQualityScore + tasteScore) / 2;

        // 5. Final Calculation (Arithmetic Average)
        const finalScore = (aiScore + customerScore) / 2;
        
        // Final Hygiene (strictly follows AI hygiene)
        let finalHygieneStatus = aiHygieneStatus;
        let qualityLevel = 'AVERAGE';
        
        if (finalScore >= 70) qualityLevel = 'GOOD';
        else if (finalScore < 50) {
            qualityLevel = 'POOR';
        }

        // 6. Detailed Breakdown for UI
        const aiBreakdown = {
            outerAppearance: wholeData.qualityScore || 0,
            internalAppearance: cutData ? (cutData.qualityScore || 0) : null,
            freshnessIndicators: cutData ? Math.max(0, 100 - ((wholeData.defectScore + cutData.defectScore) / 2)) : Math.max(0, 100 - wholeData.defectScore),
            visibleCleanliness: aiHygieneStatus === 'HYGIENIC' ? 95 : (aiHygieneStatus === 'NOT HYGIENIC' ? 30 : 60)
        };

        // 7. Save to DB
        const assessment = await TomatoAssessment.create({
            userId: req.user._id,
            wholeImage: wholeImagePath,
            cutImage: cutImagePath,
            customerFoodQuality,
            customerTaste,
            customerColour,
            customerTexture,
            customerComment,
            aiDetectedColour,
            colourMatch,
            aiScore: Math.round(aiScore),
            aiHygieneStatus,
            detectedIssues: combinedIssues,
            wholeIssues,
            cutIssues,
            aiConfidence,
            customerScore: Math.round(customerScore),
            finalScore: Math.round(finalScore),
            finalHygieneStatus,
            qualityLevel,
            aiBreakdown,
            diseaseAssessment,
            hasLabData: false
        });

        res.status(201).json({
            success: true,
            data: assessment
        });

    } catch (error) {
        console.error(error);
        if (error.status) {
            return res.status(error.status).json({ success: false, message: error.message });
        }
        next(error);
    }
};

exports.getTomatoAssessments = async (req, res, next) => {
    try {
        const assessments = await TomatoAssessment.find({ userId: req.user._id }).sort({ createdAt: -1 });
        res.json({ success: true, data: assessments });
    } catch (error) {
        next(error);
    }
};

exports.getTomatoAssessmentById = async (req, res, next) => {
    try {
        const assessment = await TomatoAssessment.findOne({ _id: req.params.id, userId: req.user._id });
        if (!assessment) {
            return res.status(404).json({ success: false, message: 'Assessment not found' });
        }
        res.json({ success: true, data: assessment });
    } catch (error) {
        next(error);
    }
};
