"use client";

import { useRef, useState } from "react";

type MicState = "idle" | "recording" | "busy" | "unavailable";

/** Spracheingabe: MediaRecorder → lokales Whisper (/bff/transcribe).
 *  Bewusst ohne Browser-Speech-API – die würde Audio in fremde Clouds senden. */
export function MicButton({ onText }: { onText: (text: string) => void }) {
  const [state, setState] = useState<MicState>("idle");
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);

  async function toggle() {
    if (state === "recording") {
      recorder.current?.stop();
      return;
    }
    if (state === "busy") return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      chunks.current = [];
      mediaRecorder.ondataavailable = (event) => chunks.current.push(event.data);
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        setState("busy");
        try {
          const blob = new Blob(chunks.current, {
            type: mediaRecorder.mimeType || "audio/webm",
          });
          const form = new FormData();
          form.append("file", blob, "aufnahme.webm");
          const response = await fetch("/bff/transcribe", { method: "POST", body: form });
          if (response.status === 501) {
            setState("unavailable");
            return;
          }
          if (response.ok) {
            const data = await response.json();
            if (data.text) onText(String(data.text).trim());
          }
          setState("idle");
        } catch {
          setState("idle");
        }
      };
      mediaRecorder.start();
      recorder.current = mediaRecorder;
      setState("recording");
    } catch {
      setState("unavailable"); // kein Mikrofon / keine Berechtigung
    }
  }

  const titles: Record<MicState, string> = {
    idle: "Spracheingabe starten",
    recording: "Aufnahme beenden",
    busy: "Transkription läuft …",
    unavailable: "Spracheingabe nicht verfügbar (Whisper nicht konfiguriert oder kein Mikrofon)",
  };

  return (
    <button
      type="button"
      className={`mic ${state}`}
      onClick={toggle}
      disabled={state === "busy" || state === "unavailable"}
      title={titles[state]}
      aria-label={titles[state]}
    >
      {state === "recording" ? "⏹" : state === "busy" ? "…" : "🎤"}
    </button>
  );
}
