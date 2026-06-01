import { type NextRequest, NextResponse } from "next/server";

const BACKEND = `http://localhost:${process.env.BACKEND_PORT ?? "8000"}`;

export async function POST(req: NextRequest) {
  const auth = req.headers.get("authorization") ?? "";
  const contentType = req.headers.get("content-type") ?? "";

  const upstream = await fetch(`${BACKEND}/api/v1/concierge/stt`, {
    method: "POST",
    headers: {
      ...(contentType ? { "Content-Type": contentType } : {}),
      ...(auth ? { Authorization: auth } : {}),
    },
    // Stream the multipart body straight through
    body: req.body,
    // @ts-expect-error — duplex is required by undici for streaming bodies
    duplex: "half",
  });

  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: { "Content-Type": "application/json" },
  });
}
