const RUNPOD_API_KEY = process.env.RUNPOD_API_KEY!;
const RUNPOD_ENDPOINT_ID = process.env.RUNPOD_ENDPOINT_ID!;
const BASE_URL = `https://api.runpod.io/v2/${RUNPOD_ENDPOINT_ID}`;

export async function submitRunPodJob(
  imageBase64: string,
  prompt: string
): Promise<string> {
  const res = await fetch(`${BASE_URL}/run`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${RUNPOD_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      input: {
        image: imageBase64,
        prompt,
        negative_prompt:
          "worst quality, inconsistent motion, blurry, jittery, distorted",
        num_frames: 25,
        num_inference_steps: 8,
        guidance_scale: 1.0,
        seed: -1,
      },
    }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`RunPod submit failed (${res.status}): ${body}`);
  }

  const data = (await res.json()) as { id: string };
  return data.id;
}

type RunPodStatusResponse = {
  status: "IN_QUEUE" | "IN_PROGRESS" | "COMPLETED" | "FAILED" | "CANCELLED";
  output?: { video_url?: string; video?: string; video_b64?: string };
  error?: string;
};

export async function getRunPodStatus(runpodJobId: string): Promise<{
  status: "pending" | "complete" | "error";
  result?: string;
  error?: string;
}> {
  const res = await fetch(`${BASE_URL}/status/${runpodJobId}`, {
    headers: { Authorization: `Bearer ${RUNPOD_API_KEY}` },
  });

  if (!res.ok) {
    throw new Error(`RunPod status failed (${res.status})`);
  }

  const data = (await res.json()) as RunPodStatusResponse;

  if (data.status === "COMPLETED") {
    // Prefer a direct URL; fall back to base64 data URL
    const videoUrl =
      data.output?.video_url ??
      data.output?.video ??
      (data.output?.video_b64
        ? `data:video/mp4;base64,${data.output.video_b64}`
        : undefined);

    if (!videoUrl) throw new Error("RunPod job completed but no video in output");
    return { status: "complete", result: videoUrl };
  }

  if (data.status === "FAILED" || data.status === "CANCELLED") {
    return { status: "error", error: data.error ?? `Job ${data.status}` };
  }

  return { status: "pending" };
}
