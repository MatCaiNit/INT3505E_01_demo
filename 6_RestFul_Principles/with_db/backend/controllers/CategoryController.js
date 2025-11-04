const Category = require('../models/Category');

module.exports = {
  categoriesGET: async (req, res) => {
    const categories = await Category.find();
    res.json(categories);
  }
};
