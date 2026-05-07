export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { token, quality, chatId } = req.body;
  if (!token) return res.status(400).json({ error: 'No token' });
  // شبیه‌سازی موفقیت بدون نیاز به توکن بله
  return res.status(200).json({ success: true, transactionId: 'sim_' + Date.now() });
}
