const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

const Reviews = require('./review');
const Dealerships = require('./dealership');

const reviewsData = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'data/reviews.json'), 'utf8')
);
const dealersData = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'data/dealerships.json'), 'utf8')
);

app.get('/', (req, res) => res.send('Welcome to the Mongoose API'));

app.get('/fetchReviews', async (req, res) => {
  try {
    res.json(await Reviews.find());
  } catch (e) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    res.json(await Reviews.find({ dealership: Number(req.params.id) }));
  } catch (e) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

app.get('/fetchDealers', async (req, res) => {
  try {
    res.json(await Dealerships.find());
  } catch (e) {
    res.status(500).json({ error: 'Error fetching dealerships' });
  }
});

app.get('/fetchDealers/:state', async (req, res) => {
  try {
    res.json(await Dealerships.find({
      state: { $regex: `^${req.params.state}$`, $options: 'i' }
    }));
  } catch (e) {
    res.status(500).json({ error: 'Error filtering dealerships' });
  }
});

app.get('/fetchDealer/:id', async (req, res) => {
  try {
    res.json(await Dealerships.find({ id: Number(req.params.id) }));
  } catch (e) {
    res.status(500).json({ error: 'Error fetching dealership' });
  }
});

app.post('/insert_review', async (req, res) => {
  try {
    const data = req.body;
    const latest = await Reviews.findOne().sort({ id: -1 });

    const review = new Reviews({
      id: latest ? latest.id + 1 : 1,
      name: data.name,
      dealership: Number(data.dealership),
      review: data.review,
      purchase: Boolean(data.purchase),
      purchase_date: data.purchase_date,
      car_make: data.car_make,
      car_model: data.car_model,
      car_year: Number(data.car_year)
    });

    res.json(await review.save());
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

async function start() {
  await mongoose.connect(
    process.env.MONGO_URL || 'mongodb://mongo_db:27017/dealershipsDB'
  );

  if (await Reviews.countDocuments() === 0) {
    await Reviews.insertMany(reviewsData.reviews);
  }
  if (await Dealerships.countDocuments() === 0) {
    await Dealerships.insertMany(dealersData.dealerships);
  }

  app.listen(port, '0.0.0.0', () => {
    console.log(`Express API running on port ${port}`);
  });
}

start().catch(e => {
  console.error('Express startup failed:', e);
  process.exit(1);
});
