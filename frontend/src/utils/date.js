export function formatDate(date) {
  return new Date(date).toLocaleString("sr-Latn-RS", {
    timeZone: "Europe/Belgrade",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  });
}

export const examStatusColors = {
  Upcoming: "primary",
  "In progress": "warning",
  Finished: "success",
  Unavailable: "secondary",
};

export function getExamStatus(start, end, now) {
  if (!start || !end) {
    return "Unavailable";
  }

  const startTime = new Date(start).getTime();
  const endTime = new Date(end).getTime();

  if (isNaN(startTime) || isNaN(endTime)) {
    return "Unavailable";
  }
  if (endTime < startTime) {
    return "Unavailable";
  }
  if (now < startTime) {
    return "Upcoming";
  }
  if (now < endTime) {
    return "In progress";
  }
  return "Finished";
}
