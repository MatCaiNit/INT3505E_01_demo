const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    email: String,
    fullName: String
}, { timestamps: true });

// Hash password trước khi save
userSchema.pre('save', function(next) {
    if (!this.isModified('password')) return next();
    this.password = bcrypt.hashSync(this.password, 8);
    next();
});

// Method compare password
userSchema.methods.comparePassword = function(password) {
    return bcrypt.compareSync(password, this.password);
};

module.exports = mongoose.model('User', userSchema);
