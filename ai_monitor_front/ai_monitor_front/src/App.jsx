import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";
import ProgressPage from "./pages/ProgressPage";
import "./theme/globals.css";

import HomePage from "./pages/HomePage";
import AnalyzerPage from "./pages/AnalyzerPage";

export default function App() {
  return (
    <Router>
      <Routes>

        <Route path="/" element={<HomePage />} />

        <Route path="/analyzer" element={<AnalyzerPage />} />
<Route path="/progress" element={<ProgressPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />

      </Routes>
    </Router>
  );
}