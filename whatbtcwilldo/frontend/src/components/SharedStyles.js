import { makeStyles } from "@material-ui/core/styles";

const PrimaryColor = "#2789f5";
const SharedStyles = makeStyles({
  header_text: {
    color: "white",
  },

  primary_background: {
    background: "#2789f5",
    padding: "15px",
  },

  cardHeaders: {
    color: "#2789f5",
    fontWeight: "bold",
  },

  default_chart_dim: {
    width: "100%",
    height: "300px",
  },
});

export default SharedStyles;
