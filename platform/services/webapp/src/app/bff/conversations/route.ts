import { forward } from "@/lib/upstream";

export async function GET(request: Request) {
  return forward(request, "/v1/conversations");
}
