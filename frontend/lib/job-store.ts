// Module-level Map — persists between requests in the same Node.js process
// Fine for a local internal tool; replace with Redis/DB for multi-process deployments.

export type JobStatus = "pending" | "complete" | "error";

export type Job = {
  provider: "huggingface" | "runpod";
  runpodJobId?: string;
  status: JobStatus;
  result?: string;
  error?: string;
};

const jobs = new Map<string, Job>();

export function createJob(
  jobId: string,
  provider: "huggingface" | "runpod",
  runpodJobId?: string
): void {
  jobs.set(jobId, { provider, runpodJobId, status: "pending" });
}

export function updateJob(jobId: string, update: Partial<Job>): void {
  const existing = jobs.get(jobId);
  if (existing) jobs.set(jobId, { ...existing, ...update });
}

export function getJob(jobId: string): Job | undefined {
  return jobs.get(jobId);
}
