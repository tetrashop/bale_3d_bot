/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  // اجازه می‌دهد توابع Python در مسیر /api/process کار کنند
  experimental: {
    serverComponentsExternalPackages: ['numpy', 'PIL'],
  },
};
