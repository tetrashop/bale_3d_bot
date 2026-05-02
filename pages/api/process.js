export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const processorUrl = process.env.PROCESSOR_API_URL;
  if (!processorUrl) {
    return res.status(500).json({ error: 'Processor API URL not configured' });
  }

  try {
    const response = await fetch(`${processorUrl}/process`, {
      method: 'POST',
      body: req.body, // فرم‌دیتا ارسال شده از فرانت را مستقیماً فوروارد می‌کنیم
      headers: {
        ...req.headers,
        host: null, // حذف host اصلی برای جلوگیری از تداخل
      },
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({ error: text });
    }

    // خروجی باینری OBJ را به فرانت برمی‌گردانیم
    const blob = await response.arrayBuffer();
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', 'attachment; filename=model.obj');
    res.send(Buffer.from(blob));
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
}
