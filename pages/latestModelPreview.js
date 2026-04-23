import { useEffect, useState } from "react";
import ModelPreview from "../components/ModelPreview";

export default function LatestModelPreview() {
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/latestReadyModel")
      .then((res) => {
        if (!res.ok) throw new Error("مدل آماده نیست");
        return res.json();
      })
      .then((data) => {
        setModelUrl(data.modelUrl);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>در حال بارگذاری مدل...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return <ModelPreview modelUrl={modelUrl} />;
}
