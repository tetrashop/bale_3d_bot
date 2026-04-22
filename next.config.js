const path = require('path');

const nextConfig = {
  webpack: (config) => {
    config.watchOptions = {
      ignored: ['**/node_modules', '/data/**', '/**'],
    };
    return config;
  },
  outputFileTracingRoot: path.join(__dirname),
};

module.exports = nextConfig;
