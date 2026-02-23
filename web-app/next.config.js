/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  serverRuntimeConfig: {
    // Will only be available on the server side
    maxApiTimeout: 60000,
  },
  publicRuntimeConfig: {
    // Will be available on both server and client
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
  },
};

module.exports = nextConfig;
