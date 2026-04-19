export default function handler(req, res) {
  if (req.method === 'POST') {
    // دریافت داده از بدنه درخواست
    const body = req.body;

    // عملیات مورد نظر (مثلاً پاسخ دادن ساده)
    res.status(200).json({ message: "Webhook received", data: body });
  } else if (req.method === 'GET') {
    // پاسخ ساده برای تست دسترسی به API
    res.status(200).send("API is alive");
  } else {
    // سایر متدها مجاز نیستند
    res.status(405).json({ error: "Method not allowed" });
  }
}
