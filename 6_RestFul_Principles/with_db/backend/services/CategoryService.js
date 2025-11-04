/* eslint-disable no-unused-vars */
const Service = require('./Service');

/**
* Lấy danh sách danh mục sản phẩm
*
* returns List
* */
const categoriesGET = () => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
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
  categoriesGET,
};
