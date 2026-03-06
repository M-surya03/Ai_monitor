import { motion } from "framer-motion";

export default function SlideAnimation({ children }) {
  return (
    <motion.div initial={{ x: 50 }} animate={{ x: 0 }}>
      {children}
    </motion.div>
  );
}