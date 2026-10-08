const axios = require('axios');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');

/**
 * Controller for Biryani Regional Classification & Quality Analysis
 * Bridges Express backend to Python Computer Vision service (Phase 25)
 */
exports.classifyBiryani = async (req, res, next) => {
    try {
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: 'Please upload an image of Biryani for regional classification.'
            });
        }

        const absolutePath = path.join(__dirname, '..', req.file.path);
        const aiServiceBase = process.env.AI_SERVICE_URL
            ? process.env.AI_SERVICE_URL.replace(/\/analyze$/, '')
            : 'http://127.0.0.1:8000';

        const targetUrl = `${aiServiceBase}/api/biryani/classify`;
        console.log(`[Biryani Controller] Calling AI classification service at: ${targetUrl}`);

        const formData = new FormData();
        formData.append('image', fs.createReadStream(absolutePath));
        formData.append('filename', req.file.filename);

        try {
            const response = await axios.post(targetUrl, formData, {
                headers: formData.getHeaders(),
                timeout: 30000 // 30s timeout for CV processing & Grad-CAM
            });

            return res.status(200).json({
                success: true,
                uploadedImage: `/uploads/${req.file.filename}`,
                ...response.data
            });
        } catch (error) {
            if (error.response) {
                console.error(`[Biryani Controller] AI Service returned error: ${error.response.status}`, error.response.data);
                return res.status(error.response.status).json({
                    success: false,
                    uploadedImage: `/uploads/${req.file.filename}`,
                    ...error.response.data
                });
            } else {
                console.error(`[Biryani Controller] AI Service unreachable:`, error.message);
                return res.status(503).json({
                    success: false,
                    message: 'Biryani Classification AI Service is currently unavailable. Please verify ai-service is running on port 8000.'
                });
            }
        }
    } catch (err) {
        console.error('[Biryani Controller] Internal Error:', err);
        return res.status(500).json({
            success: false,
            message: 'Internal server error while processing Biryani classification.',
            error: err.message
        });
    }
};
