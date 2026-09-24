import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

export const saveAdrTool = createTool({
  id: "save_adr",

  description:
    "Save an approved Architecture Decision Record (ADR) as a Markdown file.",
  requireApproval: true,


  inputSchema: z.object({
    title: z
      .string()
      .describe("Title of the architecture decision."),

    content: z
      .string()
      .describe("The complete ADR content in Markdown format."),
  }),

  execute: async ({ title, content }) => {
    const directory = "adrs";

    await mkdir(directory, { recursive: true });

    const safeFileName = title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

    const filePath = join(directory, `${safeFileName}.md`);

    await writeFile(filePath, content, "utf-8");

    return {
      success: true,
      filePath,
      message: `ADR saved successfully to ${filePath}`,
    };
  },
});