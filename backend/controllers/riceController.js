const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');

/**
 * Controller for Rice Intelligence Analysis
 * Connects Express backend with Python AI microservice.
 */
exports.analyzeRice = async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: 'Please upload an image of rice (raw grains or cooked Biryani rice).'
            });
        }

        const absolutePath = path.join(__dirname, '..', req.file.path);
        const aiServiceBase = process.env.AI_SERVICE_URL
            ? process.env.AI_SERVICE_URL.replace(/\/analyze$/, '')
            : 'http://127.0.0.1:8000';

        const targetUrl = `${aiServiceBase}/api/rice-intelligence/analyze`;
        console.log(`[Rice Intelligence Controller] Calling AI service at: ${targetUrl}`);

        const formData = new FormData();
        formData.append('image', fs.createReadStream(absolutePath));
        formData.append('filename', req.file.filename);

        if (req.body && req.body.weight) {
            formData.append('weight', req.body.weight);
        }

        try {
            const response = await axios.post(targetUrl, formData, {
                headers: formData.getHeaders(),
                timeout: 20000 // 20s timeout for CV processing
            });

            return res.status(200).json({
                success: true,
                uploadedImage: `/uploads/${req.file.filename}`,
                ...response.data
            });
        } catch (error) {
            if (error.response) {
                console.error(`[Rice Controller] AI Service returned error: ${error.response.status}`, error.response.data);
                return res.status(error.response.status).json({
                    success: false,
                    uploadedImage: `/uploads/${req.file.filename}`,
                    ...error.response.data
                });
            } else {
                console.error(`[Rice Controller] AI Service unreachable:`, error.message);
                return res.status(503).json({
                    success: false,
                    message: 'Rice Intelligence AI Service is currently unavailable. Please verify ai-service is running on port 8000.'
                });
            }
        }
    } catch (err) {
        console.error(`[Rice Controller] Server error:`, err);
        return res.status(500).json({
            success: false,
            message: 'Internal server error during rice intelligence analysis.'
        });
    }
};
