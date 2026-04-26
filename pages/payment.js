// pages/payment.js
'use client';

import { useState } from 'react';

export default function PaymentPage() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handlePayment = async () => {
    setLoading(true);
    setStatus(null);
    setErrorMsg('');

    // مقادیر تست – در واقعیت، اینها را از login یا state دریافت کنید
    const chatId = 'test_user_123';
    const amount = 5000;  // عدد، نه رشته

    try {
      const response = await fetch('/api/payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chatId, amount }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'خطا در درخواست پرداخت');
      }

      setStatus('success');
    } catch (err) {
      console.error('Client error:', err);
      setErrorMsg(err.message);
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '2rem' }}>
      <h1>💳 پرداخت</h1>
      <button
        onClick={handlePayment}
        disabled={loading}
        style={{
          padding: '12px 24px',
          fontSize: '18px',
          backgroundColor: loading ? '#ccc' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'در حال اتصال...' : 'پرداخت ۵,۰۰۰ تومان'}
      </button>
      {status === 'success' && (
        <p style={{ color: 'green', marginTop: '20px' }}>
          ✅ پرداخت موفقیت‌آمیز بود. مدل سه‌بعدی شما آماده است.
        </p>
      )}
      {status === 'error' && (
        <p style={{ color: 'red', marginTop: '20px' }}>
          ❌ خطا: {errorMsg || 'لطفاً دوباره تلاش کنید.'}
        </p>
      )}
    </div>
  );
}
