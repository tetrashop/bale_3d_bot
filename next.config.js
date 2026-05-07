/** @type {import('next').NextConfig} */
const nextConfig = {
  allowedDevOrigins: ['192.168.1.101', 'localhost', '127.0.0.1'],
  webpack: (config) => {
    config.watchOptions = { poll: 2000, ignored: /node_modules/ };
    return config;
  },
};
module.exports = nextConfig;
