import { motion, AnimatePresence } from "framer-motion";
import { ThoughtBubble } from "./ThoughtBubble";

interface ThoughtStreamProps {
  thoughts: string[];
  color: "validator" | "strategist" | "writer" | "visual" | "optimizer";
  maxVisible?: number;
}

export function ThoughtStream({
  thoughts,
  color,
  maxVisible = 5,
}: ThoughtStreamProps) {
  const visibleThoughts = thoughts.slice(-maxVisible);

  return (
    <div className="space-y-2 max-h-[200px] overflow-y-auto scrollbar-thin">
      <AnimatePresence mode="popLayout">
        {visibleThoughts.map((thought, index) => (
          <motion.div
            key={`${thought}-${index}`}
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ThoughtBubble
              thought={thought}
              color={color}
              isLatest={index === visibleThoughts.length - 1}
              showTyping={index === visibleThoughts.length - 1}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}