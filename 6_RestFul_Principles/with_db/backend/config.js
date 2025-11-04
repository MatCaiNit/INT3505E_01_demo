const path = require('path');

const config = {
  ROOT_DIR: __dirname,
  URL_PORT: 5000,
  URL_PATH: 'http://localhost',
  BASE_VERSION: '',
  CONTROLLER_DIRECTORY: path.join(__dirname, 'controllers'),
  PROJECT_DIR: __dirname,
  FILE_UPLOAD_PATH: './uploads',
  MONGO_URI: 'mongodb://localhost:27017/bookstore',
  JWT_SECRET: 'mysecretkey',
  JWT_EXPIRES_IN: '1h'

};
config.OPENAPI_YAML = path.join(config.ROOT_DIR, 'api', 'openapi.yaml');
config.FULL_PATH = `${config.URL_PATH}:${config.URL_PORT}/${config.BASE_VERSION}`;
config.FILE_UPLOAD_PATH = path.join(config.PROJECT_DIR, 'uploaded_files');

module.exports = config;
