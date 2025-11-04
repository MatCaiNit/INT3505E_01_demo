const Product = require('../models/Product');

module.exports = {
  productsGET: async (req, res) => {
    let { category, type, limit } = req.query;
    let filter = {};
    if (category) filter.category = category;
    if (type) filter.type = type;

    limit = parseInt(limit) || 20;
    const products = await Product.find(filter).limit(limit);
    res.json(products);
  },

  productsPOST: async (req, res) => {
    const product = new Product(req.body);
    await product.save();
    res.status(201).json(product);
  },

  productsIdGET: async (req, res) => {
    const product = await Product.findById(req.params.id);
    if (!product) return res.status(404).json({ message: "Không tìm thấy sản phẩm" });
    res.json(product);
  },

  productsIdPUT: async (req, res) => {
    const product = await Product.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!product) return res.status(404).json({ message: "Không tìm thấy sản phẩm" });
    res.json(product);
  },

  productsIdDELETE: async (req, res) => {
    const product = await Product.findByIdAndDelete(req.params.id);
    if (!product) return res.status(404).json({ message: "Không tìm thấy sản phẩm" });
    res.status(204).send();
  }
};
