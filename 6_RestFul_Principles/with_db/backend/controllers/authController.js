const jwt = require('jsonwebtoken');
const config = require('../config');
const User = require('../models/User');

module.exports = {
  register: async (req, res) => {
    try {
      const { username, password, email, fullName } = req.body;
      if (!username || !password) return res.status(400).json({ message: "Username và password bắt buộc" });

      const exist = await User.findOne({ username });
      if (exist) return res.status(409).json({ message: "Tài khoản đã tồn tại" });

      const user = new User({ username, password, email, fullName });
      await user.save();

      const token = jwt.sign({ id: user._id, username: user.username }, config.JWT_SECRET, { expiresIn: config.JWT_EXPIRES_IN });
      res.status(201).json({ message: "Đăng ký thành công", token });
    } catch (err) {
      res.status(500).json({ message: err.message });
    }
  },

  login: async (req, res) => {
    try {
      const { username, password } = req.body;
      const user = await User.findOne({ username });
      if (!user || !user.comparePassword(password)) return res.status(401).json({ message: "Sai username hoặc password" });

      const token = jwt.sign({ id: user._id, username: user.username }, config.JWT_SECRET, { expiresIn: config.JWT_EXPIRES_IN });
      res.json({ message: "Đăng nhập thành công", token });
    } catch (err) {
      res.status(500).json({ message: err.message });
    }
  }
};
