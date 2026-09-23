import http from "k6/http";
import { check } from "k6";

const workload = __ENV.LOAD_TEST_WORKLOAD || "frontend";
const baseUrl = (
  __ENV.LOAD_TEST_BASE_URL || "https://student-service.internal"
).replace(/\/$/, "");
const email = __ENV.LOAD_TEST_EMAIL;
const password = __ENV.LOAD_TEST_PASSWORD;
const duration = __ENV.LOAD_TEST_DURATION || "3m";
const readVus = Number(__ENV.LOAD_TEST_VUS || 10);

if (!["frontend", "backend", "write"].includes(workload)) {
  throw new Error(`Unknown workload: ${workload}`);
}

if (workload !== "frontend" && (!email || !password)) {
  throw new Error("LOAD_TEST_EMAIL and LOAD_TEST_PASSWORD are required");
}

if (workload === "write" && __ENV.LOAD_TEST_ALLOW_WRITES !== "true") {
  throw new Error("Set LOAD_TEST_ALLOW_WRITES=true to run the write workload");
}

if (!Number.isInteger(readVus) || readVus < 1) {
  throw new Error("LOAD_TEST_VUS must be a positive integer");
}

const thresholds = {
  http_req_failed: ["rate<0.01"],
  http_req_duration: ["p(95)<750"],
};

export const options = {
  vus: workload === "write" ? 1 : readVus,
  duration,
  thresholds,
};

let accessToken;

function authenticate() {
  if (accessToken) {
    return;
  }

  const response = http.post(
    `${baseUrl}/api/auth/token/`,
    JSON.stringify({ email, password }),
    {
      headers: { "Content-Type": "application/json" },
      tags: { name: "login" },
    },
  );

  const authenticated = check(response, {
    "login succeeded": (result) => result.status === 200,
  });

  if (authenticated) {
    accessToken = response.json("access");
  }
}

function authenticatedGet(path, name) {
  const response = http.get(`${baseUrl}${path}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    tags: { name },
  });

  check(response, {
    [`${name} succeeded`]: (result) => result.status === 200,
  });

  return response;
}

export function testFrontend() {
  const page = http.get(`${baseUrl}/`, { tags: { name: "frontend" } });

  check(page, { "frontend loaded": (response) => response.status === 200 });
}

function testBackend() {
  authenticate();
  if (!accessToken) {
    return;
  }

  authenticatedGet("/api/accounts/me/", "current user");
  authenticatedGet("/api/academics/enrollments/", "enrollments");
  authenticatedGet("/api/exams/available/", "available exams");
  authenticatedGet("/api/finance/wallet/", "wallet");
}

function testWrite() {
  authenticate();
  if (!accessToken) {
    return;
  }

  const availableResponse = authenticatedGet(
    "/api/exams/available/",
    "available exams",
  );
  const exams =
    availableResponse.status === 200 ? availableResponse.json() : [];
  const hasExam = check(exams, {
    "an exam is available": (items) => items.length > 0,
  });

  if (!hasExam) {
    return;
  }

  const requestOptions = {
    headers: { Authorization: `Bearer ${accessToken}` },
  };
  const registration = http.post(
    `${baseUrl}/api/exams/${exams[0].id}/register/`,
    null,
    { ...requestOptions, tags: { name: "register exam" } },
  );
  const registered = check(registration, {
    "exam registration succeeded": (response) => response.status === 201,
  });

  if (!registered) {
    return;
  }

  const cancellation = http.post(
    `${baseUrl}/api/exams/registrations/${registration.json("id")}/cancel/`,
    null,
    { ...requestOptions, tags: { name: "cancel registration" } },
  );
  check(cancellation, {
    "exam cancellation succeeded": (response) => response.status === 200,
  });
}

export default function () {
  if (workload === "frontend") {
    testFrontend();
  } else if (workload === "backend") {
    testBackend();
  } else {
    testWrite();
  }
}
