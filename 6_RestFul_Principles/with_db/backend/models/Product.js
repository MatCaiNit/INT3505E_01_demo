const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
    name: { type: String, required: true },
    category: String,
    type: { type: String, enum: ['book', 'toy', 'office_supply'], required: true },
    price: { type: Number, required: true },
    stock: { type: Number, default: 0 },
    discount: { type: Number, default: 0 },
    description: String,
    images: [String],
    author: String,
    publisher: String,
    language: String,
    brand: String,
    material: String,
    size: String,
    weight: String,
    age_range: String
}, { timestamps: true });

module.exports = mongoose.model('Product', productSchema);
