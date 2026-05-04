import { Client } from "@gradio/client";
import { updateJob } from "@/lib/job-store";

const HF_SPACE = process.env.HF_SPACE || "Lightricks/LTX-Video";
const HF_TOKEN = process.env.HF_TOKEN;
const HF_ENDPOINT = process.env.HF_ENDPOINT || "/image-to-video";

export function runHFJob(
  jobId: string,
  imageBase64: string,
  prompt: string
): void {
  // Fire-and-forget — status is tracked via updateJob
  void (async () => {
    try {
      const client = await Client.connect(HF_SPACE, {
        hf_token: HF_TOKEN as `hf_${string}` | undefined,
      });

      const b64Data = imageBase64.replace(/^data:[^;]+;base64,/, "");
      const mimeType = imageBase64.match(/^data:([^;]+);/)?.[1] ?? "image/jpeg";
      const imageBlob = new Blob([Buffer.from(b64Data, "base64")], {
        type: mimeType,
      });

      const result = await client.predict(HF_ENDPOINT, {
        image: imageBlob,
        prompt,
        negative_prompt:
          "worst quality, inconsistent motion, blurry, jittery, distorted",
        num_inference_steps: 30,
        guidance_scale: 3,
        seed: -1,
      });

      const rawData = (result.data as unknown[])?.[0];
      const videoData = rawData as { url?: string } | string | null;
      const videoUrl =
        typeof videoData === "string" ? videoData : videoData?.url;

      if (!videoUrl) throw new Error("No video URL in response");

      updateJob(jobId, { status: "complete", result: videoUrl });
    } catch (err) {
      updateJob(jobId, {
        status: "error",
        error: err instanceof Error ? err.message : "Unknown error",
      });
    }
  })();
}
