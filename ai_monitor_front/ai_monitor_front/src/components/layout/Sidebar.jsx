import { Box, IconButton } from "@mui/material";
import CodeIcon from "@mui/icons-material/Code";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import SmartToyIcon from "@mui/icons-material/SmartToy";

export default function Sidebar() {
  return (
    <Box
      sx={{
        width: 55,
        background: "#0f172a",
        borderRight: "1px solid #1e293b",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        pt: 2,
        gap: 2
      }}
    >
      <IconButton color="primary">
        <CodeIcon />
      </IconButton>

      <IconButton>
        <AnalyticsIcon />
      </IconButton>

      <IconButton>
        <SmartToyIcon />
      </IconButton>
    </Box>
  );
}