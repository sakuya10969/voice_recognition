import { Box } from "@mui/material";

import Header from "./components/Header";
import Main from "./components/Main";
import Footer from "./components/Footer";

function App() {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        alignItems: "center",
        width: "100vw",
        height: "100vh",
        overflow: "hidden"
      }}
    >
      <Header />
      <Main />
      <Footer />
    </Box>
  );
}

export default App;
