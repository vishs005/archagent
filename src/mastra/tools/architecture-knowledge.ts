import "dotenv/config";
import { createTool } from "@mastra/core/tools";
import { z } from "zod";
import { embed } from "ai";
import { ModelRouterEmbeddingModel } from "@mastra/core/llm";
import { Pinecone } from "@pinecone-database/pinecone";

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY!,
});

const index = pinecone.index("archrag");

export const architectureKnowledgeTool = createTool({
  id: "search_architecture_knowledge",

  description:
    "Search the internal architecture knowledge base for relevant architecture patterns, engineering practices, and documented architecture guidance.",

  inputSchema: z.object({
    query: z
      .string()
      .describe("The architecture question or topic to search for."),
  }),

  execute: async ({ query }) => {
   
  // existing code below...
    // Convert the agent's search query into an embedding
    const { embedding } = await embed({
      model: new ModelRouterEmbeddingModel(
        "openai/text-embedding-3-small"
      ),
      value: query,
    });

    // Search our existing ArchRAG Pinecone index
    const results = await index.query({
      vector: embedding,
      topK: 5,
      includeMetadata: true,
    });

    // Return retrieved knowledge to the agent
    const matches = results.matches.map((match) => ({
      score: match.score,
      text: match.metadata?.text,
      title: match.metadata?.title,
      sourceUrl: match.metadata?.sourceUrl,
    }));

    return {
      query,
      matches,
    };
  },
});