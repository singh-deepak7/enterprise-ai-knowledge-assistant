import { NextResponse } from "next/server";

import {
  createSessionToken,
  SESSION_COOKIE_NAME,
  SESSION_MAX_AGE_SECONDS,
} from "@/lib/auth";

interface LoginRequest {
  username?: string;
  password?: string;
}

export async function POST(request: Request) {
  let body: LoginRequest;

  try {
    body = (await request.json()) as LoginRequest;
  } catch {
    return NextResponse.json(
      {
        message: "Invalid login request.",
      },
      {
        status: 400,
      },
    );
  }

  const expectedUsername = process.env.APP_USERNAME;

  const expectedPassword = process.env.APP_PASSWORD;

  if (!expectedUsername || !expectedPassword) {
    return NextResponse.json(
      {
        message: "Authentication is not configured.",
      },
      {
        status: 500,
      },
    );
  }

  if (
    body.username !== expectedUsername ||
    body.password !== expectedPassword
  ) {
    return NextResponse.json(
      {
        message: "Invalid username or password.",
      },
      {
        status: 401,
      },
    );
  }

  const token = createSessionToken(expectedUsername);

  const response = NextResponse.json({
    success: true,
  });

  response.cookies.set(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS,
  });

  return response;
}
