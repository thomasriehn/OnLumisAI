import { serveDemoFile } from "@/lib/demo-files";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(
  request: Request,
  { params }: { params: Promise<{ path: string[] }> },
) {
  return serveDemoFile(request, (await params).path);
}
export const HEAD = GET;
