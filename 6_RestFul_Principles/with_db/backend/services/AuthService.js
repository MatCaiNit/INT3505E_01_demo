/* eslint-disable no-unused-vars */
const Service = require('./Service');

/**
* Đăng nhập vào hệ thống
*
* loginRequest LoginRequest 
* returns AuthResponse
* */
const login = ({ loginRequest }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        loginRequest,
      }));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);
/**
* Đăng ký tài khoản người dùng mới
*
* registerRequest RegisterRequest 
* returns AuthResponse
* */
const register = ({ registerRequest }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        registerRequest,
      }));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);

module.exports = {
  login,
  register,
};
