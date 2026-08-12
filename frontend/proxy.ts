import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  SESSION_COOKIE_NAME,
  verifySessionToken,
} from "@/lib/auth";

export function proxy(
  request: NextRequest,
) {
  const token =
    request.cookies.get(
      SESSION_COOKIE_NAME,
    )?.value;

  if (
    !verifySessionToken(token)
  ) {
    const loginUrl =
      new URL(
        "/login",
        request.url,
      );

    return NextResponse.redirect(
      loginUrl,
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/chat/:path*",
    "/documents/:path*",
  ],
};