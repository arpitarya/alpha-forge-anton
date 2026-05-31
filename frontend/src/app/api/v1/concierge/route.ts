import { type NextRequest, NextResponse } from "next/server";

const BACKEND = `http://localhost:${process.env.BACKEND_PORT ?? "8000"}`;

export async function POST(req: NextRequest) {
  const auth = req.headers.get("authorization") ?? "";
  const body = await req.text();

  const upstream = await fetch(`${BACKEND}/api/v1/concierge/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(auth ? { Authorization: auth } : {}),
    },
    body,
  });

  if (!upstream.ok || !upstream.body) {
    const err = await upstream.text();
    return new NextResponse(err, { status: upstream.status });
  }

  // Stream the SSE response back verbatim
  return new NextResponse(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}
