
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import Header from "./components/Header";
import Main from "./components/Main";
import Footer from "./components/Footer";

function App() {
  return (
    <>
      <CssBaseline />
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          alignItems: "center",
          width: "100vw",
          height: "100vh",
          overflowX: "hidden",
        }}
      >
        <Header />
        <Main />
        <Footer />
      </Box>
    </>
  );
}

export default App;
