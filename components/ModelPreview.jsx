import React from "react";

export default function ModelPreview({ previewImageUrl, modelUrl }) {
  return (
    <div style={{ marginTop: 20, textAlign: "center" }}>
      <h3>پیش‌نمایش مدل (عکس):</h3>
      <img
        src={previewImageUrl}
        alt="پیش‌نمایش مدل"
        style={{ maxWidth: "80vw", maxHeight: 300, border: "1px solid #ccc" }}
      />
      <div>
        <a
          href={modelUrl}
          download
          style={{
            display: "inline-block",
            marginTop: 15,
            padding: "10px 20px",
            backgroundColor: "#4CAF50",
            color: "white",
            textDecoration: "none",
            borderRadius: 4,
          }}
        >
          دانلود مدل سه‌بعدی
        </a>
      </div>
    </div>
  );
}
