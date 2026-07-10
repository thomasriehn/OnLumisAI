import { forward } from "@/lib/upstream";

export async function POST(request: Request) {
  return forward(request, "/v1/feedback");
}
