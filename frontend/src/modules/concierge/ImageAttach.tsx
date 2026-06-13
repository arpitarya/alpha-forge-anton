"use client";

import { useRef } from "react";
import { fileToDataUrl, MAX_IMAGES } from "./chat.images";

/**
 * Attach + preview image thumbnails for vision input. The composer owns the
 * `images` array; this renders the picker button and the removable previews.
 */
export function ImageAttach({
  images,
  onChange,
}: {
  images: string[];
  onChange: (next: string[]) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  async function add(files: FileList | null) {
    if (!files) return;
    const room = MAX_IMAGES - images.length;
    const picked = await Promise.all(Array.from(files).slice(0, room).map(fileToDataUrl));
    const next = [...images, ...picked.filter((u): u is string => u !== null)];
    onChange(next.slice(0, MAX_IMAGES));
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <button
        type="button"
        title="Attach image"
        aria-label="Attach image"
        disabled={images.length >= MAX_IMAGES}
        onClick={() => inputRef.current?.click()}
        style={{
          width: 30,
          height: 30,
          display: "grid",
          placeItems: "center",
          borderRadius: 7,
          border: "1px solid var(--line)",
          background: "transparent",
          color: "var(--fg-3)",
          cursor: images.length >= MAX_IMAGES ? "default" : "pointer",
          opacity: images.length >= MAX_IMAGES ? 0.4 : 1,
        }}
      >
        <svg
          width={15}
          height={15}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.7}
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <path d="m21 15-5-5L5 21" />
        </svg>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        hidden
        onChange={(e) => void add(e.target.files)}
      />
      {images.map((src, i) => (
        <span key={src.slice(-32)} style={{ position: "relative", display: "inline-block" }}>
          {/* biome-ignore lint/performance/noImgElement: local data URL preview, not remote */}
          <img
            src={src}
            alt={`attachment ${i + 1}`}
            style={{ width: 30, height: 30, borderRadius: 6, objectFit: "cover", display: "block" }}
          />
          <button
            type="button"
            aria-label="Remove image"
            onClick={() => onChange(images.filter((_, j) => j !== i))}
            style={{
              position: "absolute",
              top: -6,
              right: -6,
              width: 16,
              height: 16,
              borderRadius: "50%",
              border: "none",
              background: "var(--red)",
              color: "#fff",
              fontSize: 10,
              lineHeight: "16px",
              cursor: "pointer",
              padding: 0,
            }}
          >
            ✕
          </button>
        </span>
      ))}
    </div>
  );
}
