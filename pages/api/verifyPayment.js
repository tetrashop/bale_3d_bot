export default async function handler(req, res) {
  const { status, transactionId } = req.query;
  if (status === 'success') {
    // در اینجا می‌توانید تراکنش را ذخیره کنید و یک توکن دانلود صادر کنید
    const token = Buffer.from(`${transactionId}:${Date.now()}`).toString('base64');
    // به صفحه دانلود هدایت کنید
    res.redirect(`/download?token=${token}`);
  } else {
    res.status(400).send('پرداخت ناموفق یا انصراف');
  }
}
