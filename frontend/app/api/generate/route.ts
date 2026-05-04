import { NextRequest, NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { createJob } from "@/lib/job-store";
import { runHFJob } from "@/lib/providers/huggingface";
import { submitRunPodJob } from "@/lib/providers/runpod";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const imageFile = formData.get("image") as File | null;
    const prompt = (formData.get("prompt") as string | null)?.trim();

    if (!imageFile || !prompt) {
      return NextResponse.json(
        { error: "image and prompt are required" },
        { status: 400 }
      );
    }

    const arrayBuffer = await imageFile.arrayBuffer();
    const base64 = Buffer.from(arrayBuffer).toString("base64");
    const imageBase64 = `data:${imageFile.type || "image/jpeg"};base64,${base64}`;

    const provider =
      (process.env.PROVIDER as "huggingface" | "runpod") ?? "huggingface";
    const jobId = randomUUID();

    console.log("[debug] provider:", provider, "endpoint:", process.env.RUNPOD_ENDPOINT_ID);
    if (provider === "runpod") {
      const runpodJobId = await submitRunPodJob(imageBase64, prompt);
      createJob(jobId, "runpod", runpodJobId);
    } else {
      createJob(jobId, "huggingface");
      runHFJob(jobId, imageBase64, prompt);
    }

    return NextResponse.json({ jobId });
  } catch (err) {
    console.error("[/api/generate]", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to submit job" },
      { status: 500 }
    );
  }
}
