export function getErrorMessage(error, fallback) {
  const data = error.response?.data;

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (data && typeof data === "object") {
    const messages = Object.values(data)
      .flatMap((value) => (Array.isArray(value) ? value : [value]))
      .filter((value) => typeof value === "string");

    if (messages.length > 0) {
      return messages.join(" ");
    }
  }

  return error.response
    ? fallback
    : "Unable to reach the server. Please try again.";
}
