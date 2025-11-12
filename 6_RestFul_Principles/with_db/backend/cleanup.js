// cleanup.js
const mongoose = require("mongoose");
const User = require("./models/User");
const Product = require("./models/Product");

async function cleanup() {
  await mongoose.connect("mongodb://localhost:27017/bookstore");
  console.log("Connected to DB");

  await User.deleteMany({ username: /^user_/ });
  await Product.deleteMany({ name: /^TestProduct_/ });

  console.log("Cleanup done");
  await mongoose.disconnect();
}

cleanup().catch(console.error);
