const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');

/**
 * Core Biryani food identification service controller.
 */
exports.identifyBiryaniFood = async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: 'Please upload an image for food identification.' });
        }

        const absolutePath = path.join(__dirname, '..', req.file.path);
        const aiServiceBase = process.env.AI_SERVICE_URL
            ? process.env.AI_SERVICE_URL.replace(/\/analyze$/, '')
            : 'http://127.0.0.1:8000';
            
        const targetUrl = `${aiServiceBase}/api/food-identification/biryani`;

        console.log(`[Food ID Controller] Calling Biryani AI service at: ${targetUrl}`);

        const formData = new FormData();
        formData.append('image', fs.createReadStream(absolutePath));
        formData.append('filename', req.file.filename);

        try {
            const response = await axios.post(targetUrl, formData, {
                headers: formData.getHeaders(),
                timeout: 15000
            });

            return res.status(200).json({
                success: true,
                uploadedImage: `/uploads/${req.file.filename}`,
                ...response.data
            });
        } catch (error) {
            if (error.response) {
                console.error(`[Food ID] AI Service responded with error: ${error.response.status}`, error.response.data);
                return res.status(error.response.status).json(error.response.data);
            } else {
                console.error(`[Food ID] AI Service unreachable:`, error.message);
                return res.status(503).json({
                    success: false,
                    message: 'Food Identification AI Service is currently unavailable. Please verify ai-service is running on port 8000.'
                });
            }
        }
    } catch (err) {
        console.error(`[Food ID] Controller error:`, err);
        return res.status(500).json({ success: false, message: 'Internal server error during food identification.' });
    }
};
