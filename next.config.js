module.exports = {
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
        ignored: ['/data/**', '/data/data/**', '/**'],
      };
    }
    return config;
  },
};
