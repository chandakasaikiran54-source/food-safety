const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const dotenv = require("dotenv");
const path = require("path");
const { errorHandler } = require('./middleware/errorMiddleware');
const VerifiedOfficer = require('./models/VerifiedOfficer');

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Routes
app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/scans', require('./routes/scanRoutes'));
app.use('/api/restaurants', require('./routes/restaurantRoutes'));
app.use('/api/officers', require('./routes/officerRoutes'));
app.use('/api/complaints', require('./routes/complaintRoutes'));
app.use('/api/raw-food', require('./routes/rawFoodRoutes'));
app.use('/api/tomato', require('./routes/tomatoRoutes'));
app.use('/api/microbial', require('./routes/microbialRoutes'));

// Error Handler
app.use(errorHandler);

// Health Endpoint
app.get('/api/health', (req, res) => {
  const isDbConnected = mongoose.connection.readyState === 1;
  res.status(isDbConnected ? 200 : 503).json({
    success: isDbConnected,
    server: 'running',
    database: isDbConnected ? 'connected' : 'disconnected'
  });
});

// Root Route
app.get('/', (req, res) => {
  res.json({ success: true, message: "FoodSafe AI Backend is running" });
});

// Database Connection and Server Startup
const PORT = process.env.PORT || 5000;

mongoose
  .connect(process.env.MONGO_URI)
  .then(async () => {
    console.log("MongoDB connected successfully");
    try {
      const officerExists = await VerifiedOfficer.findOne({ officerId: 'FDA-HYD-001' });
      if (!officerExists) {
        await VerifiedOfficer.create({
          officerId: 'FDA-HYD-001',
          name: 'System Admin',
          state: 'Telangana',
          district: 'Hyderabad',
          verificationStatus: 'VERIFIED'
        });
        console.log('Mock Officer seeded: FDA-HYD-001');
      }
    } catch (e) {
      console.error("Error seeding mock officer:", e);
    }

    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  })
  .catch((err) => {
    console.error("MongoDB connection failed:", err.message);
    process.exit(1);
  });