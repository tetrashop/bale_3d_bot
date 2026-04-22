export const config = {
  api: {
    bodyParser: {
      sizeLimit: '10mb', // یا مقدار دلخواه بزرگ‌تر
    },
  },
};

export default function handler(req, res) {
  if (req.method === 'POST') {
    // منطق تبدیل یا پردازش داده‌ها
    res.status(200).json({ message: 'Conversion successful' });
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}
