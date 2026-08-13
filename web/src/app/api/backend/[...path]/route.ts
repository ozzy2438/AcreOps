import { NextRequest, NextResponse } from "next/server";
import { demoPdf, handleDemo } from "@/lib/demo";

const API = process.env.ACREOPS_API_URL;

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

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
      // Hosted interview demos must remain fully explorable if FastAPI is absent.
    }
  }

  if (req.method === "GET" && joinedPath.startsWith("artifacts/")) {
    const filename = joinedPath.split("/").at(-1) ?? "acreops-demo.pdf";
    return new NextResponse(Buffer.from(demoPdf(joinedPath)), {
      headers: {
        "content-type": "application/pdf",
        "content-disposition": `inline; filename="${filename}"`,
        "cache-control": "no-store",
        "x-acreops-runtime": "interactive-demo",
      },
    });
  }

  let body: Record<string, unknown> = {};
  if (requestBody) {
    try {
      body = JSON.parse(requestBody) as Record<string, unknown>;
    } catch {
      return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
    }
  }

  const result = handleDemo(joinedPath, req.method, body);
  if (result === null) {
    return NextResponse.json({ detail: "Demo route not found" }, { status: 404 });
  }
  return NextResponse.json(result, {
    headers: {
      "x-acreops-runtime": "interactive-demo",
      "cache-control": "no-store",
    },
  });
}

export const GET = proxy;
export const POST = proxy;
