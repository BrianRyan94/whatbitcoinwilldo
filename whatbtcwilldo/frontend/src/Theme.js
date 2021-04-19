import { createMuiTheme } from "@material-ui/core/styles";

const font = "'Quicksand', sans-serif";

const Theme = createMuiTheme({
  typography: {
    fontFamily: font,
    button: {
      textTransform: "none",
      color: "white",
    },
  },
  palette: {
    primary: {
      main: "#2789f5",
    },

    secondary: {
      main: "rgb(255, 255, 255)",
    },
  },
});

export default Theme;
