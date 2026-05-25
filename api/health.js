export default function handler(req, res) {
    res.status(200).json({ message: 'API is healthy! Your bot webhook is working.' });
}
