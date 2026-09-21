import http from "k6/http";
import { browser } from "k6/browser";
import { check } from "k6";
import { Counter, Rate } from "k6/metrics";

const workload = __ENV.LOAD_TEST_WORKLOAD || "frontend";
const baseUrl = (
  __ENV.LOAD_TEST_BASE_URL || "https://student-service.internal"
).replace(/\/$/, "");
const email = __ENV.LOAD_TEST_EMAIL;
const password = __ENV.LOAD_TEST_PASSWORD;
const duration = __ENV.LOAD_TEST_DURATION || "3m";
const readVus = Number(__ENV.LOAD_TEST_VUS || 10);
const browserChecks = new Rate("browser_checks");
const browserPageLoads = new Counter("browser_page_loads");

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

export const options = workload === "frontend" ? {
  scenarios: {
    requests: {
      executor: "constant-vus",
      vus: readVus,
      duration,
      exec: "testFrontend",
    },
    browser: {
      executor: "constant-vus",
      vus: 1,
      duration,
      exec: "renderFrontend",
      options: { browser: { type: "chromium" } },
    },
  },
  thresholds: {
    ...thresholds,
    browser_checks: ["rate==1"],
    browser_web_vital_lcp: ["p(95)<2500"],
    browser_web_vital_cls: ["p(95)<0.1"],
  },
} : {
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
  const health = http.get(`${baseUrl}/healthz`, {
    tags: { name: "frontend health" },
  });

  check(page, { "frontend loaded": (response) => response.status === 200 });
  check(health, {
    "frontend is healthy": (response) => response.status === 200,
  });
}

export async function renderFrontend() {
  const page = await browser.newPage();

  try {
    const response = await page.goto(`${baseUrl}/`, { waitUntil: "load" });
    const heading = await page.locator("h1").textContent();
    const loaded = response?.status() === 200;
    const rendered = heading?.trim() === "Log in";

    check(loaded, { "page loaded": (result) => result });
    check(rendered, { "login rendered": (result) => result });
    browserChecks.add(loaded);
    browserChecks.add(rendered);
    if (loaded && rendered) {
      browserPageLoads.add(1);
    }
  } finally {
    await page.close();
  }
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
  if (workload === "backend") {
    testBackend();
  } else {
    testWrite();
  }
}
