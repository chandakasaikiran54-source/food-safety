const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Provide correct relative path to .env
dotenv.config({ path: path.join(__dirname, '../.env') });

const VerifiedOfficer = require('../models/VerifiedOfficer');

const seedOfficers = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI);
        
        await VerifiedOfficer.deleteMany();
        
        const officers = [
            {
                officerId: 'FDA-HYD-001',
                name: 'Anjali Sharma',
                designation: 'Senior Food Safety Officer',
                state: 'Telangana',
                district: 'Hyderabad',
                verificationStatus: 'VERIFIED'
            },
            {
                officerId: 'FDA-MUM-042',
                name: 'Ravi Kumar',
                designation: 'Food Inspector',
                state: 'Maharashtra',
                district: 'Mumbai',
                verificationStatus: 'VERIFIED'
            },
            {
                officerId: 'FDA-DEL-019',
                name: 'Suresh Singh',
                designation: 'Chief Food Safety Officer',
                state: 'Delhi',
                district: 'New Delhi',
                verificationStatus: 'INACTIVE'
            }
        ];

        await VerifiedOfficer.insertMany(officers);
        console.log('Officer data successfully synchronized with mock official source.');
        process.exit();
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
};

seedOfficers();
