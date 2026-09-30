import { serveDemoFile } from "@/lib/demo-files";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request: Request) {
  return serveDemoFile(request, ["VIDEOS.html"]);
}
export const HEAD = GET;
