const Scan = require('../models/Scan');
const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');

const generateHowToEatGuide = (mealItems) => {
    let guide = [];
    let suggestion = "These items can be eaten in any preferred order.";
    
    if (!mealItems || mealItems.length === 0) return { guide, suggestion };

    const itemNames = mealItems.map(item => item.name.toLowerCase());
    
    const hasBiryani = itemNames.includes("chicken biryani") || itemNames.includes("biryani");
    const hasRaita = itemNames.includes("raita");
    const hasSalad = itemNames.includes("onion salad") || itemNames.includes("salad");
    const hasLemon = itemNames.includes("lemon");
    
    const hasDosa = itemNames.includes("dosa");
    const hasSambar = itemNames.includes("sambar");
    const hasChutney = itemNames.includes("coconut chutney") || itemNames.includes("chutney");

    // Generate Rules for Biryani Meal
    if (hasBiryani) {
        let biryaniRule = "Main dish. Eat directly";
        if (hasRaita) biryaniRule += " or combine with the detected raita.";
        else biryaniRule += ".";
        guide.push({ item: "Chicken Biryani", instructions: biryaniRule });
        
        if (hasRaita) guide.push({ item: "Raita", instructions: "Usually eaten as a side with biryani. You can mix a small amount with biryani or eat it separately." });
        if (hasSalad) guide.push({ item: "Onion Salad", instructions: "Can be eaten separately as a side." });
        if (hasLemon) guide.push({ item: "Lemon", instructions: "Optional. Add according to personal taste." });
        
        suggestion = "These items are commonly eaten together. You can combine the biryani with raita and have the salad/lemon separately according to your preference.";
    } 
    // Generate Rules for Dosa Meal
    else if (hasDosa) {
        guide.push({ item: "Dosa", instructions: "Main dish. Can commonly be eaten with the detected sambar and chutney." });
        if (hasSambar) guide.push({ item: "Sambar", instructions: "Can be combined with dosa." });
        if (hasChutney) guide.push({ item: "Coconut Chutney", instructions: "Can be eaten as a side/dip." });
        
        let sugText = "Dosa can commonly be eaten with";
        if (hasSambar && hasChutney) sugText += " the detected sambar and coconut chutney.";
        else if (hasSambar) sugText += " the detected sambar.";
        else if (hasChutney) sugText += " the detected chutney.";
        else sugText = "Dosa can be eaten directly.";
        
        suggestion = sugText;
    }
    // Generic
    else {
        mealItems.forEach(item => {
            if (item.name !== "Unknown Food Item") {
                guide.push({ item: item.name, instructions: "Can be eaten according to personal preference." });
            }
        });
    }

    return { guide, suggestion };
};

exports.analyzeFood = async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'Please upload an image' });
        }

        const imagePath = `/uploads/${req.file.filename}`;
        const absolutePath = path.join(__dirname, '..', req.file.path);

        // Call the AI Python Service
        let aiResult = {};
        const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/analyze';
        
        console.log(`[AI] Sending image to AI service: ${aiServiceUrl}`);
        console.log(`[AI] Image path: ${absolutePath}`);
        
        const formData = new FormData();
        formData.append('image', fs.createReadStream(absolutePath));
        formData.append('filename', req.file.filename);
        
        try {
            const response = await axios.post(aiServiceUrl, formData, {
                headers: formData.getHeaders(),
                timeout: 10000 // 10s timeout
            });
            console.log(`[AI] AI service response: ${response.status}`);
            aiResult = response.data;
        } catch (error) {
            if (error.response) {
                console.error(`[AI] Connection error: API returned status ${error.response.status}`);
                console.error(`[AI] Response status: ${error.response.status}`);
                console.error(`[AI] Response body:`, error.response.data);
                
                // If the AI service returned a 400 (e.g. image quality issue), forward it to the frontend
                if (error.response.status === 400 && error.response.data && error.response.data.message) {
                    return res.status(400).json({ success: false, message: error.response.data.message });
                }
            } else if (error.request) {
                console.error(`[AI] Connection error: No response received`);
                console.error(`[AI] Real error:`, error.message);
            } else {
                console.error(`[AI] Connection error:`, error.message);
            }
            
            return res.status(503).json({ success: false, message: 'AI Service unavailable. Please try again later.' });
        }

        // Save to Database
        let scanData = {
            userId: req.user._id,
            image: imagePath,
            isFood: aiResult.isFood
        };

        if (aiResult.isFood === false) {
            const data = aiResult.data || {};
            scanData.status = data.status || 'INVALID_IMAGE';
            scanData.message = data.message || 'Food Not Detected';
            scanData.score = null;
            scanData.hygieneStatus = 'NOT_APPLICABLE';
            scanData.cookingStatus = 'NOT_APPLICABLE';
            scanData.detectedFood = null;
            scanData.confidence = 0;
        } else {
            const data = aiResult.data || {};
            scanData.status = data.status || 'Analyzed';
            scanData.detectedFood = data.foodName || 'Unknown';
            scanData.confidence = data.foodConfidence || 0.0;
            
            // New Tomato Fields
            scanData.qualityScore = data.qualityScore || 0;
            scanData.defectScore = data.defectScore || 0;
            scanData.qualityLevel = data.qualityLevel || 'UNKNOWN';
            scanData.reason = data.reason || '';
            scanData.visualAssessmentStatus = data.visualAssessmentStatus || 'INSUFFICIENT EVIDENCE';
            scanData.microbialSafetyRisk = data.microbialSafetyRisk || 'Unknown / Cannot Determine';
            scanData.hygieneConfidence = data.hygieneConfidence || 0.0;
            scanData.visibleIssues = data.visibleIssues || [];
            scanData.howToEat = data.howToEat || [];
            
            scanData.limitations = data.limitations || "This AI performs visual food-quality analysis. It cannot directly detect bacteria, viruses, toxins, pesticides, or other microscopic/chemical contaminants. Visual appearance does not guarantee microbiological safety.";
        }

        const scan = await Scan.create(scanData);

        res.status(201).json({
            success: true,
            data: scan
        });
    } catch (error) {
        console.error(error);
        next(error);
    }
};

exports.getScans = async (req, res, next) => {
    try {
        const scans = await Scan.find({ userId: req.user._id }).sort({ createdAt: -1 });
        res.json({ success: true, data: scans });
    } catch (error) {
        next(error);
    }
};

exports.getScanById = async (req, res, next) => {
    try {
        const scan = await Scan.findOne({ _id: req.params.id, userId: req.user._id });
        if (!scan) {
            return res.status(404).json({ success: false, message: 'Scan not found' });
        }
        res.json({ success: true, data: scan });
    } catch (error) {
        next(error);
    }
};

exports.deleteScan = async (req, res, next) => {
    try {
        const scan = await Scan.findOne({ _id: req.params.id, userId: req.user._id });
        if (!scan) {
            return res.status(404).json({ success: false, message: 'Scan not found' });
        }
        await Scan.deleteOne({ _id: req.params.id, userId: req.user._id });
        res.json({ success: true, message: 'Scan removed' });
    } catch (error) {
        next(error);
    }
};

exports.submitCustomerAssessment = async (req, res, next) => {
    try {
        const { quality, taste, comment } = req.body;
        const scanId = req.params.id;

        const scan = await Scan.findOne({ _id: scanId, userId: req.user._id });
        if (!scan) {
            return res.status(404).json({ success: false, message: 'Scan not found' });
        }

        // Map textual quality to score (out of 100)
        const qualityMap = {
            'Excellent': 100,
            'Good': 80,
            'Average': 60,
            'Poor': 40,
            'Very Poor': 20
        };
        const customerScore = qualityMap[quality] || 60; // Default 60

        scan.customerAssessment = { quality, taste, comment };

        // Final Score Formula: (Visual Quality × 0.40) + ((100 - Visible Defect Score) × 0.30) + (Customer Score × 0.30)
        // Note: We use 100 - defectScore because defectScore is a penalty value (lower is better, higher is worse).
        const aiVisualScore = scan.qualityScore || 0;
        const defectScoreValue = scan.defectScore || 0;
        const invertedDefectScore = 100 - defectScoreValue;
        
        const finalQualityScore = (aiVisualScore * 0.40) + (invertedDefectScore * 0.30) + (customerScore * 0.30);
        
        scan.finalQualityScore = finalQualityScore;

        // Disagreement Logic
        const diff = Math.abs(aiVisualScore - customerScore);
        let explanation = '';
        if (diff > 20) {
            if (aiVisualScore > customerScore) {
                explanation = "Customer and visual assessments differ significantly. The tomato appears visually healthy, but the customer reported poor quality. Visual analysis cannot evaluate taste, smell, internal texture, or other non-visible factors.";
            } else {
                explanation = "Customer and visual assessments differ significantly. The AI detected visual defects, but the customer reported good quality.";
            }
        } else {
            explanation = "Customer and visual assessments are generally in agreement.";
        }
        
        scan.assessmentDifference = explanation;

        await scan.save();

        res.status(200).json({
            success: true,
            data: scan
        });

    } catch (error) {
        console.error(error);
        next(error);
    }
};
