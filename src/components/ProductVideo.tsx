"use client";
import { useRef, useState } from "react";
export function ProductVideo() {
  const ref = useRef<HTMLVideoElement>(null);
  const [started, setStarted] = useState(false);
  return (
    <div className="product-video">
      <video
        ref={ref}
        controls={started}
        playsInline
        preload="none"
        poster="/media/service-cover.png"
        aria-label="Erklärvideo: OnLumisAI im Serviceeinsatz"
        onPlay={() => setStarted(true)}
      >
        <source src="/media/service-erklaervideo.mp4" type="video/mp4" />
        Ihr Browser unterstützt die Videowiedergabe nicht.
      </video>
      {!started && (
        <button
          className="video-start"
          onClick={() => {
            setStarted(true);
            ref.current?.play().catch(() => setStarted(false));
          }}
          aria-label="Service-Erklärvideo abspielen"
        >
          <span className="video-play">▶</span>
          <span>
            OnLumis im Serviceeinsatz<small>Film starten · Ton an</small>
          </span>
          <b>4:28</b>
        </button>
      )}
    </div>
  );
}
