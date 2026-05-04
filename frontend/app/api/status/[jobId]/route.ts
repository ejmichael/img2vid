import { NextRequest, NextResponse } from "next/server";
import { getJob, updateJob } from "@/lib/job-store";
import { getRunPodStatus } from "@/lib/providers/runpod";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;
  const job = getJob(jobId);

  if (!job) {
    return NextResponse.json({ error: "Job not found" }, { status: 404 });
  }

  // For RunPod, actively poll the RunPod API while the job is pending
  if (job.provider === "runpod" && job.status === "pending" && job.runpodJobId) {
    try {
      const runpodStatus = await getRunPodStatus(job.runpodJobId);
      if (runpodStatus.status !== "pending") {
        updateJob(jobId, runpodStatus);
        return NextResponse.json(runpodStatus);
      }
    } catch {
      // Swallow transient errors — client will retry
    }
  }

  return NextResponse.json({
    status: job.status,
    result: job.result,
    error: job.error,
  });
}
