import { createReadStream } from "node:fs";
import { realpath, stat } from "node:fs/promises";
import path from "node:path";
import { Readable } from "node:stream";
import { hasDemoSession, PRIVATE_HEADERS } from "./demo-auth";
const types: Record<string, string> = {
  ".mp4": "video/mp4",
  ".pdf": "application/pdf",
  ".png": "image/png",
  ".webp": "image/webp",
  ".html": "text/html; charset=utf-8",
  ".md": "text/plain; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
};
export function parseRange(
  range: string | null,
  size: number,
): { start: number; end: number } | null | false {
  if (!range) return null;
  const match = /^bytes=(\d*)-(\d*)$/.exec(range);
  if (!match || (!match[1] && !match[2])) return false;
  const start = match[1]
    ? Number(match[1])
    : Math.max(0, size - Number(match[2]));
  const end =
    match[1] && match[2] ? Math.min(size - 1, Number(match[2])) : size - 1;
  if (
    !Number.isSafeInteger(start) ||
    !Number.isSafeInteger(end) ||
    start < 0 ||
    start >= size ||
    end < start ||
    (!match[1] && Number(match[2]) === 0)
  )
    return false;
  return { start, end };
}
export async function serveDemoFile(request: Request, parts: string[]) {
  if (!(await hasDemoSession()))
    return new Response("Bitte zuerst im Demo-Studio anmelden.", {
      status: 401,
      headers: PRIVATE_HEADERS,
    });
  if (
    parts.length > 3 ||
    parts.some(
      (p) =>
        p.startsWith(".") ||
        p.includes("/") ||
        p.includes("\\") ||
        p.includes("\0"),
    )
  )
    return new Response("Nicht gefunden", {
      status: 404,
      headers: PRIVATE_HEADERS,
    });
  const relative = parts.join("/");
  const permitted =
    /^V[123]_\d{2}_[\w-]+\.mp4$/.test(relative) ||
    /^assets\/V[123]_\d{2}_titel\.png$/.test(relative) ||
    /^playbooks\/OnLumis_Playbook_V[123]_[\w-]+\.pdf$/.test(relative) ||
    [
      "VIDEOS.html",
      "ABLAUF.md",
      "BEOBACHTUNGEN.md",
      "PRUEFPROTOKOLL.md",
      "LIESMICH.md",
      "SHA256SUMS.txt",
    ].includes(relative);
  if (!permitted)
    return new Response("Nicht gefunden", {
      status: 404,
      headers: PRIVATE_HEADERS,
    });
  try {
    const root = await realpath(
      process.env.DEMO_ASSET_DIR || path.join(process.cwd(), "private/demo"),
    );
    const file = await realpath(path.join(root, ...parts));
    if (!file.startsWith(root + path.sep))
      return new Response("Nicht gefunden", {
        status: 404,
        headers: PRIVATE_HEADERS,
      });
    const info = await stat(file);
    if (!info.isFile())
      return new Response("Nicht gefunden", {
        status: 404,
        headers: PRIVATE_HEADERS,
      });
    const range = parseRange(request.headers.get("range"), info.size);
    if (range === false)
      return new Response(null, {
        status: 416,
        headers: {
          ...PRIVATE_HEADERS,
          "Content-Range": `bytes */${info.size}`,
        },
      });
    const start = range?.start ?? 0;
    const end = range?.end ?? info.size - 1;
    const headers: Record<string, string> = {
      ...PRIVATE_HEADERS,
      "Content-Type": types[path.extname(file)] ?? "application/octet-stream",
      "Accept-Ranges": "bytes",
      "Content-Length": String(end - start + 1),
    };
    if (range) headers["Content-Range"] = `bytes ${start}-${end}/${info.size}`;
    if (path.extname(file) === ".html")
      headers["Content-Security-Policy"] =
        "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; media-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'none'";
    if (request.method === "HEAD")
      return new Response(null, { status: range ? 206 : 200, headers });
    const stream = createReadStream(file, { start, end });
    return new Response(Readable.toWeb(stream) as ReadableStream, {
      status: range ? 206 : 200,
      headers,
    });
  } catch {
    return new Response("Nicht gefunden", {
      status: 404,
      headers: PRIVATE_HEADERS,
    });
  }
}
