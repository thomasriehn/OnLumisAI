import { forward } from "@/lib/upstream";

// Spracheingabe: Audio-Blob → /v1/transcriptions (lokales Whisper).
export async function POST(request: Request) {
  return forward(request, "/v1/transcriptions");
}
