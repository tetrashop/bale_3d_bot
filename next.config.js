module.exports = {
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        ignored: [
          '**/node_modules',
          '/data/**',
          '/data/data/**',
          '/**'  // به شدت پوشه ریشه رو نادیده می‌گیره تا خطاها کمتر شود
        ]
      };
    }
    return config;
  },
};
