/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    WALLET_ID: process.env.WALLET_ID,
    PROCESSOR_API_URL: process.env.PROCESSOR_API_URL,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
  },
  allowedDevOrigins: ['21.246.178.87', 'localhost', '127.0.0.1'],
};

module.exports = nextConfig;
