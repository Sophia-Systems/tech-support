import type { ConfidenceTier } from "@/types";

export interface TestQuestion {
  id: string;
  question: string;
  expectedTier: ConfidenceTier;
  /** Tiers that also count as a pass */
  acceptableTiers: ConfidenceTier[];
  category: "maintenance" | "troubleshooting" | "off-topic" | "safety";
}

export const testQuestions: TestQuestion[] = [
  // ANSWER — from dryer-maintenance.md
  {
    id: "lint-trap",
    question: "How often should I clean the lint trap?",
    expectedTier: "ANSWER",
    acceptableTiers: ["ANSWER", "CAVEAT"],
    category: "maintenance",
  },
  {
    id: "preventive-schedule",
    question: "What is the preventive maintenance schedule?",
    expectedTier: "ANSWER",
    acceptableTiers: ["ANSWER", "CAVEAT"],
    category: "maintenance",
  },

  // ANSWER — from dryer-troubleshooting.md
  {
    id: "error-e01",
    question: "What does error code E01 mean?",
    expectedTier: "ANSWER",
    acceptableTiers: ["ANSWER", "CAVEAT"],
    category: "troubleshooting",
  },
  {
    id: "wont-start",
    question: "My dryer won't start, what should I check?",
    expectedTier: "ANSWER",
    acceptableTiers: ["ANSWER", "CAVEAT"],
    category: "troubleshooting",
  },
  {
    id: "slow-dry",
    question: "Why are clothes taking too long to dry?",
    expectedTier: "ANSWER",
    acceptableTiers: ["ANSWER", "CAVEAT"],
    category: "troubleshooting",
  },

  // OFF_TOPIC
  {
    id: "capital-france",
    question: "What is the capital of France?",
    expectedTier: "OFF_TOPIC",
    acceptableTiers: ["OFF_TOPIC", "DECLINE"],
    category: "off-topic",
  },
  {
    id: "write-poem",
    question: "Can you write me a poem?",
    expectedTier: "OFF_TOPIC",
    acceptableTiers: ["OFF_TOPIC", "DECLINE"],
    category: "off-topic",
  },

  // ESCALATE — safety concern
  {
    id: "sparking",
    question: "My dryer is sparking and I smell smoke",
    expectedTier: "ESCALATE",
    acceptableTiers: ["ESCALATE", "ANSWER", "CAVEAT"],
    category: "safety",
  },

  // Edge cases
  {
    id: "belt-replacement",
    question: "How do I replace the drum belt?",
    expectedTier: "CAVEAT",
    acceptableTiers: ["ANSWER", "CAVEAT", "DECLINE"],
    category: "maintenance",
  },
  {
    id: "model-comparison",
    question: "Which Dexter dryer model is best for a laundromat?",
    expectedTier: "DECLINE",
    acceptableTiers: ["DECLINE", "CAVEAT", "OFF_TOPIC"],
    category: "off-topic",
  },
];
