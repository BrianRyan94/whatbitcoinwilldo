import { makeStyles } from "@material-ui/core/styles";

const SharedStyles = makeStyles({
  primary_background: {
    background: "#2789f5",
    padding: "15px",
  },

  secondary_background: {
    backgroundColor: "rgba(20, 20, 20, 0.05)",
  },

  header_text: {
    color: "white",
  },

  cardHeaders: {
    color: "#2789f5",
    fontWeight: "bolder",
  },

  default_chart_dim: {
    width: "100%",
    height: "300px",
  },

  flexRow: {
    display: "flex",
    flexDirection: "row",
  },

  spaceBetween: {
    justifyContent: "space-between",
  },

  RowWrap: {
    flexFlow: "row wrap",
  },
});

export default SharedStyles;
