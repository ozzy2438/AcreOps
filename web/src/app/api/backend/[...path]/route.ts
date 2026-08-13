import { NextRequest, NextResponse } from "next/server";
import { demoPdf, handleDemo } from "@/lib/demo";

const API = process.env.ACREOPS_API_URL;

async function proxy(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const joinedPath = path.join("/");
  const requestBody = req.method === "GET" || req.method === "HEAD" ? undefined : await req.text();

  if (API) {
    try {
      const headers = new Headers();
      const contentType = req.headers.get("content-type");
      if (contentType) headers.set("content-type", contentType);
      const upstream = await fetch(`${API}/${joinedPath}${req.nextUrl.search}`, {
        method: req.method,
        headers,
        body: requestBody,
        cache: "no-store",
      });
      return new NextResponse(await upstream.text(), {
        status: upstream.status,
        headers: {
          "content-type": upstream.headers.get("content-type") ?? "application/json",
          "x-acreops-runtime": "backend",
        },
      });
    } catch {
      // A preview must remain fully explorable if the optional Python service is unavailable.
    }
  }

  if (req.method === "GET" && joinedPath.startsWith("artifacts/")) {
    return new NextResponse(demoPdf(joinedPath), {
      headers: {
        "content-type": "application/pdf",
        "content-disposition": `inline; filename="${joinedPath.split("/").at(-1)}"`,
        "x-acreops-runtime": "interactive-demo",
      },
    });
  }

  const body = requestBody ? (JSON.parse(requestBody) as Record<string, unknown>) : {};
  const result = handleDemo(joinedPath, req.method, body);
  if (result === null) {
    return NextResponse.json({ detail: "Demo route not found" }, { status: 404 });
  }
  return NextResponse.json(result, {
    headers: { "x-acreops-runtime": "interactive-demo" },
  });
}

export const GET = proxy;
export const POST = proxy;
