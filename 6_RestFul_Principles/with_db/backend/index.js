const mongoose = require('mongoose');
const path = require('path');
const ExpressServer = require('./expressServer');
const config = require('./config');

mongoose.connect(config.MONGO_URI)
    .then(() => console.log("MongoDB connected"))
    .catch(err => console.error(err));

const server = new ExpressServer(5000, path.join(__dirname, 'api/openapi.yaml'));
server.launch();
