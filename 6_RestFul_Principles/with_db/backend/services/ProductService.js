/* eslint-disable no-unused-vars */
const Service = require('./Service');

/**
* Lấy danh sách tất cả sản phẩm
*
* category String Lọc sản phẩm theo danh mục (optional)
* type String Lọc theo loại sản phẩm (optional)
* limit Integer  (optional)
* returns List
* */
const productsGET = ({ category, type, limit }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        category,
        type,
        limit,
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
* (Admin) Xóa sản phẩm
*
* id String 
* no response value expected for this operation
* */
const productsIdDELETE = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        id,
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
* Lấy chi tiết một sản phẩm
*
* id String 
* returns Product
* */
const productsIdGET = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        id,
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
* (Admin) Cập nhật thông tin sản phẩm
*
* id String 
* productUpdate ProductUpdate 
* returns Product
* */
const productsIdPUT = ({ id, productUpdate }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        id,
        productUpdate,
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
* (Admin) Tạo mới sản phẩm
*
* productCreate ProductCreate 
* returns Product
* */
const productsPOST = ({ productCreate }) => new Promise(
  async (resolve, reject) => {
    try {
      resolve(Service.successResponse({
        productCreate,
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
  productsGET,
  productsIdDELETE,
  productsIdGET,
  productsIdPUT,
  productsPOST,
};
