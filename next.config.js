module.exports = {
  webpack: (config, options) => {
    if (options.dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
};
